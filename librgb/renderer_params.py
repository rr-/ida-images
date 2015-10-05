from .renderer import Renderer


class RendererParams(object):
    @property
    def readers(self):
        return self._readers

    @readers.setter
    def readers(self, v):
        self._readers = v
        if v:
            self._reader_idx = 0
            self.reader = v[self._reader_idx]
        else:
            self.reader = None
            self._reader_idx = -1

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

    def __setattr__(self, k, v):
        old_v = getattr(self, k) if hasattr(self, k) else None
        super(RendererParams, self).__setattr__(k, v)
        if k.startswith('_') or k == 'draw_cb' or old_v == v:
            return
        self.fire_redraw()

    @property
    def shown_bytes(self):
        bytes = Renderer.FORMAT_MAP[self.format][0]
        return self.width * self.height * bytes

    def fire_redraw(self):
        if hasattr(self, 'draw_cb') and self.draw_cb:
            self.draw_cb()

    def use_prev_reader(self):
        if self._reader_idx > 0:
            self._reader_idx -= 1
            self.reader = self.readers[self._reader_idx]

    def use_next_reader(self):
        if self._reader_idx + 1 < len(self.readers):
            self._reader_idx += 1
            self.reader = self.readers[self._reader_idx]
