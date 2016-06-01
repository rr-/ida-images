import os
from librgb.reader import Reader


class FileReader(Reader):
    def __init__(self, source_path):
        super(FileReader, self).__init__()
        self.path = source_path
        self.source = open(source_path, 'rb')
        self.source.seek(0, os.SEEK_END)
        self._max_address = self.source.tell()
        self.source.seek(0, os.SEEK_SET)

    def get_padded_bytes(self, size):
        self.source.seek(self.address)
        data = self.source.read(size)
        data += b'\x00' * (size - len(data))
        return data

    @property
    def min_address(self):
        return 0

    @property
    def max_address(self):
        return self._max_address

    @property
    def address_text(self):
        return '%s @ %08x' % (self.path, self.address)
