import logging
import socket
import threading

from quantdog.client.common import logger


class TCPListener:
    """Base TCP listener"""

    # TODO: Add thread locking to avoid memory shenanigans

    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 8888,
        listener_type: str = "TCP",
    ):
        self.host = host
        self.port = port
        self.listener_type = listener_type
        self.socket: socket.socket | None = None
        self.is_running = False

    def start(self):
        """Start the TCP listener."""
        try:
            # Create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Bind to address
            self.socket.bind((self.host, self.port))

            # Start listening
            self.socket.listen(5)
            self.socket.settimeout(5)
            self.is_running = True

            logger.info(
                "%s Listener started on %s:%s",
                self.listener_type,
                self.host,
                self.port,
            )

            while self.is_running:
                try:
                    # Accept connection
                    client_socket, client_address = self.socket.accept()
                    logger.debug(f"New connection from {client_address}")

                    # Handle connection in separate thread
                    client_thread = threading.Thread(
                        target=self.handler,
                        args=(client_socket, client_address),
                    )
                    client_thread.daemon = True
                    client_thread.start()

                except TimeoutError:
                    if self.is_running:
                        continue
                    break
                except OSError as e:
                    if self.is_running:
                        logger.error(f"Socket error: {e}")
                    break

        except Exception as e:
            logger.exception(
                "Failed to start %s listener: %s", self.listener_type, e
            )
            raise

    def stop(self):
        """Stop the TCP listener."""
        self.is_running = False
        if self.socket:
            self.socket.close()
        logger.info("%s Listener stopped", self.listener_type)

    def handler(self, client_socket: socket.socket, client_address: tuple):
        """Basic TCP handler"""
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
    listener = TCPListener()

    try:
        listener.start()
    except KeyboardInterrupt:
        listener.stop()
