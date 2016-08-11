import os
from librgb.reader import Reader


class FileReader(Reader):
    def __init__(self, source_path):
        super(FileReader, self).__init__()
        self.path = source_path
        with open(source_path, 'rb') as handle:
            handle.seek(0, os.SEEK_END)
            self._max_address = handle.tell()
            handle.seek(0, os.SEEK_SET)

    def get_padded_bytes(self, size):
        with open(self.path, 'rb') as handle:
            handle.seek(self.address)
            data = handle.read(size)
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
