import os
import sys
import errno
import stat
import base64
import hmac
import json
import hashlib
import dns.resolver
import dns.update
import dns.query
import logging
from time import time, sleep
from fuse import FUSE, FuseOSError, Operations
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from argon2.low_level import hash_secret_raw, Type
from concurrent.futures import ThreadPoolExecutor, as_completed
import tqdm
import argparse

LOG_FILE = "dnsfs.log"

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("dnsfs")

BLOCK_SIZE = 256
META_LABELS = ["meta0", "meta1", "meta2"]
DNS_WRITE_DELAY = 0.2
MAX_RETRIES = 3
RETRY_DELAY = 0.5

class DNSBlockDevice:
    def __init__(self, domain: str, passphrase: str, server: str = "127.0.0.1", port: int = 53, force_salt: bool = False):
        self.domain = domain
        self.server = server
        self.port = port
        self.force_salt = force_salt
        self.local_salt_file = f".dnsfs_salt_{domain.replace('.', '_')}.bin"
        self.executor = ThreadPoolExecutor(max_workers=10)

        self.salt = self._get_or_create_salt()
        key = hash_secret_raw(
            secret=passphrase.encode(),
            salt=self.salt,
            time_cost=4,
            memory_cost=65536,
            parallelism=2,
            hash_len=64,
            type=Type.ID
        )
        self.enc_key = key[:32]
        self.hmac_key = key[32:]
        self.counter = 0

    def _get_or_create_salt(self) -> bytes:
        label = "salt"

        if self.force_salt:
            logger.warning("\u26a0\ufe0f Forcing regeneration of salt!")
            salt = os.urandom(16)
            self._write_txt(label, base64.b64encode(salt).decode())
            with open(self.local_salt_file, 'wb') as f:
                f.write(salt)
            return salt

        if os.path.exists(self.local_salt_file):
            with open(self.local_salt_file, 'rb') as f:
                salt = f.read()
                if len(salt) == 16:
                    logger.info("Using local salt backup.")
                    return salt

        try:
            b64 = self._read_txt(label)
            salt = base64.b64decode(b64)
            if len(salt) != 16:
                raise ValueError("Bad salt length")
            logger.info("Retrieved salt from DNS TXT.")
            with open(self.local_salt_file, 'wb') as f:
                f.write(salt)
            return salt
        except Exception as e:
            logger.warning(f"Salt TXT not found or invalid: {e}")
            salt = os.urandom(16)
            logger.info("Generated new salt.")
            b64salt = base64.b64encode(salt).decode()
            self._write_txt(label, b64salt)
            with open(self.local_salt_file, 'wb') as f:
                f.write(salt)
            return salt

    def _label_for_index(self, index):
        msg = index.to_bytes(8, 'big')
        digest = hmac.new(self.hmac_key, msg, hashlib.sha256).hexdigest()
        return f"blk-{digest[:16]}"

    def _encrypt(self, plaintext):
        aesgcm = AESGCM(self.enc_key)
        nonce = os.urandom(12)
        ct = aesgcm.encrypt(nonce, plaintext, None)
        tag = hmac.new(self.hmac_key, nonce + ct, hashlib.sha256).digest()
        return base64.b64encode(nonce + ct + tag).decode()

    def _decrypt(self, b64text):
        raw = base64.b64decode(b64text)
        nonce, ct, tag = raw[:12], raw[12:-32], raw[-32:]
        expected_tag = hmac.new(self.hmac_key, nonce + ct, hashlib.sha256).digest()
        if not hmac.compare_digest(tag, expected_tag):
            raise ValueError("Invalid HMAC: possible tampering or wrong key")
        aesgcm = AESGCM(self.enc_key)
        return aesgcm.decrypt(nonce, ct, None)

    def _resolver_no_cache(self):
        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = [self.server]
        resolver.port = self.port
        resolver.cache = None
        return resolver

    def _read_txt(self, label):
        fqdn = f"{label}.{self.domain}"
        for attempt in range(MAX_RETRIES):
            try:
                resolver = self._resolver_no_cache()
                logger.debug(f"Reading TXT for {fqdn}, attempt {attempt + 1}")
                answer = resolver.resolve(fqdn, 'TXT')
                return ''.join([str(a).strip('"') for a in answer])
            except Exception as e:
                logger.warning(f"Read failed for {fqdn}: {e}")
                sleep(RETRY_DELAY)
        raise IOError(f"Failed to read TXT record for {fqdn} after {MAX_RETRIES} retries")

    def _write_txt(self, label, txt):
        max_len = 255
        chunks = [txt[i:i+max_len] for i in range(0, len(txt), max_len)]
        update = dns.update.Update(self.domain)
        for chunk in chunks:
            update.replace(label, 3600, 'TXT', chunk)
        for attempt in range(MAX_RETRIES):
            try:
                dns.query.tcp(update, self.server, port=self.port)
                sleep(DNS_WRITE_DELAY)
                return
            except Exception as e:
                logger.warning(f"Write failed for {label}, retry {attempt + 1}: {e}")
                sleep(RETRY_DELAY)
        raise IOError(f"Failed to write TXT record for {label} after {MAX_RETRIES} retries")

    def write_block(self, index, data):
        label = self._label_for_index(index)
        encrypted = self._encrypt(data)
        self.executor.submit(self._write_txt, label, encrypted)

    def read_block(self, index):
        label = self._label_for_index(index)
        try:
            b64 = self._read_txt(label)
        except Exception as e:
            logger.error(f"Failed to read block {index}: {e}")
            return b"\x00" * BLOCK_SIZE
        if not b64:
            return b"\x00" * BLOCK_SIZE
        try:
            return self._decrypt(b64)
        except Exception as e:
            logger.error(f"Decryption failed for block {index}: {e}")
            return b"\x00" * BLOCK_SIZE

    def delete_block(self, index):
        label = self._label_for_index(index)
        null_data = b"\x00" * BLOCK_SIZE
        encrypted = self._encrypt(null_data)
        self.executor.submit(self._write_txt, label, encrypted)

    def save_metadata(self, metadata: dict):
        metadata['version'] = metadata.get('version', 0) + 1
        metadata['updated'] = time()
        metadata['checksum'] = hmac.new(self.hmac_key, json.dumps(metadata, sort_keys=True).encode(), hashlib.sha256).hexdigest()
        meta_json = json.dumps(metadata).encode()
        encrypted = self._encrypt(meta_json)
        futures = [self.executor.submit(self._write_txt, label, encrypted) for label in META_LABELS]
        for f in as_completed(futures):
            f.result()

    def load_metadata(self):
        best = None
        best_time = 0
        logger.info("Loading metadata blocks:")
        for label in tqdm.tqdm(META_LABELS):
            try:
                b64 = self._read_txt(label)
                if not b64:
                    continue
                decrypted = self._decrypt(b64)
                candidate = json.loads(decrypted)
                expected_checksum = candidate.pop('checksum', None)
                real_checksum = hmac.new(self.hmac_key, json.dumps(candidate, sort_keys=True).encode(), hashlib.sha256).hexdigest()
                if expected_checksum != real_checksum:
                    logger.warning(f"Metadata checksum mismatch in {label}")
                    continue
                if 'updated' in candidate and candidate['updated'] > best_time:
                    best = candidate
                    best_time = candidate['updated']
            except Exception as e:
                logger.warning(f"Failed to load metadata from {label}: {e}")
                continue
        return best or {}

