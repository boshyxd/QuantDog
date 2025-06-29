# TODO: Look at liboqs crypto
from pprint import pformat

import oqs
from oqs.oqs import KeyEncapsulation

from quantdog.client.common import logger, settings


def encapsulate_secret(
    server: KeyEncapsulation, public_key_client: bytes
) -> tuple[bytes, bytes]:
    ciphertext, shared_secret_server = server.encap_secret(public_key_client)
    return ciphertext, shared_secret_server


def decapsulate_secret(client: KeyEncapsulation, ciphertext: bytes) -> bytes:
    shared_secret_client = client.decap_secret(ciphertext)
    return shared_secret_client


logger.info("liboqs version: %s", oqs.oqs_version())
with (
    oqs.KeyEncapsulation(settings.kemalg) as client,
    oqs.KeyEncapsulation(settings.kemalg) as server,
):
    logger.info("Key encapsulation details:\n%s", pformat(client.details))

    # Client generates its keypair
    public_key_client = client.generate_keypair()
    # Optionally, the secret key can be obtained by calling export_secret_key()
    # and the client can later be re-instantiated with the key pair:
    # secret_key_client = client.export_secret_key()

    # Store key pair, wait... (session resumption):
    # client = oqs.KeyEncapsulation(kemalg, secret_key_client)

    # The server encapsulates its secret using the client's public key
    ciphertext, shared_secret_server = server.encap_secret(public_key_client)

    # The client decapsulates the server's ciphertext to obtain the shared secret
    shared_secret_client = client.decap_secret(ciphertext)
