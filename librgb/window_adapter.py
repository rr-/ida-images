from .pixel_formats import PixelFormats
from .renderer import Renderer
try:
    from PySide import QtCore, QtGui
except ImportError:
    from PyQt4 import QtCore, QtGui


class GenericWindowAdapter(object):
    def __init__(self, params):
        self.params = params

    def create_layout(self):
        layout = QtGui.QVBoxLayout()

        upper_toolbar = QtGui.QHBoxLayout()
        self.add_format_box(upper_toolbar)
        self.add_size_boxes(upper_toolbar)
        upper_toolbar.addStretch()
        self.add_flip_checkbox(upper_toolbar)
        self.add_brightness_box(upper_toolbar)

        lower_toolbar = QtGui.QHBoxLayout()
        self.add_address_label(lower_toolbar)
        lower_toolbar.addStretch()
        self.add_goto_button(lower_toolbar)
        self.add_redraw_button(lower_toolbar)
        self.add_save_button(lower_toolbar)

        self.image_label = QtGui.QLabel()
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        scroll_area = QtGui.QScrollArea()
        scroll_area.setWidget(self.image_label)
        scroll_area.setWidgetResizable(True)
        layout.addLayout(upper_toolbar)
        layout.addWidget(scroll_area)
        layout.addLayout(lower_toolbar)

        return layout

    def add_format_box(self, layout):
        self.format_box = QtGui.QComboBox()
        for text in PixelFormats.get_long_names():
            self.format_box.addItem(text, text)
        self.format_box.currentIndexChanged.connect(self.format_changed)
        layout.addWidget(self.format_box)

    def add_flip_checkbox(self, layout):
        self.flip_checkbox = QtGui.QCheckBox()
        self.flip_checkbox.stateChanged.connect(self.flip_changed)
        self.flip_checkbox.setText('Flip vertically')
        layout.addWidget(self.flip_checkbox)

    def add_brightness_box(self, layout):
        layout.addWidget(QtGui.QLabel('Brightness:'))
        self.brightness_box = QtGui.QDoubleSpinBox()
        self.brightness_box.setMinimum(0.0)
        self.brightness_box.setMaximum(100.0)
        self.brightness_box.valueChanged.connect(self.brightness_changed)
        layout.addWidget(self.brightness_box)

    def add_size_boxes(self, layout):
        self.width_box = QtGui.QSpinBox()
        self.width_box.setMinimum(1)
        self.width_box.setMaximum(4096)
        self.width_box.valueChanged.connect(self.width_changed)
        layout.addWidget(self.width_box)
        layout.addWidget(QtGui.QLabel('x'))
        self.height_box = QtGui.QSpinBox()
        self.height_box.setMinimum(1)
        self.height_box.setMaximum(4096)
        self.height_box.valueChanged.connect(self.height_changed)
        layout.addWidget(self.height_box)

    def add_goto_button(self, layout):
        goto_button = QtGui.QPushButton('&Go to... [G]')
        goto_button.setDefault(True)
        goto_button.clicked.connect(self.change_address)
        layout.addWidget(goto_button)

    def add_address_label(self, layout):
        address_label1 = QtGui.QLabel('Address:')
        address_label2 = QtGui.QLabel('...')
        layout.addWidget(address_label1)
        layout.addWidget(address_label2)
        self.address_label = address_label2

    def add_save_button(self, layout):
        save_button = QtGui.QPushButton('&Save...')
        save_button.clicked.connect(self.save)
        layout.addWidget(save_button)

    def add_redraw_button(self, layout):
        redraw_button = QtGui.QPushButton('&Redraw')
        redraw_button.clicked.connect(self.draw)
        layout.addWidget(redraw_button)


    def flip_changed(self, state):
        self.params.flip = state == QtCore.Qt.Checked

    def brightness_changed(self, value):
        self.params.brightness = value

    def width_changed(self, value):
        self.params.width = value

    def height_changed(self, value):
        self.params.height = value

    def format_changed(self, index):
        self.params.format = \
            self.format_box.itemData(self.format_box.currentIndex())


    def change_address(self):
        address = self.ask_address(self.params.reader.address)
        if address is not None:
            self.params.reader.address = address
            self.params.fire_redraw()

    def save(self):
        path = self.ask_file()
        if path is not None:
            self.image_label.pixmap().save(path, 'PNG')

    def draw(self):
        self.params.draw_cb = None

        if self.params.reader is None:
            self.address_label.setText('UNAVAILABLE')
        else:
            self.address_label.setText(
                self.params.reader.address_text)
        self.flip_checkbox.setCheckState(
            QtCore.Qt.Checked if self.params.flip else QtCore.Qt.Unchecked)
        self.brightness_box.setValue(self.params.brightness)
        self.width_box.setValue(self.params.width)
        self.height_box.setValue(self.params.height)
        self.format_box.setCurrentIndex(
            self.format_box.findData(self.params.format))

        pixmap = Renderer(self.params).get_pixmap()
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
