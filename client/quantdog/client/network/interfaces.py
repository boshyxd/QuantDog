import fcntl
import os
import struct
from contextlib import contextmanager

from pyroute2 import IPRoute

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
