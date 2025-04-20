import base64
import dns.resolver
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from argon2.low_level import hash_secret_raw, Type

DOMAIN = "test.lan"
SERVER = "127.0.0.1"
PORT = 1053
LABEL = "blk-test"
PASSPHRASE = "testpassword"
SALT = b"static-dnsfs-salt"

# Derive encryption key
def derive_key(passphrase: str):
    key = hash_secret_raw(
        secret=passphrase.encode(),
        salt=SALT,
        time_cost=4,
        memory_cost=65536,
        parallelism=2,
        hash_len=32,
        type=Type.ID
    )
    return key

# Decrypt a block
def decrypt_block(key, b64data):
    raw = base64.b64decode(b64data)
    nonce, ciphertext = raw[:12], raw[12:]
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None)

# Read from DNS
def read_txt(label):
    fqdn = f"{label}.{DOMAIN}"
    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = [SERVER]
    resolver.port = PORT
    answer = resolver.resolve(fqdn, 'TXT')
    return str(answer[0]).strip('"')

# Run test
key = derive_key(PASSPHRASE)
print("🔍 Reading from DNS...")
read_b64 = read_txt(LABEL)
print("📦 Fetched TXT:", read_b64)

decrypted = decrypt_block(key, read_b64)
print("✅ Decrypted Block:", decrypted.decode())
