class ShortcutManager(object):
    def __init__(self, window_adapter, params):
        self.window_adapter = window_adapter
        self.params = params

    @property
    def shortcuts(self):
        return {
            "G": self.window_adapter.change_address,
            "Ctrl+S": self.window_adapter.save,
            "H": self.resize_near_left,
            "J": self.resize_near_down,
            "K": self.resize_near_up,
            "L": self.resize_near_right,
            "Shift+H": self.resize_far_left,
            "Shift+J": self.resize_far_down,
            "Shift+K": self.resize_far_up,
            "Shift+L": self.resize_far_right,
            "Ctrl+F": self.toggle_flip,
            "left": self.go_near_left,
            "right": self.go_near_right,
            "Shift+left": self.go_near_medium_left,
            "Shift+right": self.go_near_medium_right,
            "Ctrl+left": self.go_medium_left,
            "Ctrl+right": self.go_medium_right,
            "Ctrl+Shift+left": self.go_far_left,
            "Ctrl+Shift+right": self.go_far_right,
            "<": self.go_to_prev_file,
            ">": self.go_to_next_file,
        }

    def resize_near_left(self):
        self.params.width -= 1

    def resize_near_right(self):
        self.params.width += 1

    def resize_near_up(self):
        self.params.height -= 1

    def resize_near_down(self):
        self.params.height += 1

    def resize_far_left(self):
        self.params.width -= 25

    def resize_far_right(self):
        self.params.width += 25

    def resize_far_up(self):
        self.params.height -= 25

    def resize_far_down(self):
        self.params.height += 25

    def toggle_flip(self):
        self.params.flip = not self.params.flip

    def go_near_left(self):
        self.params.reader.address -= 1
        self.params.fire_redraw()

    def go_near_right(self):
        self.params.reader.address += 1
        self.params.fire_redraw()

    def go_near_medium_left(self):
        self.params.reader.address -= 25
        self.params.fire_redraw()

    def go_near_medium_right(self):
        self.params.reader.address += 25
        self.params.fire_redraw()

    def go_medium_left(self):
        self.params.reader.address -= self.params.shown_bytes // 10
        self.params.fire_redraw()

    def go_medium_right(self):
        self.params.reader.address += self.params.shown_bytes // 10
        self.params.fire_redraw()

    def go_far_left(self):
        self.params.reader.address -= self.params.shown_bytes
        self.params.fire_redraw()

    def go_far_right(self):
        self.params.reader.address += self.params.shown_bytes
        self.params.fire_redraw()

    def go_to_prev_file(self):
        self.params.use_prev_reader()

    def go_to_next_file(self):
        self.params.use_next_reader()
