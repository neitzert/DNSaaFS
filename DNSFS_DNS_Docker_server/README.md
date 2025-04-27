🛰 DNSFS DNS Docker Server
Welcome to the DNSFS authoritative DNS zone server, lovingly stuffed into a Docker container for your convenience and plausible deniability.

This is the backend for DNSFS, the filesystem that shouldn't exist — where files live as encrypted TXT records inside a DNS zone.

⚙️ What This Does
Runs BIND9 in a container

Serves an editable zone file (e.g. test.lan)

Accepts dynamic DNS updates from the DNSFS client

Exposes TCP and UDP on port 1053

Logs everything — because the court will want details

🛠 Files in this directory
```
.
├── Dockerfile             # Builds the DNS server image
├── docker-compose.yml     # Spins it up with named.conf config & volume mappings
├── build.sh               # Shorthand for docker build
├── named.conf*            # BIND9 config: main, local, options
├── db.test.lan            # Your DNS zone file (edit or replace as needed)
└── zones/                 # Mounted into container for persistent zone storage
```

🚀 Quick Start
```./build.sh
docker-compose up -d
```
This will:

Build the image as dnsfs-bind9

Start it as dnsfs-server

Listen on port 1053 (both TCP and UDP)

Use a static IP: 172.28.0.53 inside the dnsnet bridge

You'll need to point your DNSFS client at this IP and port.

🔐 Dynamic Updates
Dynamic updates are allowed from anyone because:

You’re running this locally

We have no fear

DNSSEC is off

You're supposed to know better

If you don’t know what you’re doing, stop reading and go touch grass.

⚠️ Warnings
This server is not secure.

Do not expose this to the public Internet unless you're a chaos enthusiast.

No rate limiting, no validation, no sanity checks.

This was built to make DNS cry. It succeeds.

🔥 License
Covered under the Try Me and Die License v1.1​
.
Commercial use triggers extreme legal, personal, and metaphysical consequences.

🚫 No Warranties
This container might:

Break DNS across your network

Cause bind9 to segfault in 17 languages

Accidentally resolve apple.com to localhost

Summon ghosts from the DARPA net

Emit ASCII smoke in your terminal

If you thought this would work on the first try, that's adorable.

Use at your own risk. Preferably in a VM, wearing gloves, behind three firewalls, and after making peace with your gods.

Look, this is a tool that uses a protocol from 1983 as a distributed block store

This is not safe. This is not supported. This is not sane. You likely belong here.

We offer:

❌ No uptime promises

❌ No data loss protection

❌ No DNSSEC hugs

❌ No warranty of fitness for anything except chaos

If it bricks your system, leaks your files, corrupts your dog, or gets you featured in a DEF CON talk — that’s on you.

It might work. It might summon Clippy. It might email your boss a hexdump of your Porn folder.
We don’t know. We don’t want to know. Don’t send bug reports unless they’re funny.
