#!/usr/bin/python3
import argparse
import os, sys

try:
    import idaapi
    has_ida = True
except ImportError:
    has_ida = False

try:
    from PySide import QtCore, QtGui
    has_pyside = True
except ImportError:
    from PyQt4 import Qt, QtCore, QtGui
    has_pyqt = True

try:
    import numpy
    has_numpy = True
except ImportError:
    print('Brightness adjustment will be slow without numpy')
    has_numpy = False


class PixelFormats(object):
    RGB888    = 'RGB (8-8-8)'
    RGB565    = 'RGB (5-6-5)'
    RGBA8888  = 'RGBA (8-8-8-8)'
    RGBA8888i = 'RGBA (8-8-8-8, invert alpha)'
    RGBA8888x = 'RGBA (8-8-8-8, ignore alpha)'
    RGBA5658  = 'RGBA (5-6-5-8)'
    RGBA5658i = 'RGBA (5-6-5-8, invert alpha)'
    RGBA5658  = 'RGBA (5-6-5-8)'
    BGR888    = 'BGR (8-8-8)'
    BGR565    = 'BGR (5-6-5)'
    BGRA8888  = 'BGRA (8-8-8-8)'
    BGRA8888i = 'BGRA (8-8-8-8, invert alpha)'
    BGRA8888x = 'BGRA (8-8-8-8, ignore alpha)'
    BGRA5658  = 'BGRA (5-6-5-8)'
    BGRA5658i = 'BGRA (5-6-5-8, invert alpha)'
    BGRA5658  = 'BGRA (5-6-5-8)'
    GRAY8     = 'Grayscale (8)'

    @staticmethod
    def get_short_names():
        return [v for v in dir(PixelFormats) if not '_' in v]

    @staticmethod
    def get_long_names():
        short_names = PixelFormats.get_short_names()
        return [PixelFormats.from_short_name(text) for text in short_names]

    @staticmethod
    def from_short_name(text):
        return getattr(PixelFormats, text)

class Reader(object):
    @property
    def max_address(self):
        raise NotImplementedError()

    def get_padded_bytes(self, address, size):
        raise NotImplementedError()

class FileReader(object):
    def __init__(self, source_path):
        self.source = open(source_path, 'rb')
        self.source.seek(0, os.SEEK_END)
        self._max_address = self.source.tell()
        self.source.seek(0, os.SEEK_SET)

    def get_padded_bytes(self, address, size):
        self.source.seek(address)
        data = self.source.read(size)
        data += b'\x00' * (size - len(data))
        return data

    @property
    def min_address(self):
        return 0

    @property
    def max_address(self):
        return self._max_address

# Reads continuous memory chunk even if it spans accross multiple segments.
# "Missing" bytes are filled with NULL byte.
class MemoryReader(Reader):
    class MemoryRange(object):
        def __init__(self, start, end):
            self.start = start
            self.end = end

        def length(self):
            return self.end - self.start

        def __str__(self):
            return 'start: %08x end: %08x' % (self.start, self.end)

    def get_padded_bytes(self, address, count):
        result = "\x00" * count
        ranges_left = [self.MemoryRange(address, address + count)]

        segment_count = idaapi.get_segm_qty()
        valid_memory_ranges = []
        for i in range(segment_count):
            segment = idaapi.getnseg(i)
            #skip segments with unstable data
            if segment.type == SEG_XTRN:
                continue
            valid_memory_ranges.append(
                self.MemoryRange(segment.startEA, segment.endEA))

        while len(ranges_left) > 0:
            #get a requested memory range and remove it from the list
            current_range = ranges_left.pop()

            intersection = None
            for memory_range in valid_memory_ranges:
                start = max(current_range.start, memory_range.start)
                end = min(current_range.end, memory_range.end)
                if end > start:
                    intersection = self.MemoryRange(start, end)
                    break

            #no segment can satisfy any part of requested range
            if intersection is None:
                continue

            chunk = GetManyBytes(
                intersection.start,
                intersection.end - intersection.start)
            if chunk is None:
                print('Some bytes are unreadable in %s..%s' % (
                    atoa(intersection.start), atoa(intersection.end)))
                continue

            result = \
                result[0:intersection.start - address] \
                + chunk \
                + result[intersection.end - address:]
            assert(len(result) == count)

            #if necessary, enqueue ranges unsatisfied by chosen mem segment
            range1 = self.MemoryRange(current_range.start, intersection.start)
            range2 = self.MemoryRange(intersection.end, current_range.end)
            if range1.length > 0:
                ranges_left.append(range1)
            if range2.length > 0:
                ranges_left.append(range2)

        assert(len(result) == count)
        return result

    @property
    def min_address(self):
        return idaapi.cvar.inf.minEA

    @property
    def max_address(self):
        return idaapi.cvar.inf.maxEA


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