class DNSFS(Operations):
    def __init__(self, domain, passphrase, server, port, force_salt):
        logger.info("Starting DNSFS init")
        self.dev = DNSBlockDevice(domain, passphrase, server, port, force_salt)
        self.files = self.dev.load_metadata()
        logger.info(f"Metadata loaded: {self.files.keys()}")
        if '/' not in self.files:
            now = time()
            self.files['/'] = dict(st_mode=(stat.S_IFDIR | 0o755), st_ctime=now,
                                   st_mtime=now, st_atime=now, st_nlink=2)
        self.fd = 0

    def _save(self):
        self.dev.save_metadata(self.files)

    def _update_hash(self, path):
        blocks = self.files[path]['blocks']
        data = b''.join([self.dev.read_block(i) for i in tqdm.tqdm(blocks)])
        size = self.files[path]['st_size']
        h = hashlib.sha256(data[:size]).digest()
        tag = hmac.new(self.dev.hmac_key, h, hashlib.sha256).hexdigest()
        self.files[path]['hash'] = tag

    def _verify_hash(self, path):
        if 'hash' not in self.files[path]:
            return True
        blocks = self.files[path]['blocks']
        data = b''.join([self.dev.read_block(i) for i in blocks])
        size = self.files[path]['st_size']
        h = hashlib.sha256(data[:size]).digest()
        tag = hmac.new(self.dev.hmac_key, h, hashlib.sha256).hexdigest()
        return hmac.compare_digest(tag, self.files[path]['hash'])

    def getattr(self, path, fh=None):
        logger.debug(f"getattr called for {path}")
        if path not in self.files:
            raise FuseOSError(errno.ENOENT)
        return self.files[path]

    def readdir(self, path, fh):
        logger.debug(f"readdir called for {path}")
        return ['.', '..'] + [name[1:] for name in self.files if name != '/']

    def create(self, path, mode):
        now = time()
        self.files[path] = dict(st_mode=(stat.S_IFREG | mode), st_nlink=1,
                                st_size=0, st_ctime=now, st_mtime=now, st_atime=now,
                                blocks=[], hash="")
        self.fd += 1
        self._save()
        return self.fd

    def open(self, path, flags):
        self.fd += 1
        return self.fd

    def read(self, path, size, offset, fh):
        if not self._verify_hash(path):
            raise FuseOSError(errno.EIO)
        file = self.files[path]
        blocks = file['blocks']
        start = offset // BLOCK_SIZE
        end = (offset + size - 1) // BLOCK_SIZE
        data = b""
        for i in range(start, end + 1):
            if i < len(blocks):
                data += self.dev.read_block(blocks[i])
            else:
                data += b"\x00" * BLOCK_SIZE
        return data[offset % BLOCK_SIZE:offset % BLOCK_SIZE + size]

    def write(self, path, buf, offset, fh):
        file = self.files[path]
        blocks = file['blocks']
        start = offset // BLOCK_SIZE
        end = (offset + len(buf) - 1) // BLOCK_SIZE

        while end >= len(blocks):
            blocks.append(self.dev.counter)
            self.dev.counter += 1

        total_written = 0
        for i in range(start, end + 1):
            index = blocks[i]
            try:
                block = bytearray(self.dev.read_block(index))
            except Exception as e:
                logger.error(f"Failed to read block {index} during write: {e}")
                block = bytearray(BLOCK_SIZE)
            bo = i * BLOCK_SIZE
            bs = max(offset - bo, 0)
            be = min(offset + len(buf) - bo, BLOCK_SIZE)
            seg = buf[total_written:total_written + be - bs]
            block[bs:be] = seg
            try:
                self.dev.write_block(index, bytes(block))
            except Exception as e:
                logger.error(f"Failed to write block {index}: {e}")
            total_written += be - bs

        file['st_size'] = max(file['st_size'], offset + len(buf))
        file['st_mtime'] = time()
        self._update_hash(path)
        self._save()
        return len(buf)

    def unlink(self, path):
        for idx in self.files[path].get('blocks', []):
            try:
                self.dev.delete_block(idx)
            except Exception as e:
                logger.error(f"Failed to delete block {idx}: {e}")
        del self.files[path]
        self._save()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--domain', required=True)
    parser.add_argument('--mountpoint', required=True)
    parser.add_argument('--server', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=1053)
    parser.add_argument('--passphrase', default=os.getenv('DNSFS_PASSPHRASE'))
    parser.add_argument('--force-salt', action='store_true', help='Force new salt generation')
    args = parser.parse_args()

    passphrase = args.passphrase or input("\U0001f511 Enter passphrase: ")
    FUSE(DNSFS(args.domain, passphrase, args.server, args.port, args.force_salt), args.mountpoint, foreground=True)