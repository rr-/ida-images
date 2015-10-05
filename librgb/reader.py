class Reader(object):
    def __init__(self):
        self._address = self.min_address

    @property
    def min_address(self):
        raise NotImplementedError()

    @property
    def max_address(self):
        raise NotImplementedError()

    def get_padded_bytes(self, size):
        raise NotImplementedError()

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, v):
        self._address = (
            max(self.min_address, min(self.max_address, v)))
