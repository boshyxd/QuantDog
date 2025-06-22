# TODO: Look at liboqs crypto
from pprint import pformat

import oqs

from quantdog.client.common import logger

logger.info("liboqs version: %s", oqs.oqs_version())
kemalg = "ML-KEM-512"
with (
    oqs.KeyEncapsulation(kemalg) as client,
    oqs.KeyEncapsulation(kemalg) as server,
):
    logger.info("Key encapsulation details:\n%s", pformat(client.details))
