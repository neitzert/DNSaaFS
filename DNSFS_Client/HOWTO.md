mkdir -p ~/dnsfs
python3 dnsfs_mount.py --domain test.lan --mountpoint ~/dnsfs --server 127.0.0.1 --port 1053
dnssec-keygen -a HMAC-SHA256 -b 256 -n HOST dnsfs-key
