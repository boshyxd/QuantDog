import logging
import socket

from quantdog.client.common import logger, settings
from quantdog.client.network.tcp_listener import TCPListener


class PQCListenerTCP(TCPListener):
    """Listener for handling PQC-encrypted data"""

    def __init__(
        self, host: str = "0.0.0.0", pqc_port: int = settings.pqc_port
    ):
        super().__init__(host, pqc_port, listener_type="PQC TCP")

    def handler(self, client_socket: socket.socket, client_address: tuple):
        """Handler for PQC encrypted data"""
        try:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break

                logger.debug("Data received: %s", data.hex())

                # Echo the data back
                client_socket.send(data)

        except Exception as e:
            logger.error(f"Error handling client {client_address}: {e}")
        finally:
            client_socket.close()
            logger.info(f"Connection with {client_address} closed")


# Example usage
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Create and start listener
    listener = PQCListenerTCP()

    try:
        listener.start()
    except KeyboardInterrupt:
        listener.stop()
