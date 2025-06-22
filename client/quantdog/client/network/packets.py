import os
import sys

import structlog
from scapy.layers.inet import IP, TCP, UDP
from scapy.packet import Packet

from quantdog.client.common import logger


def process_packet(packet: Packet):
    logger.debug("Received packet: %s", packet.summary())

    tcp = packet.getlayer(TCP)
    udp = packet.getlayer(UDP)

    if tcp is not None:
        process_tcp_packet(packet, tcp)
    if udp is not None:
        process_udp_packet(packet, udp)


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


def process_udp_packet(packet: Packet, udp: Packet):
    if not udp.payload:
        return

    structlog.contextvars.bind_contextvars(
        src_port=packet[UDP].sport,
        src_ip=packet[IP].src,
        dst_port=packet[UDP].dport,
        dst_ip=packet[IP].dst,
        payload=udp.payload,
    )
    logger.debug("UDP packet identified.")
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
