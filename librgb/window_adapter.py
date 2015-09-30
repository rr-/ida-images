from .pixel_formats import PixelFormats
from .renderer import Renderer
try:
    from PySide import QtCore, QtGui
except ImportError:
    from PyQt4 import QtCore, QtGui


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

        self.address_label.setText(
            self.params.reader.translate_address(self.params.address))
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

