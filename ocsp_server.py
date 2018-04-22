#!/usr/bin/python3


import sys


from socket import socket, SO_REUSEADDR, SOL_SOCKET
from client_manager import ClientManager
from multiprocessing import Process


__modes: dict = {
    "0": "ignore",
    "1": "http_200",
    "2": "http_301",
    "3": "http_302",
    "4": "http_307",
    "5": "http_308",
    "6": "http_400",
    "7": "http_401",
    "8": "http_403",
    "9": "http_404",
    "10": "http_405",
    "11": "http_408",
    "12": "http_410",
    "13": "http_500",
    "14": "malformed_request",
    "15": "internal_error",
    "16": "try_later",
    "17": "sig_required",
    "18": "unauthorized",
    "19": "successful"
}


def main():
    __print_server_welcome()

    mode = __get_mode()

    __print_server_mode(mode)
    __start_server(mode)


def __print_server_welcome() -> None:
    print("Welcome to the Bogus OCSP Responder by cloudstrife9999!\n")
    __print_help()


def __get_mode() -> str:
    mode_code: str = input("Please, select the number corresponding to the mode you want to use:\n")

    if mode_code in __modes.keys():
        return __modes[mode_code]
    else:
        __print_help()
        sys.exit(-1)


def __print_help() -> None:
    print("Available modes:")
    print("<mode> --> <meaning>")
    print("0 --> always ignore OCSP requests from clients.")
    print("1 --> always reply to clients with a '200 OK' HTTP response without OCSP data.")
    print("2 --> always reply to clients with a '301 Moved Permanently' HTTP response without OCSP data.")
    print("3 --> always reply to clients with a '302 Found' HTTP response without OCSP data.")
    print("4 --> always reply to clients with a '307 Temporary Redirect' HTTP response without OCSP data.")
    print("5 --> always reply to clients with a '308 Permanent Redirect' HTTP response without OCSP data.")
    print("6 --> always reply to clients with a '400 Bad Request' HTTP response without OCSP data.")
    print("7 --> always reply to clients with a '401 Unauthorized' HTTP response without OCSP data.")
    print("8 --> always reply to clients with a '403 Forbidden' HTTP response without OCSP data.")
    print("9 --> always reply to clients with a '404 Not Found' HTTP response without OCSP data.")
    print("10 --> always reply to clients with a '405 Method Not Allowed' HTTP response without OCSP data.")
    print("11 --> always reply to clients with a '408 Request Timeout' HTTP response without OCSP data.")
    print("12 --> always reply to clients with a '410 Gone' HTTP response without OCSP data.")
    print("13 --> always reply to clients with a '500 Internal Server Error' HTTP response without OCSP data.")
    print("14 --> always reply to clients with a 'malformed_request' OCSP response over HTTP.")
    print("15 --> always reply to clients with an 'internal_error' OCSP response over HTTP.")
    print("16 --> always reply to clients with a 'try_later' OCSP response over HTTP.")
    print("17 --> always reply to clients with a 'sig_required' OCSP response over HTTP.")
    print("18 --> always reply to clients with a 'unauthorized' OCSP response over HTTP.")
    print("19 --> always reply to clients with a 'successful' OCSP response over HTTP (without the required bytes).\n")


def __print_server_mode(mode: str) -> None:
    if mode == "ignore":
        msg: str = "ignore OCSP requests from clients."
    elif mode.startswith("http_"):
        msg: str = "reply to clients with a '" + mode + "' HTTP response without OCSP data."
    elif mode == "internal_error":
        msg: str = "reply to clients with an '" + mode + "' OCSP response over HTTP."
    else:
        msg: str = "reply to clients with a '" + mode + "' OCSP response over HTTP."

    print("You chose to always %s." % msg)


def __start_server(mode: str) -> None:
    server_socket: socket = socket()
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_socket.bind(("0.0.0.0", 80))
    server_socket.listen()

    server_data: str = server_socket.getsockname()[0] + ":" + str(server_socket.getsockname()[1])

    print("Bound to %s\n" % server_data)

    try:
        __loop(server_socket=server_socket, mode=mode)
    except KeyboardInterrupt:
        print("\nShutting down the server...")

        server_socket.close()

        print("Done.")
        print("Bye!")


def __loop(server_socket: socket, mode: str) -> None:
    while True:
        conn: tuple = server_socket.accept()
        client_socket: socket = conn[0]
        client_addr: str = conn[1][0] + ":" + str(conn[1][1])
        client_manager: ClientManager = ClientManager(client_socket=client_socket, client_addr=client_addr, mode=mode)
        Process(target=client_manager.manage_client).start()
        client_socket.close()


if __name__ == "__main__":
    main()