class Renderer(object):
    FORMAT_MAP = \
    {
        PixelFormats.RGB888:    (3, QtGui.QImage.Format_RGB888,   True,  False),
        PixelFormats.RGB565:    (2, QtGui.QImage.Format_RGB16,    True,  False),
        PixelFormats.RGBA8888:  (4, QtGui.QImage.Format_ARGB32,   True,  False),
        PixelFormats.RGBA8888i: (4, QtGui.QImage.Format_ARGB32,   True,  True),
        PixelFormats.RGBA8888x: (4, QtGui.QImage.Format_RGB32,    True,  False),
        PixelFormats.RGBA5658:  (3, QtGui.QImage.Format_RGB16,    True,  False),
        PixelFormats.RGBA5658i: (3, QtGui.QImage.Format_RGB16,    True,  True),
        PixelFormats.BGR888:    (3, QtGui.QImage.Format_RGB888,   False, False),
        PixelFormats.BGR565:    (2, QtGui.QImage.Format_RGB16,    False, False),
        PixelFormats.BGRA8888:  (4, QtGui.QImage.Format_ARGB32,   False, False),
        PixelFormats.BGRA8888i: (4, QtGui.QImage.Format_ARGB32,   False, True),
        PixelFormats.BGRA8888x: (4, QtGui.QImage.Format_RGB32,    False, False),
        PixelFormats.BGRA5658:  (3, QtGui.QImage.Format_RGB16,    False, False),
        PixelFormats.BGRA5658i: (3, QtGui.QImage.Format_RGB16,    False, True),
        PixelFormats.GRAY8:     (1, QtGui.QImage.Format_Indexed8, False, False),
    }

    def __init__(self, params):
        self.params = params

    def getPixmap(self):
        params = self.params
        reader = self.params.reader

        if params.format not in self.FORMAT_MAP:
            raise NotImplementedError()

        channels, qt_format, swap_rgb, invert_alpha = \
            self.FORMAT_MAP[params.format]

        stride = params.width * channels
        data_size = params.height * stride
        data = reader.get_padded_bytes(params.address, data_size)
        assert data is not None
        assert len(data) == data_size

        if params.flip:
            output = b''
            for y in range(params.height):
                y2 = params.height - 1 - y
                output += data[y2 * stride:(y2 + 1) * stride]
            data = output

        if params.brightness != 50.0:
            #param   multiplier
            #0       0 = 2^(-8)
            #50      1 = 2^0
            #100     256 = 2^8
            multiplier = 2 ** ((params.brightness - 50) / (50 / 8))
            if has_numpy:
                arr = numpy.fromstring(data, dtype=numpy.uint8)
                arr = arr.astype(dtype=numpy.float)
                arr *= multiplier
                arr = arr.clip(0, 255)
                arr = arr.astype(dtype=numpy.uint8)
                data = arr.tobytes()
            else:
                output = bytearray(len(data))
                for i in range(len(data)):
                    output[i] = int(output[i] * multiplier) & 0xFF
                data = output

        image = QtGui.QImage(
            data,
            params.width,
            params.height,
            params.width * channels,
            qt_format)
        assert len(data) == image.byteCount()

        if swap_rgb:
            image = image.rgbSwapped()
        if invert_alpha:
            image.invertPixels(QtGui.QImage.InvertRgba)
            image.invertPixels(QtGui.QImage.InvertRgb)

        #creating pixmap crashes on RGB32?
        if qt_format == QtGui.QImage.Format_RGB32:
            image = image.convertToFormat(QtGui.QImage.Format_RGB888)

        pixmap = QtGui.QPixmap()
        pixmap.convertFromImage(image)
        return pixmap

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

