import os
import socket
import sys
import uuid
from functools import cache

import structlog
from scapy.layers.inet import IP, TCP, UDP
from scapy.packet import Packet

from quantdog.client.common import logger, settings


@cache
def get_secret_cache() -> dict[str, bytes]:
    return dict()


# Probably want to convert this to an LRU cache somehow
SECRET_CACHE = get_secret_cache()


def process_packet(packet: Packet):
    tcp = packet.getlayer(TCP)
    udp = packet.getlayer(UDP)

    if tcp is not None:
        process_tcp_packet(packet, tcp)
    # if udp is not None:
    #     process_udp_packet(packet, udp)


def add_kem_secret(dst_ip: str):
    dst_kem_port = settings.kem_port

    try:
        kem_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        kem_client.settimeout(5)
        kem_client.connect((dst_ip, dst_kem_port))
        logger.debug("Connected for KEM encryption!")
        return True
    except TimeoutError:
        logger.debug("KEM port not found on %s.", dst_ip)
        structlog.contextvars.clear_contextvars()
        return False
    except Exception as e:
        logger.exception(str(e))
        structlog.contextvars.clear_contextvars()
        raise


def process_tcp_packet(packet: Packet, tcp: Packet):
    if not tcp.payload:
        return

    structlog.contextvars.bind_contextvars(
        src_port=packet[TCP].sport,
        src_ip=packet[IP].src,
        dst_port=packet[TCP].dport,
        dst_ip=packet[IP].dst,
        len=packet[IP].len,
        payload=tcp.payload,
        packet_request_id=uuid.uuid4().hex,
    )

    logger.debug("TCP packet identified.")

    # This is going to be modified and encrypted as a payload
    payload_packet = packet.copy()
    transport_packet = packet

    dst_ip = transport_packet[IP].dst

    if dst_ip not in SECRET_CACHE:
        addition_successful = add_kem_secret(dst_ip)
        if not addition_successful:
            return

    payload_packet[IP].dst = "127.0.0.1"
    transport_packet[TCP].dport = settings.pqc_port
    payload_layer = transport_packet.lastlayer()
    logger.debug("Encrypting packet using %s.", settings.kemalg)

    payload_layer.load = "HEYO"

    del transport_packet[IP].len
    del transport_packet[IP].chksum
    del transport_packet[TCP].chksum

    transport_packet = IP(transport_packet.build())

    structlog.contextvars.bind_contextvars(
        src_port=transport_packet[TCP].sport,
        src_ip=transport_packet[IP].src,
        dst_port=transport_packet[TCP].dport,
        dst_ip=transport_packet[IP].dst,
        len=transport_packet[IP].len,
        payload=tcp.payload,
    )

    logger.debug("Modifications complete.")

    # TODO
    # 1. Identify whether a Quantdog is running on that server
    # 2. Perform a key exchange with the Quantdog server
    # 3. Send the modified packet
    #
    # Maybe I should be encrypting the *entire packet?*
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

    raw_packet_bytes = bytes(packet)

    structlog.contextvars.bind_contextvars()

    logger.debug("UDP packet identified.")
    structlog.contextvars.clear_contextvars()


def packet_listener(tun_fd: int, tun_name: str):
    logger.info("Server running. Use CTRL+C to exit.")
    try:
        while True:
            raw_packet = os.read(tun_fd, settings.packet_length)
            packet = IP(raw_packet)
            processed_packet = process_packet(packet)

    except KeyboardInterrupt:
        pass

    except Exception as e:
        logger.exception(str(e))
    finally:
        logger.info("Shutting down.")
        sys.exit(0)
