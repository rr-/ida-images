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
            assert(chunk is not None)

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

class DrawParameters(object):
    def __init__(self):
        self.width = 800
        self.height = 600
        self.address = GetEntryPoint(1)

class ImagePreviewForm(PluginForm):
    def OnCreate(self, form):
        self.parameters = DrawParameters()
        self.parent = self.FormToPySideWidget(form)
        self.populateForm()
        self.draw()

    def populateForm(self):
        layout = QtGui.QVBoxLayout()
        toolbar = QtGui.QHBoxLayout()
        self.addWidthBox(toolbar)
        self.addHeightBox(toolbar)
        self.addGotoButton(toolbar)
        self.image_label = QtGui.QLabel()
        layout.addLayout(toolbar)
        layout.addWidget(self.image_label)
        self.parent.setLayout(layout)

    def addWidthBox(self, layout):
        width_box = QtGui.QSpinBox()
        width_box.setMinimum(1)
        width_box.setMaximum(2000)
        width_box.setValue(self.parameters.width)
        width_box.valueChanged.connect(self.widthChanged)
        layout.addWidget(width_box)

    def addHeightBox(self, layout):
        height_box = QtGui.QSpinBox()
        height_box.setMinimum(1)
        height_box.setMaximum(2000)
        height_box.setValue(self.parameters.height)
        height_box.valueChanged.connect(self.heightChanged)
        layout.addWidget(height_box)

    def addGotoButton(self, layout):
        button_goto = QtGui.QPushButton('&Go to address... [G]')
        button_goto.setDefault(True)
        button_goto.clicked.connect(self.choose)
        layout.addWidget(button_goto)

        QtGui.QShortcut(
            QtGui.QKeySequence('G'),
            self.parent,
            self.choose,
            context=QtCore.Qt.ApplicationShortcut)

    def widthChanged(self, newWidth):
        self.parameters.width = newWidth
        self.draw()

    def heightChanged(self, newHeight):
        self.parameters.height = newHeight
        self.draw()

    def choose(self):
        address = AskAddr(self.parameters.address, 'Please enter an address')
        if address is not None:
            self.parameters.address = address
            self.draw()

    def draw(self):
        channels = 4
        format = QtGui.QImage.Format_RGB888
        byte_count = self.parameters.width * self.parameters.height * channels
        bytes = MemoryReader.read(self.parameters.address, byte_count)
        assert(bytes is not None)

        pixmap = QtGui.QPixmap()
        pixmap.convertFromImage(QtGui.QImage(
            bytes,
            self.parameters.width,
            self.parameters.height,
            format))

        self.image_label.setPixmap(pixmap)

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
