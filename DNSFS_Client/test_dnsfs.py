import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
from mountDNSFS import DNSBlockDevice, BLOCK_SIZE
import base64
import json
import hashlib
import hmac

TEST_DOMAIN = "test.lan"
TEST_PASSPHRASE = "password123"
TEST_BLOCK_DATA = b"hello world" + b"\x00" * (BLOCK_SIZE - 11)

class TestDNSBlockDevice(unittest.TestCase):

    def setUp(self):
        self.device = DNSBlockDevice(TEST_DOMAIN, TEST_PASSPHRASE, server="127.0.0.1")

    def test_key_derivation_consistency(self):
        other = DNSBlockDevice(TEST_DOMAIN, TEST_PASSPHRASE, server="127.0.0.1")
        self.assertEqual(self.device.enc_key, other.enc_key)
        self.assertEqual(self.device.hmac_key, other.hmac_key)

    def test_encrypt_decrypt_roundtrip(self):
        encrypted = self.device._encrypt(TEST_BLOCK_DATA)
        decrypted = self.device._decrypt(encrypted)
        self.assertEqual(decrypted, TEST_BLOCK_DATA)

    @patch("dns.query.tcp")
    @patch("dns.update.Update")
    def test_write_txt_invokes_dns_update(self, mock_update, mock_tcp):
        mock_tcp.return_value = None
        self.device._write_txt("test", "foobar")
        self.assertTrue(mock_tcp.called)

    @patch("dns.resolver.Resolver.resolve")
    def test_read_txt_returns_combined_chunks(self, mock_resolve):
        mock_answer = [MagicMock(), MagicMock()]
        mock_answer[0].__str__.return_value = '"foo"'
        mock_answer[1].__str__.return_value = '"bar"'
        mock_resolve.return_value = mock_answer
        result = self.device._read_txt("test")
        self.assertEqual(result, "foobar")

    def test_label_for_index(self):
        label = self.device._label_for_index(0)
        self.assertTrue(label.startswith("blk-"))
        self.assertEqual(len(label), 20)

    def test_metadata_checksum(self):
        meta = {'/': {'st_mode': 16877, 'st_ctime': time(), 'st_mtime': time(), 'st_atime': time(), 'st_nlink': 2}}
        meta['version'] = 1
        meta['updated'] = time()
        meta['checksum'] = hmac.new(
            self.device.hmac_key,
            json.dumps(meta, sort_keys=True).encode(),
            hashlib.sha256
        ).hexdigest()
        calculated_checksum = hmac.new(
            self.device.hmac_key,
            json.dumps({k: v for k, v in meta.items() if k != 'checksum'}, sort_keys=True).encode(),
            hashlib.sha256
        ).hexdigest()
        self.assertEqual(meta['checksum'], calculated_checksum)

if __name__ == '__main__':
    unittest.main()
