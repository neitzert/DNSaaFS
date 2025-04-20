## 📁 DNSFS Client

The DNSFS client lets you **mount a filesystem where files are stored as encrypted TXT records in a DNS zone**. It is stateless, misuses DNS on purpose, and laughs in the face of conventional infrastructure.

You are in the client/ directory. Welcome to the edge.

---

### 🚀 What’s in here

```bash
.
├── mountDNSFS.py      # The main tool. Mounts your DNS zone as a filesystem using FUSE
├── test_dnsfs.py      # Tests for the block device, encryption, and metadata
├── requirements.txt   # Pip dependencies
├── HOWTO.md           # Minimal setup example for mounting DNSFS
├── utils/             # Helper scripts and tools (not shown here yet)
```

---

### 🧪 Dependencies

Install them like this:

```bash
pip install -r requirements.txt
```

Requires Python 3.12+. Also FUSE support (WinFsp on Windows).

---

### ⚙️ Usage

Mount a DNSFS volume like this:

```bash
python3 mountDNSFS.py \
  --domain test.lan \
  --mountpoint ~/dnsfs \
  --server 127.0.0.1 \
  --port 1053
```

If you don’t pass `--passphrase`, it’ll ask you.

Make sure your DNS server is up and allowing dynamic updates on that zone.

More detailed usage: [`HOWTO.md`](HOWTO.md)

---

### 🔐 How It Works

- Uses `argon2` to derive encryption + HMAC keys from your passphrase
- Encrypts each file block with `AES-GCM`
- Base64 encodes it and stores as TXT records in your DNS zone
- Metadata is triple-redundant and includes SHA-256 + HMAC checks
- All writes are async, all reads skip cache

---

### 🧪 Testing

```bash
python3 test_dnsfs.py
```

Includes tests for:
- Key derivation
- Encrypt/decrypt
- DNS TXT interaction
- Metadata checksums

---

🚫 NO WARRANTIES, NO GUARANTEES, NO REGRETS
Look, this is a tool that:

Stores encrypted file blocks in DNS zone records

Mounts them as a filesystem

Uses a protocol from 1983 as a distributed block store

And you thought it was going to be stable?

This is not safe. This is not supported. This is not sane.

We offer:

❌ No uptime promises

❌ No data loss protection

❌ No DNSSEC hugs

❌ No warranty of fitness for anything except chaos

If it bricks your system, leaks your files, corrupts your dog, or gets you featured in a DEF CON talk — that’s on you, we don't care, we only care in shits and giggles.

It might work. It might summon Clippy. It might email your boss a hexdump of your Porn folder. We don’t know. We don’t want to know. Don’t send bug reports unless they’re funny or you've got a proposed fix.
---

### 🔥 License

This code is under the **FreeForEducationalandPersonalUse License v1.1**, aka the **Try Me and Die License**.

Do NOT try to monetize this unless you want to:

- Give up your first-born
- Appear in [`VIOLATORS.md`](../VIOLATORS.md)
- Lose access to your crypto wallet, pension, moral compass, and any nanogram of integrity you might have had...

If you're confused, read the [LICENSE.md](../LICENSE.md) and [TERMS_OF_HUMILIATION.md](../TERMS_OF_HUMILIATION.md) thoroughly.

---

### 🤝 Commercial Use?

Cool, just don't be an asshole about it and I'll probably work with you.  
Email: 📧 **ChristopherNeitzert@neitzert.com**
