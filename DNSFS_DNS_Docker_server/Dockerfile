FROM ubuntu:22.04

RUN apt-get update && \
    apt-get install -y bind9 bind9utils dnsutils && \
    mkdir -p /etc/bind/zones && \
    mkdir -p /var/log/named && \
    touch /var/log/named/named.log && \
    chown -R bind:bind /var/log/named

COPY named.conf /etc/bind/named.conf
COPY named.conf.options /etc/bind/named.conf.options
COPY named.conf.local /etc/bind/named.conf.local
COPY db.test.lan /etc/bind/zones/db.test.lan

CMD ["/usr/sbin/named", "-f", "-g", "-c", "/etc/bind/named.conf"]
