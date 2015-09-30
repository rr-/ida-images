from .renderer import Renderer


class RendererParams(object):
    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, v):
        self._brightness = min(100, max(0, v))

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, v):
        self._width = max(1, v)

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, v):
        self._height = max(1, v)

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, v):
        self._address = (
            max(self.reader.min_address, min(self.reader.max_address, v)))

    def __setattr__(self, k, v):
        old_v = getattr(self, k) if hasattr(self, k) else None
        super(RendererParams, self).__setattr__(k, v)
        if k.startswith('_') or k == 'draw_cb' or old_v == v:
            return
        if hasattr(self, 'draw_cb') and self.draw_cb:
            self.draw_cb()

    @property
    def shown_bytes(self):
        bytes = Renderer.FORMAT_MAP[self.format][0]
        return self.width * self.height * bytes
