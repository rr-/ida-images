from idaapi import *
from PySide import QtCore, QtGui


class MemoryRange(object):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def length(self):
        return self.end - self.start

    def __str__(self):
        return 'start: %08x end: %08x' % (self.start, self.end)

# Reads continuous memory chunk even if it spans accross multiple segments.
# "Missing" bytes are filled with NULL byte.
class MemoryReader(object):
    @staticmethod
    def read(address, count):
        result = "\x00" * count
        ranges_left = [MemoryRange(address, address + count)]

        segment_count = get_segm_qty()
        valid_memory_ranges = []
        for i in range(segment_count):
            segment = getnseg(i)
            #skip segments with unstable data
            if segment.type == SEG_XTRN:
                continue
            valid_memory_ranges.append(
                MemoryRange(segment.startEA, segment.endEA))

        while len(ranges_left) > 0:
            #get a requested memory range and remove it from the list
            current_range = ranges_left.pop()

            intersection = None
            for memory_range in valid_memory_ranges:
                start = max(current_range.start, memory_range.start)
                end = min(current_range.end, memory_range.end)
                if end > start:
                    intersection = MemoryRange(start, end)
                    break

            #no segment can satisfy any part of requested range
            if intersection is None:
                continue

            chunk = GetManyBytes(
                intersection.start,
                intersection.end - intersection.start)
            if chunk is None:
                print 'Some bytes are unreadable in %s..%s' % (
                    atoa(intersection.start), atoa(intersection.end))
                continue

            result = \
                result[0:intersection.start - address] \
                + chunk \
                + result[intersection.end - address:]
            assert(len(result) == count)

            #if necessary, enqueue ranges unsatisfied by chosen mem segment
            range1 = MemoryRange(current_range.start, intersection.start)
            range2 = MemoryRange(intersection.end, current_range.end)
            if range1.length > 0:
                ranges_left.append(range1)
            if range2.length > 0:
                ranges_left.append(range2)

        return result

class PixelFormats(object):
    RGB888 = 'RGB (8-8-8)'
    #RGB565 = 'RGB (5-6-5)'
    #RGBA8888 = 'RGBA (8-8-8-8)'
    #RGBA4444 = 'RGBA (4-4-4-4)'
    #RGBA5658 = 'RGBA (5-6-5-8)'
    ARGB8888 = 'ARGB (8-8-8-8)'
    #ARGB4444 = 'ARGB (4-4-4-4)'
    #ARGB5658 = 'ARGB (5-6-5-8)'
    BGR888 = 'BGR (8-8-8)'
    #BGR565 = 'BGR (5-6-5)'
    #BGRA8888 = 'BGRA (8-8-8-8)'
    #BGRA4444 = 'BGRA (4-4-4-4)'
    #BGRA5658 = 'BGRA (5-6-5-8)'
    ABGR8888 = 'ABGR (8-8-8-8)'
    #ABGR4444 = 'ABGR (4-4-4-4)'
    #ABGR5658 = 'ABGR (5-6-5-8)'
    GRAY8 = 'Grayscale (8)'

class DrawParameters(object):
    def __init__(self):
        self.format = PixelFormats.RGB888
        self.width = 800
        self.height = 600
        self.address = GetEntryPoint(1)

class Drawer(object):
    FORMAT_MAP = \
    {
        PixelFormats.RGB888:   (3, QtGui.QImage.Format_RGB888, False),
        PixelFormats.ARGB8888: (4, QtGui.QImage.Format_ARGB32, False),
        PixelFormats.BGR888:   (3, QtGui.QImage.Format_RGB888, True),
        PixelFormats.ABGR8888: (4, QtGui.QImage.Format_ARGB32, True),
        PixelFormats.GRAY8:    (1, QtGui.QImage.Format_Indexed8, False),
    }

    def __init__(self, parameters):
        self.parameters = parameters

    def getPixmap(self):
        bytes, qt_format, swap_rgb = self.getBytes()
        image = QtGui.QImage(
            bytes,
            self.parameters.width,
            self.parameters.height,
            qt_format)
        if swap_rgb:
            image = image.rgbSwapped()
        pixmap = QtGui.QPixmap()
        pixmap.convertFromImage(image)
        return pixmap

    def getBytes(self):
        if self.parameters.format not in self.FORMAT_MAP:
            raise RuntimeError('Not implemented')

        span, qt_format, swap_rgb = self.FORMAT_MAP[self.parameters.format]
        byte_count = self.parameters.width * self.parameters.height * span
        bytes = MemoryReader.read(self.parameters.address, byte_count)
        assert(bytes is not None)
        return bytes, qt_format, swap_rgb

