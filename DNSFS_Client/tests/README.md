# 🤪 DNSFS Testing Suite  
_AKA: The Department of Distributed Sabotage Prevention_

Welcome to `tests/`, the digital proving ground where we find out just how badly you can screw up a DNS-based filesystem before it breaks. Spoiler: it’s surprisingly resilient — unless you sneeze near a recursive resolver.

## What's In Here?

- **`DNSFS_blocktest.py`**  
  Hurts a single block repeatedly. It deserves it. Writes, reads, overwrites, deletes. If it fails, you’ll know. The test won't.

- **`DNSFS_blockreadtest.py`**  
  Attempts to read what should exist. If it doesn’t, one of you lied. The script is not interested in who.

- **`mountDNSFS.py`**  
  Mounts the whole damn thing. If your DNS zone cries, logs it. If your DNS server dies, logs that too. You’ll still be at fault, of course.

## How to Run the Tests

You'll need:
- Python 3.12+
- `fusepy`, `dnspython`, `cryptography`, `argon2-cffi`, `tqdm`
- A functioning will to debug low-level DNS I/O failures

```bash
# Make sure you're not mounted — emotionally or otherwise
sudo umount /tmp/dnsfs || true

# Then:
python3 DNSFS_blocktest.py
python3 DNSFS_blockreadtest.py
```

If these pass, you probably forgot to test something important.

## When It Fails

1. **Check the logs**: `dnsfs.log` knows all.  
2. **Blame someone else**: start with your DNS provider.  
3. **Drink something calming**: you mounted a filesystem over DNS, after all.

## Contributing Tests

If you want to write a new test, go ahead. Just remember:
- If it doesn't fail in absurd edge cases, it's not done.
- If it doesn't produce existential doubt in the user, it's not complete.
- If it passes every time, you probably hardcoded the answer.

---

_“Testing is just believing you caught all the bugs before the public does.”_ – some random developer

---

## License

# License

This testing suite is licensed under the terms of FreeForEducationalandPersonalUse License v1.1
Also known as the “Try Me and Die” License. Please see the top level liscense file for those terms.

If you violate the terms in this license, the `TERMS_OF_HUMILIATION` and `VIOLATORS.md` will be publicly updated with your username, timestamp, and the last thing you googled.

## Warranty

There is none. If this suite bricks your recursive resolver, eats your glue records, or rewrites your zone serials into Nietzsche quotes, that sounds like a *you* problem.

Proceed with caution, caffeine, and backups.
