try:
    from PySide import QtGui
except ImportError:
    from PyQt4 import QtGui


class ShortcutManager(object):
    def __init__(self, window_adapter, params):
        self.window_adapter = window_adapter
        self.params = params

    def register(self, widget):
        if hasattr(widget, 'close'):
            self._define(widget, 'Q', widget.close)
        self._define(widget, 'G', self.window_adapter.change_address)
        self._define(widget, 'Ctrl+S', self.window_adapter.save)
        self._define(widget, 'H', self.resize_near_left)
        self._define(widget, 'J', self.resize_near_down)
        self._define(widget, 'K', self.resize_near_up)
        self._define(widget, 'L', self.resize_near_right)
        self._define(widget, 'Shift+H', self.resize_far_left)
        self._define(widget, 'Shift+J', self.resize_far_down)
        self._define(widget, 'Shift+K', self.resize_far_up)
        self._define(widget, 'Shift+L', self.resize_far_right)
        self._define(widget, 'Ctrl+F', self.toggle_flip)
        self._define(widget, 'left', self.go_near_left)
        self._define(widget, 'right', self.go_near_right)
        self._define(widget, 'Shift+left', self.go_near_medium_left)
        self._define(widget, 'Shift+right', self.go_near_medium_right)
        self._define(widget, 'Ctrl+left', self.go_medium_left)
        self._define(widget, 'Ctrl+right', self.go_medium_right)
        self._define(widget, 'Ctrl+Shift+left', self.go_far_left)
        self._define(widget, 'Ctrl+Shift+right', self.go_far_right)

    def _define(self, widget, shortcut, func):
        QtGui.QShortcut(QtGui.QKeySequence(shortcut), widget, lambda: func())

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
        self.params.address -= 1

    def go_near_right(self):
        self.params.address += 1

    def go_near_medium_left(self):
        self.params.address -= 25

    def go_near_medium_right(self):
        self.params.address += 25

    def go_medium_left(self):
        self.params.address -= self.params.shown_bytes // 10

    def go_medium_right(self):
        self.params.address += self.params.shown_bytes // 10

    def go_far_left(self):
        self.params.address -= self.params.shown_bytes

    def go_far_right(self):
        self.params.address += self.params.shown_bytes
