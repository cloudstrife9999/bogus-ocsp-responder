#!/usr/bin/python3


import sys


from socket import socket, SO_REUSEADDR, SOL_SOCKET
from client_manager import ClientManager
from multiprocessing import Process
from responses import http_status_codes


__modes: dict = {
    "0": {
        "0": "http_200",
        "1": "http_301",
        "2": "http_302",
        "3": "http_307",
        "4": "http_308",
        "5": "http_400",
        "6": "http_401",
        "7": "http_403",
        "8": "http_404",
        "9": "http_405",
        "10": "http_408",
        "11": "http_410",
        "12": "http_500"
    },
    "1": {
        "0": "successful",
        "1": "malformed_request",
        "2": "internal_error",
        "3": "try_later",
        "4": "__unused__",
        "5": "sig_required",
        "6": "unauthorized"
    },
    "2": {
        "0": "ignore"
    }
}


def main():
    __print_server_welcome()

    mode = __get_mode()

    __print_server_mode(mode)
    __start_server(mode)


def __print_server_welcome() -> None:
    print("Welcome to the Bogus OCSP Responder by cloudstrife9999!\n")
    __print_help(mode_code="help")


def __get_mode() -> str:
    mode_code: str = input("Please choose the number corresponding to a class of behaviors:\n")

    if mode_code not in __modes.keys():
        __print_help(mode_code="help")
        sys.exit(-1)
    else:
        return __get_sub_mode(mode_code=mode_code)


def __get_sub_mode(mode_code: str) -> str:
    if mode_code == "0":
        print("\nYou chose to send a plain HTTP response without OCSP data.")
        __print_plain_http_mode_help()
        sub_mode_code = input("Select a behavior:\n")
    elif mode_code == "1":
        print("\nYou chose to send an OCSP response over plain HTTP.")
        __print_ocsp_over_http_mode_help()
        sub_mode_code = input("Select a behavior:\n")
    elif mode_code == "2":
        print("\nYou chose a miscellaneous behavior.")
        __print_misc_mode_help()
        sub_mode_code = input("Select a behavior:\n")
    else:
        raise ValueError()  # this branch cannot be reached.

    return __validate_sub_mode_code(mode_code=mode_code, sub_mode_code=sub_mode_code)


def __validate_sub_mode_code(mode_code: str, sub_mode_code: str) -> str:
    if sub_mode_code not in __modes[mode_code].keys():
        __print_help(mode_code=mode_code)
        sys.exit(-1)

    return __modes[mode_code][sub_mode_code]


def __print_help(mode_code: str) -> None:
    if mode_code == "help":
        __print_main_help()
    elif mode_code == "0":
        __print_plain_http_mode_help()
    elif mode_code == "1":
        __print_ocsp_over_http_mode_help()
    elif mode_code == "2":
        __print_misc_mode_help()


def __print_main_help() -> None:
    print("Available classes of behaviors:")
    print("<code> --> <meaning>")
    print("0 --> choose a plain HTTP response without OCSP data.")
    print("1 --> choose an OCSP response over plain HTTP.")
    print("2 --> choose a miscellaneous behavior.\n")


def __print_plain_http_mode_help() -> None:
    print("Available plain HTTP responses without OCSP data:")
    print("<code> --> <meaning>")
    print("0 --> always reply to clients with a '200 OK' HTTP response without OCSP data.")
    print("1 --> always reply to clients with a '301 Moved Permanently' HTTP response without OCSP data.")
    print("2 --> always reply to clients with a '302 Found' HTTP response without OCSP data.")
    print("3 --> always reply to clients with a '307 Temporary Redirect' HTTP response without OCSP data.")
    print("4 --> always reply to clients with a '308 Permanent Redirect' HTTP response without OCSP data.")
    print("5 --> always reply to clients with a '400 Bad Request' HTTP response without OCSP data.")
    print("6 --> always reply to clients with a '401 Unauthorized' HTTP response without OCSP data.")
    print("7 --> always reply to clients with a '403 Forbidden' HTTP response without OCSP data.")
    print("8 --> always reply to clients with a '404 Not Found' HTTP response without OCSP data.")
    print("9 --> always reply to clients with a '405 Method Not Allowed' HTTP response without OCSP data.")
    print("10 --> always reply to clients with a '408 Request Timeout' HTTP response without OCSP data.")
    print("11 --> always reply to clients with a '410 Gone' HTTP response without OCSP data.")
    print("12 --> always reply to clients with a '500 Internal Server Error' HTTP response without OCSP data.\n")


def __print_ocsp_over_http_mode_help() -> None:
    print("Available OCSP responses over plain HTTP:")
    print("<code> --> <meaning>")
    print("0 --> always reply to clients with a 'successful' OCSP response over HTTP (without the required bytes).")
    print("1 --> always reply to clients with a 'malformed_request' OCSP response over HTTP.")
    print("2 --> always reply to clients with an 'internal_error' OCSP response over HTTP.")
    print("3 --> always reply to clients with a 'try_later' OCSP response over HTTP.")
    print("4 --> always reply to clients with the sequence [0x30, 0x03, 0x0a, 0x01, 0x04] over HTTP.")
    print("5 --> always reply to clients with a 'sig_required' OCSP response over HTTP.")
    print("6 --> always reply to clients with an 'unauthorized' OCSP response over HTTP.\n")


def __print_misc_mode_help() -> None:
    print("Available miscellaneous behaviors:")
    print("<code> --> <meaning>")
    print("0 --> always ignore OCSP requests from clients.\n")


def __print_server_mode(mode: str) -> None:
    if mode == "ignore":
        msg: str = "ignore OCSP requests from clients."
    elif mode.startswith("http_"):
        msg: str = "reply to clients with a '" + http_status_codes[mode] + "' HTTP response without OCSP data."
    elif mode in ["internal_error", "unauthorized"]:
        msg: str = "reply to clients with an '" + mode + "' OCSP response over HTTP."
    elif mode == "__unused__":
        msg: str = "reply to clients with the sequence [0x30, 0x03, 0x0a, 0x01, 0x04] over HTTP."
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