class GenericWindowAdapter(object):
    def __init__(self, params):
        self.params = params

    def createLayout(self):
        layout = QtGui.QVBoxLayout()

        upper_toolbar = QtGui.QHBoxLayout()
        self.addFormatBox(upper_toolbar)
        self.addSizeBoxes(upper_toolbar)
        upper_toolbar.addStretch()
        self.addFlipCheckbox(upper_toolbar)
        self.addBrightnessBox(upper_toolbar)

        lower_toolbar = QtGui.QHBoxLayout()
        self.addAddressLabel(lower_toolbar)
        lower_toolbar.addStretch()
        self.addGotoButton(lower_toolbar)
        self.addRedrawButton(lower_toolbar)
        self.addSaveButton(lower_toolbar)

        self.image_label = QtGui.QLabel()
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        scroll_area = QtGui.QScrollArea()
        scroll_area.setWidget(self.image_label)
        scroll_area.setWidgetResizable(True)
        layout.addLayout(upper_toolbar)
        layout.addWidget(scroll_area)
        layout.addLayout(lower_toolbar)

        return layout

    def addFormatBox(self, layout):
        self.format_box = QtGui.QComboBox()
        for text in PixelFormats.get_long_names():
            self.format_box.addItem(text, text)
        self.format_box.currentIndexChanged.connect(self.formatChanged)
        layout.addWidget(self.format_box)

    def addFlipCheckbox(self, layout):
        self.flip_checkbox = QtGui.QCheckBox()
        self.flip_checkbox.stateChanged.connect(self.flipChanged)
        self.flip_checkbox.setText('Flip vertically')
        layout.addWidget(self.flip_checkbox)

    def addBrightnessBox(self, layout):
        layout.addWidget(QtGui.QLabel('Brightness:'))
        self.brightness_box = QtGui.QDoubleSpinBox()
        self.brightness_box.setMinimum(0.0)
        self.brightness_box.setMaximum(100.0)
        self.brightness_box.valueChanged.connect(self.brightnessChanged)
        layout.addWidget(self.brightness_box)

    def addSizeBoxes(self, layout):
        self.width_box = QtGui.QSpinBox()
        self.width_box.setMinimum(1)
        self.width_box.setMaximum(2000)
        self.width_box.valueChanged.connect(self.widthChanged)
        layout.addWidget(self.width_box)
        layout.addWidget(QtGui.QLabel('x'))
        self.height_box = QtGui.QSpinBox()
        self.height_box.setMinimum(1)
        self.height_box.setMaximum(2000)
        self.height_box.valueChanged.connect(self.heightChanged)
        layout.addWidget(self.height_box)

    def addGotoButton(self, layout):
        goto_button = QtGui.QPushButton('&Go to... [G]')
        goto_button.setDefault(True)
        goto_button.clicked.connect(self.changeAddress)
        layout.addWidget(goto_button)

    def addAddressLabel(self, layout):
        address_label1 = QtGui.QLabel('Address:')
        address_label2 = QtGui.QLabel('...')
        layout.addWidget(address_label1)
        layout.addWidget(address_label2)
        self.address_label = address_label2

    def addSaveButton(self, layout):
        save_button = QtGui.QPushButton('&Save...')
        save_button.clicked.connect(self.save)
        layout.addWidget(save_button)

    def addRedrawButton(self, layout):
        redraw_button = QtGui.QPushButton('&Redraw')
        redraw_button.clicked.connect(self.draw)
        layout.addWidget(redraw_button)


    def flipChanged(self, state):
        self.params.flip = state == QtCore.Qt.Checked

    def brightnessChanged(self, value):
        self.params.brightness = value

    def widthChanged(self, newWidth):
        self.params.width = newWidth

    def heightChanged(self, newHeight):
        self.params.height = newHeight

    def formatChanged(self, newFormatIndex):
        self.params.format = \
            self.format_box.itemData(self.format_box.currentIndex())


    def changeAddress(self):
        address = self.ask_address(self.params.address)
        if address is not None:
            self.params.address = address

    def resizeLeft(self):
        self.params.width -= 1

    def resizeRight(self):
        self.params.width += 1

    def resizeUp(self):
        self.params.height -= 1

    def resizeDown(self):
        self.params.height += 1

    def flip(self):
        self.params.flip = not self.params.flip

    def goLeft(self):
        self.params.address -= self.params.shown_bytes

    def goRight(self):
        self.params.address += self.params.shown_bytes

    def save(self):
        path = self.ask_file()
        if path is not None:
            self.image_label.pixmap().save(path, 'PNG')

    def draw(self):
        self.params.draw_cb = None

        self.address_label.setText('%08x' % self.params.address)
        self.flip_checkbox.setCheckState(
            QtCore.Qt.Checked if self.params.flip else QtCore.Qt.Unchecked)
        self.brightness_box.setValue(self.params.brightness)
        self.width_box.setValue(self.params.width)
        self.height_box.setValue(self.params.height)
        self.format_box.setCurrentIndex(
            self.format_box.findData(self.params.format))

        pixmap = Renderer(self.params).getPixmap()
        self.image_label.setPixmap(pixmap)

        self.params.draw_cb = self.draw

