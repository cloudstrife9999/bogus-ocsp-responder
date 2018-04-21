#!/usr/bin/python3


import sys


from socket import socket
from client_manager import ClientManager
from multiprocessing import Process


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

    if mode_code == "0":
        return "ignore"
    elif mode_code == "1":
        return "404"
    elif mode_code == "2":
        return "500"
    elif mode_code == "3":
        return "malformed_request"
    elif mode_code == "4":
        return "internal_error"
    elif mode_code == "5":
        return "try_later"
    elif mode_code == "6":
        return "sig_required"
    elif mode_code == "7":
        return "unauthorized"
    else:
        __print_help()
        sys.exit(-1)


def __print_help() -> None:
    print("Available modes:")
    print("<mode> --> <meaning>")
    print("0 --> always ignore OCSP requests from clients.")
    print("1 --> always reply to clients with a '404 Not Found' HTTP response.")
    print("2 --> always reply to clients with a '500 Internal Server Error' HTTP response.")
    print("3 --> always reply to clients with a 'malformed_request' OCSP response over HTTP.")
    print("4 --> always reply to clients with an 'internal_error' OCSP response over HTTP.")
    print("5 --> always reply to clients with a 'try_later' OCSP response over HTTP.")
    print("6 --> always reply to clients with a 'sig_required' OCSP response over HTTP.")
    print("7 --> always reply to clients with a 'unauthorized' OCSP response over HTTP.\n")


def __print_server_mode(mode: str) -> None:
    if mode == "ignore":
        msg: str = "ignore OCSP requests from clients."
    elif mode in ["404", "500"]:
        msg: str = "reply to clients with a '" + mode + "' HTTP response."
    elif mode == "internal_error":
        msg: str = "reply to clients with an '" + mode + "' OCSP response over HTTP."
    else:
        msg: str = "reply to clients with a '" + mode + "' OCSP response over HTTP."

    print("You chose to always %s." % msg)


def __start_server(mode: str) -> None:
    server_socket: socket = socket()
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
