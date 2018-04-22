__http_version: str = "HTTP/1.1"

__space: str = " "
__terminators: str = "\r\n"

http_status_codes: dict = {
    "http_200": "200 OK",
    "http_301": "301 Moved Permanently",
    "http_302": "302 Found",
    "http_307": "307 Temporary Redirect",
    "http_308": "308 Permanent Redirect",
    "http_400": "400 Bad Request",
    "http_401": "401 Unauthorized",
    "http_403": "403 Forbidden",
    "http_404": "404 Not Found",
    "http_405": "405 Method Not Allowed",
    "http_408": "408 Request Timeout",
    "http_410": "410 Gone",
    "http_500": "500 Internal Server Error"
}

__http_response_headers: dict = {
    "default": {
        "Content-Type": "application/ocsp-response",
        "Server": "ocsp_responder",
        "Content-Length": "5"
    },
    "http_200": {
        "Content-Length": "0"
    }
}

__ocsp_response_trailing_bytes = bytes([0x30, 0x03, 0x0a, 0x01])

__ocsp_responses: dict = {
    "successful": __ocsp_response_trailing_bytes + bytes([0x00]),  # Requires the 'optional bytes', but we try anyway.
    "malformed_request": __ocsp_response_trailing_bytes + bytes([0x01]),
    "internal_error": __ocsp_response_trailing_bytes + bytes([0x02]),
    "try_later": __ocsp_response_trailing_bytes + bytes([0x03]),
    "__unused__": __ocsp_response_trailing_bytes + bytes([0x04]),
    "sig_required": __ocsp_response_trailing_bytes + bytes([0x05]),
    "unauthorized": __ocsp_response_trailing_bytes + bytes([0x06])
}


def __build__full_ocsp_response(response_type: str, use_headers: bool) -> bytes:
    response: bytes = bytes(__build_http_response(response_type=response_type, use_headers=use_headers), "utf8")

    if not response_type.startswith("http_"):  # we need to send OCSP data.
        response += __ocsp_responses[response_type]

    return response


def __build_http_response(response_type: str, use_headers: bool) -> str:
    http_response = __http_version + __space + __get_http_code(response_type=response_type) + __terminators

    if use_headers:  # i.e., "http_200" or OCSP.
        http_response += __build_headers(response_type=response_type) + __terminators

    return http_response


def __get_http_code(response_type: str) -> str:
    if response_type.startswith("http_"):  # plain HTTP response without OCSP data.
        return http_status_codes[response_type]
    else:  # response_type is one of the OCSP response types.
        return http_status_codes["http_200"]


def __build_headers(response_type: str) -> str:
    headers: str = ""

    if response_type != "http_200":  # by construction, it must be an OCSP response type in this case.
        for k, v in __http_response_headers["default"].items():
            headers += k + ":" + __space + v + __terminators
    else:  # by construction, it must be "http_200" --> we want to send the default headers.
        for k, v in __http_response_headers["http_200"].items():
            headers += k + ":" + __space + v + __terminators

    return headers


def get_response(mode: str) -> bytes:
    if mode == "ignore":
        return bytes()
    else:
        use_headers: bool = not mode.startswith("http_") or mode.startswith("http_200")

        return __build__full_ocsp_response(response_type=mode, use_headers=use_headers)
