from librgb.renderer import Renderer


class RendererParams(object):
    def __init__(self):
        self._width = 800
        self._height = 600
        self._brightness = 50
        self._readers = []
        self._reader_idx = None
        self.reader = None

    @property
    def readers(self):
        return self._readers

    @readers.setter
    def readers(self, value):
        self._readers = value
        if value:
            self._reader_idx = 0
            self.reader = value[self._reader_idx]
        else:
            self.reader = None
            self._reader_idx = -1

    @property
    def brightness(self):
        return self._brightness

    @brightness.setter
    def brightness(self, value):
        self._brightness = min(100, max(0, value))

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = max(1, value)

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = max(1, value)

    def __setattr__(self, key, value):
        old_value = getattr(self, key) if hasattr(self, key) else None
        super(RendererParams, self).__setattr__(key, value)
        if key.startswith('_') or key == 'draw_cb' or old_value == value:
            return
        self.fire_redraw()

    @property
    def shown_bytes(self):
        return self.width * self.height * Renderer.get_byte_count(self.format)

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
