import fcntl
import os
import struct
import sys
from contextlib import contextmanager

import structlog
from pyroute2 import IPRoute
from scapy.layers.inet import IP, TCP, UDP
from scapy.packet import Packet

from quantdog.client.common import logger

# TUN/TAP constants
TUNSETIFF = 0x400454CA
IFF_TUN = 0x0001
IFF_NO_PI = 0x1000


@contextmanager
def create_tun_interface(name: str = "tun0"):
    ipr = IPRoute()
    tun_fd = os.open("/dev/net/tun", os.O_RDWR)
    ifr = struct.pack("16sH", name.encode("utf-8"), IFF_TUN | IFF_NO_PI)
    fcntl.ioctl(tun_fd, TUNSETIFF, ifr)

    device = ipr.link_lookup(ifname=name)[0]
    ipr.addr(
        "add",
        index=device,
        address="10.117.0.2",
        prefixlen=24,
        broadcast="10.117.0.255",
    )
    ipr.link("set", index=device, state="up")
    os.system(f"ip route add 10.118.0.0/24 dev {name}")
    os.system(f"ip route add default via 10.117.0.1 dev {name}")

    yield tun_fd

    os.close(tun_fd)
    ipr.close()


def process_packet(packet: Packet):
    logger.debug("Received packet: %s", packet.summary())

    tcp = packet.getlayer(TCP)
    udp = packet.getlayer(UDP)

    if tcp is not None:
        process_tcp_packet(packet, tcp)


def process_tcp_packet(packet: Packet, tcp: Packet):
    if not tcp.payload:
        return

    structlog.contextvars.bind_contextvars(
        src_port=packet[TCP].sport,
        src_ip=packet[IP].src,
        dst_port=packet[TCP].dport,
        dst_ip=packet[IP].dst,
        payload=tcp.payload,
    )
    logger.debug("TCP packet identified.")
    structlog.contextvars.clear_contextvars()


def packet_listener(tun_fd: int, tun_name: str):
    logger.info("Server running. Use CTRL+C to exit.")
    try:
        while True:
            raw_packet = os.read(tun_fd, 1500)
            packet = IP(raw_packet)
            process_packet(packet)

    except KeyboardInterrupt:
        pass
    finally:
        logger.info("Shutting down.")
        sys.exit(0)
