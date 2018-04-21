from ocsp_dissector import OCSPDissector


class HTTPDissector:
    def __init__(self, raw_data: bytes):
        if raw_data is None:
            raise ValueError("Bad HTTP raw data")

        self.__raw_data: bytes = raw_data
        self.__next_position_to_parse = 0
        self.__method: str = None
        self.__resource: str = None
        self.__http_version: str = None
        self.__headers: dict = {}
        self.__ocsp_raw_request: bytes = None
        self.__ocsp_dissector: OCSPDissector = None

    def parse(self) -> None:
        first_line: str = self.__get_first_line()
        self.__parse_first_line(line=first_line)
        self.__parse_headers()
        self.__ocsp_raw_request = self.__raw_data[self.__next_position_to_parse:]
        self.__parse_ocsp_request()

    def dump(self):
        if self.__method is None:
            raise ValueError("Nothing to visualize!")
        else:
            s: str = "Dissected HTTP:\n"
            s += " Method: %s\n" % self.__method
            s += " Requested resource: %s\n" % self.__resource
            s += " HTTP version: %s\n" % self.__http_version
            s += " HTTP request headers:\n"
            s += self.__dump_headers()
            s += self.__ocsp_dissector.dump()

            print(s)

    def __dump_headers(self) -> str:
        s: str = ""

        for header_name, header_value in self.__headers.items():
            s += "  " + header_name + ": " + header_value + "\n"

        return s

    def __parse_ocsp_request(self) -> None:
        self.__ocsp_dissector = OCSPDissector(self.__ocsp_raw_request)
        self.__ocsp_dissector.parse()

    def __get_first_line(self) -> str:
        line: list = []

        for byte in self.__raw_data:
            if byte != 13:
                line.append(byte)
            else:
                break

        self.__next_position_to_parse = len(line) + 2  # +2 is to exclude \r\n

        return "".join(chr(c) for c in line)

    def __parse_first_line(self, line: str) -> None:
        tokens: list = line.split(" ")
        method_candidate = tokens[0]
        resource_candidate = tokens[1]
        version_candidate = tokens[2]

        if method_candidate not in ["GET", "POST"]:
            raise ValueError("Bad request method!")

        if resource_candidate != "/":
            raise ValueError("Bad resource requested.")

        if version_candidate != "HTTP/1.1":
            raise ValueError("Bad HTTP version!")

        self.__method = method_candidate
        self.__resource = resource_candidate
        self.__http_version = version_candidate

    def __parse_headers(self) -> None:
        tokens: bytes = self.__raw_data[self.__next_position_to_parse:].split(b"\r\n")[:-2]

        self.__next_position_to_parse = self.__raw_data.find(b"\r\n\r\n") + 4

        for token in tokens:
            token: bytes = token
            header_name, header_value = str(token, "utf-8").split(": ")

            if header_name == "" or header_value == "":
                raise ValueError("Bad header!")
            else:
                self.__headers[header_name] = header_value
