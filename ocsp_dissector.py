import binascii


class OCSPDissector:
    def __init__(self, raw_ocsp_data: bytes) -> None:
        if raw_ocsp_data is None:
            raise ValueError("Bad OCSP raw data.")

        self.__raw_data: bytes = raw_ocsp_data
        self.__hash_algorithm: bytes = bytes()
        self.__issuer_name_hash: bytes = bytes()
        self.__issuer_key_hash: bytes = bytes()
        self.__serial_number: int = -1

    def parse(self):
        if len(self.__raw_data) < 68:
            raise ValueError("Bad OCSP raw data.")
        else:
            self.__hash_algorithm = self.__raw_data[14:19]
            self.__issuer_name_hash = self.__raw_data[23:43]
            self.__issuer_key_hash = self.__raw_data[45:65]
            self.__serial_number = self.__raw_data[67:67+int(self.__raw_data[66])]

    def dump(self) -> str:
        s: str = ""
        s += " Wrapped OCSP request:\n"
        s += "  Hash function: %s\n" % self.__hash_lookup()
        s += "  Issuer name hash: %s\n" % str(binascii.hexlify(self.__issuer_name_hash), "utf-8")
        s += "  Issuer key hash: %s\n" % str(binascii.hexlify(self.__issuer_key_hash), "utf-8")
        s += "  Serial number: %s\n" % str(binascii.hexlify(self.__serial_number), "utf-8")

        return s

    def __hash_lookup(self) -> str:
        hashes: dict = {
            "2b0e03021a": "SHA-1"
        }

        k = str(binascii.hexlify(self.__hash_algorithm), "utf-8")

        if k not in hashes.keys():
            raise ValueError("Bad hash function.")
        else:
            return hashes[k]
