try:
    from PySide import QtCore, QtGui
except ImportError:
    from PyQt4 import QtCore, QtGui


class ShortcutManager(object):
    def __init__(self, window_adapter):
        self.window_adapter = window_adapter

    def register(self, widget):
        if hasattr(widget, 'close'):
            self._define(widget, 'Q', widget.close)
        self._define(widget, 'G', self.window_adapter.changeAddress)
        self._define(widget, 'H', self.window_adapter.resizeLeft)
        self._define(widget, 'J', self.window_adapter.resizeDown)
        self._define(widget, 'K', self.window_adapter.resizeUp)
        self._define(widget, 'L', self.window_adapter.resizeRight)
        self._define(widget, 'Ctrl+F', self.window_adapter.flip)
        self._define(widget, 'Ctrl+left', self.window_adapter.goLeft)
        self._define(widget, 'Ctrl+right', self.window_adapter.goRight)

    def _define(self, widget, shortcut, func):
        QtGui.QShortcut(QtGui.QKeySequence(shortcut), widget, func)
