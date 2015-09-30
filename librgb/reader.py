class Reader(object):
    @property
    def max_address(self):
        raise NotImplementedError()

    def get_padded_bytes(self, address, size):
        raise NotImplementedError()
