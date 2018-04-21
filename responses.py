__http_version: str = "HTTP/1.1"

__space: str = " "
__terminators: str = "\r\n"

__http_status_codes: dict = {
    "200": "200 OK",
    "404": "404 Not Found",
    "500": "500 Internal Server Error"
}

__http_response_headers: dict = {
    "200": {
        "Content-Type": "application/ocsp-response",
        "Server": "ocsp_responder",
        "Content-Length": "5"
    }
}

__ocsp_response_trailing_bytes = bytes([0x30, 0x03, 0x0a, 0x01])

__ocsp_responses: dict = {
    "malformed_request": __ocsp_response_trailing_bytes + bytes([0x01]),
    "internal_error": __ocsp_response_trailing_bytes + bytes([0x02]),
    "try_later": __ocsp_response_trailing_bytes + bytes([0x03]),
    "sig_required": __ocsp_response_trailing_bytes + bytes([0x05]),
    "unauthorized": __ocsp_response_trailing_bytes + bytes([0x06])
}


def __build__full_ocsp_response(response_type: str) -> bytes:
    response: bytes = bytes(__build_http_response(response_type=response_type), "utf8")

    if response_type not in ["404", "500"]:
        response += __ocsp_responses[response_type]

    return response


def __build_http_response(response_type: str) -> str:
    http_response = __http_version + __space + __get_http_code(response_type=response_type) + __terminators

    return http_response + __build_headers(response_type=response_type) + __terminators


def __get_http_code(response_type: str) -> str:
    if response_type in ["404", "500"]:
        return __http_status_codes[response_type]
    else:
        return __http_status_codes["200"]


def __build_headers(response_type: str) -> str:
    headers: str = ""

    if response_type not in ["404", "500"]:
        for k, v in __http_response_headers["200"].items():
            headers += k + ":" + __space + v + __terminators

    return headers


def get_response(mode: str) -> bytes:
    if mode == "ignore":
        return bytes()
    else:
        return __build__full_ocsp_response(response_type=mode)


def get_malformed_request_ocsp_response() -> bytes:
    return __build__full_ocsp_response("malformed_request")


def get_internal_error_ocsp_response() -> bytes:
    return __build__full_ocsp_response("internal_error")


def get_try_later_ocsp_response() -> bytes:
    return __build__full_ocsp_response("try_later")


def get_sig_required_ocsp_response() -> bytes:
    return __build__full_ocsp_response("sig_required")


def get_unauthorized_ocsp_response() -> bytes:
    return __build__full_ocsp_response("unauthorized")


def get_404_http_response() -> bytes:
    return __build__full_ocsp_response("404")


def get_500_http_response() -> bytes:
    return __build__full_ocsp_response("500")