def parse_args():
    class CustomHelpFormatter(argparse.HelpFormatter):
        def __init__(self, prog):
            super().__init__(prog, max_help_position=40, width=80)

        def _format_action_invocation(self, action):
            if not action.option_strings:
                return super()._format_action_invocation(action)
            default = self._get_default_metavar_for_optional(action)
            values = self._format_args(action, default)
            opts = action.option_strings
            short = [arg for arg in opts if not arg.startswith('--')]
            long = [arg for arg in opts if arg.startswith('--')]
            return '%*s%s%s %s' % (
                3, ', '.join(short), ', ' if short else '  ', ', '.join(long),
                values)

    class HexAction(argparse.Action):
        def __call__(self, parser, ns, values, option_string=None):
            setattr(ns, self.dest, int(values, 16))

    fmt = lambda prog: CustomHelpFormatter(prog)
    parser = argparse.ArgumentParser(
        description='Preview given file as raw pixels.', formatter_class=fmt)

    parser.add_argument('file', metavar='FILE', help='file to view')
    parser.add_argument(
        '--flip', default=False, action='store_true',
        help='flip the preview vertically')
    parser.add_argument(
        '--brightness', metavar='MULTIPLIER', default=50.0, type=float,
        help='sets brightness adjustment')
    parser.add_argument(
        '-f', '--format', metavar='FORMAT',
        choices=PixelFormats.get_short_names(), default='BGRA8888x',
        help='set the pixel format of the preview')
    parser.add_argument(
        '--width', metavar='NUM', type=int, default=800,
        help='set the preview width')
    parser.add_argument(
        '--height', metavar='NUM', type=int, default=600,
        help='set the preview height')
    parser.add_argument(
        '-a', '--address', metavar='HEXNUM', action=HexAction, default=0,
        help='set the position within the file to start preview at')

    return parser.parse_args()

def plain_main():
    class PlainWindowAdapter(GenericWindowAdapter):
        def ask_address(self, address):
            text, ok = QtGui.QInputDialog.getText(
                None,
                'Input Dialog',
                'Please enter an hexadecimal address:')
            if ok:
                return int(text, 16)
            return None

        def ask_file(self):
            return QtGui.QFileDialog.getSaveFileName(
                None, 'Save the image as...', None, '*.png')

    class MainWindow(QtGui.QMainWindow):
        def __init__(self, params):
            super(MainWindow, self).__init__()

            adapter = PlainWindowAdapter(params)
            ShortcutManager(adapter).register(self)

            layout = adapter.createLayout()
            central_widget = QtGui.QWidget(self)
            central_widget.setLayout(layout)
            self.setCentralWidget(central_widget)
            adapter.draw()

    args = parse_args()
    params = RendererParams()
    params.reader = FileReader(args.file)
    params.format = PixelFormats.from_short_name(args.format)
    params.width = args.width
    params.height = args.height
    params.address = args.address
    params.flip = args.flip
    params.brightness = args.brightness

    app = QtGui.QApplication(sys.argv)
    win = MainWindow(params)
    win.show()
    app.exec_()

def ida_main():
    class ImagePreviewPlugin(idaapi.plugin_t):
        flags = 0
        wanted_name = 'Image previewer'
        wanted_hotkey = 'Alt + I'
        comment = 'Preview memory as image'
        help = 'https://github.com/rr-/ida-images'

        def init(self):
            return PLUGIN_OK

        def term(self):
            pass

        def run(self, arg):
            class IdaWindowAdapter(GenericWindowAdapter):
                def ask_address(self, address):
                    return AskAddr(address, 'Please enter an address')

                def ask_file(self):
                    return AskFile(1, '*.png', 'Save the image as...')

            class MainWindow(idaapi.PluginForm):
                def __init__(self, params):
                    super(MainWindow, self).__init__()
                    self.params = params

                def OnCreate(self, form):
                    self.parent = self.FormToPySideWidget(form)

                    adapter = IdaWindowAdapter(params)
                    ShortcutManager(adapter).register(self.parent)

                    layout = adapter.createLayout()
                    self.parent.setLayout(layout)
                    adapter.draw()

            params = RendererParams()
            params.reader = MemoryReader()
            params.format = PixelFormats.GRAY8
            params.width = 800
            params.height = 600
            params.address = params.reader.min_address
            params.flip = False
            params.brightness = 50
            image_preview_form = MainWindow(params)
            image_preview_form.Show('Image preview')

    ImagePreviewPlugin().run(0)

def PLUGIN_ENTRY():
    return ImagePreviewPlugin()

if __name__ == '__main__':
    if has_ida:
        ida_main()
    else:
        plain_main()