class ImagePreviewForm(PluginForm):
    def OnCreate(self, form):
        self.parameters = DrawParameters()
        self.parent = self.FormToPySideWidget(form)
        self.populateForm()
        self.draw()

    def populateForm(self):
        layout = QtGui.QVBoxLayout()

        toolbar = QtGui.QHBoxLayout()
        self.addFormatBox(toolbar)
        self.addWidthBox(toolbar)
        self.addHeightBox(toolbar)
        self.addAddressLabel(toolbar)
        self.addGotoButton(toolbar)
        self.addRedrawButton(toolbar)
        self.addSaveButton(toolbar)
        toolbar.addStretch()

        self.addShortcuts()

        self.image_label = QtGui.QLabel()
        scroll_area = QtGui.QScrollArea()
        scroll_area.setWidget(self.image_label)
        scroll_area.setWidgetResizable(True)
        layout.addLayout(toolbar)
        layout.addWidget(scroll_area)
        self.parent.setLayout(layout)

    def addShortcuts(self):
        QtGui.QShortcut(
            QtGui.QKeySequence('G'),
            self.parent,
            self.changeAddress,
            context=QtCore.Qt.ApplicationShortcut)

        QtGui.QShortcut(
            QtGui.QKeySequence('Ctrl+left'),
            self.parent,
            self.goLeft,
            context=QtCore.Qt.ApplicationShortcut)

        QtGui.QShortcut(
            QtGui.QKeySequence('Ctrl+right'),
            self.parent,
            self.goRight,
            context=QtCore.Qt.ApplicationShortcut)

    def addFormatBox(self, layout):
        layout.addWidget(QtGui.QLabel('Format:'))
        format_box = QtGui.QComboBox()
        formats = [attr
            for attr in dir(PixelFormats())
            if not callable(attr) and not attr.startswith("__")]
        for format in formats:
            text = getattr(PixelFormats, format)
            format_box.addItem(text, text)
        format_box.setCurrentIndex(format_box.findData(self.parameters.format))
        format_box.currentIndexChanged.connect(self.formatChanged)
        self.format_box = format_box
        layout.addWidget(format_box)

    def addWidthBox(self, layout):
        layout.addWidget(QtGui.QLabel('Width:'))
        width_box = QtGui.QSpinBox()
        width_box.setMinimum(1)
        width_box.setMaximum(2000)
        width_box.setValue(self.parameters.width)
        width_box.valueChanged.connect(self.widthChanged)
        layout.addWidget(width_box)

    def addHeightBox(self, layout):
        layout.addWidget(QtGui.QLabel('Height:'))
        height_box = QtGui.QSpinBox()
        height_box.setMinimum(1)
        height_box.setMaximum(2000)
        height_box.setValue(self.parameters.height)
        height_box.valueChanged.connect(self.heightChanged)
        layout.addWidget(height_box)

    def addGotoButton(self, layout):
        goto_button = QtGui.QPushButton('&Go to address... [G]')
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
        redraw_button.clicked.connect(self.redraw)
        layout.addWidget(redraw_button)

    def widthChanged(self, newWidth):
        self.parameters.width = newWidth
        self.draw()

    def heightChanged(self, newHeight):
        self.parameters.height = newHeight
        self.draw()

    def formatChanged(self, newFormatIndex):
        self.parameters.format = \
            self.format_box.itemData(self.format_box.currentIndex())
        self.draw()

    def changeAddress(self):
        address = AskAddr(self.parameters.address, 'Please enter an address')
        if address is not None:
            self.parameters.address = address
            self.draw()

    def goLeft(self):
        self.parameters.address -= self.getShownByteCount()
        self.parameters.address = max(self.parameters.address, MinEA())
        self.draw()

    def goRight(self):
        self.parameters.address += self.getShownByteCount()
        self.parameters.address = min(self.parameters.address, MaxEA())
        self.draw()

    def redraw(self):
        self.draw()

    def save(self):
        path = AskFile(1, '*.png', 'Save the image as...')
        if path is not None:
            self.image_label.pixmap().save(path, 'PNG')

    def draw(self):
        self.address_label.setText(atoa(self.parameters.address))
        pixmap = Drawer(self.parameters).getPixmap()
        self.image_label.setPixmap(pixmap)

    def getShownByteCount(self):
        bytes = Drawer.FORMAT_MAP[self.parameters.format][0]
        return self.parameters.width * self.parameters.height * bytes

class ImagePreviewPlugin(plugin_t):
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
        image_preview_form = ImagePreviewForm()
        image_preview_form.Show('Image preview')

def PLUGIN_ENTRY():
    return ImagePreviewPlugin()

if __name__ == '__main__':
    PLUGIN_ENTRY().run(0)
