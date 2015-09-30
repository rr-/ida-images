import os
from .reader import Reader


class FileReader(Reader):
    def __init__(self, source_path):
        self.source = open(source_path, 'rb')
        self.source.seek(0, os.SEEK_END)
        self._max_address = self.source.tell()
        self.source.seek(0, os.SEEK_SET)

    def get_padded_bytes(self, address, size):
        self.source.seek(address)
        data = self.source.read(size)
        data += b'\x00' * (size - len(data))
        return data

    @property
    def min_address(self):
        return 0

    @property
    def max_address(self):
        return self._max_address

    def translate_address(self, address):
        return '%08x' % address
