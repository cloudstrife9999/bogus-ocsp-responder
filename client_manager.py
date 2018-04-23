import responses


from time import sleep
from socket import socket
from http_dissector import HTTPDissector


def _generate_hex_dump(raw_data: bytes) -> str:
    return " ".join(hex(b) for b in raw_data) + "\n"


class ClientManager:
    def __init__(self, client_socket: socket, client_addr: str, mode: str):
        self.__client_socket: socket = client_socket
        self.__client_address: str = client_addr
        self.__ignore_ocsp_requests: bool = mode == "ignore"
        self.__mode: str = mode
        self.__response_bytes: bytes = responses.get_response(mode=self.__mode)

    def manage_client(self) -> None:
        data: bytes = self.__client_socket.recv(1024)  # We read 1024 bytes at most.

        print("Received request from %s" % self.__client_address)

        try:
            dissector: HTTPDissector = HTTPDissector(raw_data=data)
            dissector.parse()
            dissector.dump()
        except (IndexError, ValueError, TypeError) as e:
            print("An internal error occurred while analyzing the request: '%s'\n" % e)
            print("Hex dump of the received bytes:")
            print(_generate_hex_dump(raw_data=data))

        if not self.__ignore_ocsp_requests:
            print("Sending '" + self.__mode + "' to %s" % self.__client_address)
            self.__client_socket.send(self.__response_bytes)
        else:
            sleep_time: int = 20
            print("Ignoring the request from %s and sleeping for %d seconds..." % (self.__client_address, sleep_time))
            sleep(sleep_time)

        print("Done.")

        self.__client_socket.close()

        print("Connection with %s closed.\n" % self.__client_address)
