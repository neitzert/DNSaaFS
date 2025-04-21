# 🧠 DNSaaFS  
### A DNS-backed, encrypted, chunked, stateless filesystem for maniacs and misfits.

**DNSaaFS** is a filesystem that stores encrypted file chunks as DNS zone records.  
It uses zero trusted infrastructure, leverages DNS caching infrastructure, and laughs in the face of centralized control.

---

## 📂 Project Structure

```bash
.
├── DNSFS_DNS_Docker_server/     # Docker container with authoritative DNS server + dynamic update support
├── DNSFS_Client/                # Python FUSE tool to mount, read/write, and verify DNS-backed files
├── LICENSE.md                   # Try Me and Die license
├── TERMS_OF_HUMILIATION.md      # You probably want to read this
├── VIOLATORS.md                 # Learn from the mistakes of others
```

---

## 🚧 Status

- 🧪 Proof of Concept
- 💀 Untested in production
- 🔥 Built to be weird 
- 📜 Licensed to be hostile to commercial exploitation

---

## 🕳 Why?

Because DNS is everywhere. It's slow, globally cached, and was never meant to do this. That’s why we did it.

---

## 🔒 License

This project is [licensed](License.md) under the **FreeForEducationalandPersonalUse v1.1**, also known as the **“Try Me and Die” License**.

### TL;DR:

- ✅ You can use it for learning, tinkering, academic work, and art projects  
- ❌ You may NOT make a single cent off it without a separate commercial license, or use this to commit crime  
- 💀 If you do, you owe the author(s) all your assets, your firstborn, your pension, and your soul  
- 📹 Plus you’ll appear in [`VIOLATORS.md`](VIOLATORS.md) and the world will laugh at you forever

**🤝 If you’re a corporate goon and you want to Use this Legally?** read [`TERMS_OF_HUMILIATION.md`](TERMS_OF_HUMILIATION.md) first, then go away or send an email like an adult, we're far more chill than our code lets on...  
📧 ChristopherNeitzert@neitzert.com

---

## 🛠 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/DNSFS.git
   cd DNSFS
   ```

2. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. (Optional) Set up the Dockerized DNS server:
   ```bash
   cd DNSFS_DNS_Docker_server
   docker-compose up
   ```

4. Run the client:
   ```bash
   python DNSFS_Client/mountDNSFS.py --domain example.com --mountpoint /mnt/dnsfs
   ```

---

## 🚀 Usage Examples

### Mount the Filesystem
```bash
python DNSFS_Client/mountDNSFS.py --domain example.com --mountpoint /mnt/dnsfs --server 127.0.0.1 --port 1053
```

### Create and Write a File
```bash
echo "Hello, DNSFS!" > /mnt/dnsfs/hello.txt
```

### Read a File
```bash
cat /mnt/dnsfs/hello.txt
```

### Unmount the Filesystem
```bash
fusermount -u /mnt/dnsfs
```

---

## 🧪 Requirements

- Python 3.12+
- dnspython>=2.4.2
- cryptography>=41.0.3
- argon2-cffi>=21.3.0
- tqdm>=4.0.0
- Docker (for `DNSFS_DNS_Docker_server/`)
- A working sense of mischief

---

## 🛠 Troubleshooting

### Common Issues

- **DNS Server Not Responding**:
  Ensure your DNS server is running and accessible at the specified `--server` and `--port`.

- **Permission Denied**:
  Run the script with elevated privileges (e.g., `sudo`).

- **File Not Found**:
  Verify that the file exists in the mounted directory.

- **Slow Performance**:
  DNSFS is inherently slow due to DNS limitations. Consider enabling caching (future feature).

If you encounter other issues, please open an issue on GitHub or email us at 📧 ChristopherNeitzert@neitzert.com.

---

## 🦴 Roadmap (maybe)

- [ ] Metadata versioning & integrity hashing  
- [ ] Multi-record block mapping  
- [ ] Optional caching layer for read-only mounts  
- [ ] Improved error handling  
- [ ] Logging enhancements  
- [ ] Performance improvements  
- [ ] Security upgrades  
- [ ] Windows Support  
- [ ] Testing framework  
- [ ] GUI for launching DNSFS like a madman  
- [ ] Community contributions  

---

## 🧪 Testing

To run tests, use the following command:
```bash
pytest tests/
```

Ensure you have the required dependencies installed:
```bash
pip install -r requirements-dev.txt
```

If you encounter issues, please report them in the GitHub issues section.

---

## 🙏 Acknowledgments

- Inspired by the creativity of unconventional storage systems.
- Thanks to the contributors who made this project possible.
- Special thanks to the open-source community for the tools and libraries used in this project.

---

## ❓ FAQ

### Why use DNS for a filesystem?
Because it's fun, weird, and challenges the norms of storage systems.

### Is this production-ready?
No, it's a proof of concept and should not be used in production.

### Can I use this commercially?
No, unless you obtain a commercial license. See the license section for details.

---

## 🔐 Security Considerations

- DNSFS is not designed for secure or sensitive data storage in production environments.
- Ensure your DNS server is properly secured to prevent unauthorized access.
- Use strong passphrases for encryption.

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository.
2. Create a new branch for your feature or bug fix:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add feature-name"
   ```
4. Push to your branch:
   ```bash
   git push origin feature-name
   ```
5. Open a pull request.

Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) for more details.

---

## 📹 Learn from the Mistakes of Others

Check out [`VIOLATORS.md`](VIOLATORS.md) for a humorous take on what happens when you break the license. Don’t be that person.
