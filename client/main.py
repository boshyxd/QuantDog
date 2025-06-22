import psutil

from quantdog.client.common import check_sudo, logger
from quantdog.client.network import create_tun_interface, packet_listener


def main():
    check_sudo()
    tun_name: str = "tunqd"
    with create_tun_interface(tun_name) as tun_fd:
        logger.info("Created interface '%s'.", tun_name, tun_fd=tun_fd)
        for interface_name, details in psutil.net_if_addrs().items():
            stats = psutil.net_if_stats().get(interface_name, None)
            logger.debug(
                "Found interface: %s",
                interface_name,
                details=details,
                stats=stats,
            )

        packet_listener(tun_fd, tun_name)


if __name__ == "__main__":
    main()
