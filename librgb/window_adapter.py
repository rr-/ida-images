from librgb.pixel_formats import PixelFormats
from librgb.qt_shims import QtCore, QtGui, QtWidgets
from librgb.renderer import Renderer


class GenericWindowAdapter(object):
    def __init__(self, params):
        self.params = params
        self.upper_toolbar = None
        self.lower_toolbar = None
        self.scroll_are = None
        self.format_box = None
        self.brightness_box = None
        self.width_box = None
        self.height_box = None
        self.address_label = None
        self.image_label = None
        self.flip_checkbox = None

    def create_layout(self):
        layout = QtWidgets.QVBoxLayout()

        upper_toolbar = QtWidgets.QHBoxLayout()
        self.add_format_box(upper_toolbar)
        self.add_size_boxes(upper_toolbar)
        upper_toolbar.addStretch()
        self.add_flip_checkbox(upper_toolbar)
        self.add_brightness_box(upper_toolbar)

        lower_toolbar = QtWidgets.QHBoxLayout()
        self.add_address_label(lower_toolbar)
        lower_toolbar.addStretch()
        self.add_goto_button(lower_toolbar)
        self.add_redraw_button(lower_toolbar)
        self.add_save_button(lower_toolbar)

        self.image_label = QtWidgets.QLabel()
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidget(self.image_label)
        scroll_area.setWidgetResizable(True)
        layout.addLayout(upper_toolbar)
        layout.addWidget(scroll_area)
        layout.addLayout(lower_toolbar)

        return layout

    def add_format_box(self, layout):
        self.format_box = QtWidgets.QComboBox()
        for key, text in PixelFormats.get_long_names().items():
            self.format_box.addItem(text, key)
        self.format_box.currentIndexChanged.connect(self.format_changed)
        layout.addWidget(self.format_box)

    def add_flip_checkbox(self, layout):
        self.flip_checkbox = QtWidgets.QCheckBox()
        self.flip_checkbox.stateChanged.connect(self.flip_changed)
        self.flip_checkbox.setText("Flip vertically")
        layout.addWidget(self.flip_checkbox)

    def add_brightness_box(self, layout):
        layout.addWidget(QtWidgets.QLabel("Brightness:"))
        self.brightness_box = QtWidgets.QDoubleSpinBox()
        self.brightness_box.setMinimum(0.0)
        self.brightness_box.setMaximum(100.0)
        self.brightness_box.valueChanged.connect(self.brightness_changed)
        layout.addWidget(self.brightness_box)

    def add_size_boxes(self, layout):
        self.width_box = QtWidgets.QSpinBox()
        self.width_box.setMinimum(1)
        self.width_box.setMaximum(4096)
        self.width_box.valueChanged.connect(self.width_changed)
        layout.addWidget(self.width_box)
        layout.addWidget(QtWidgets.QLabel("x"))
        self.height_box = QtWidgets.QSpinBox()
        self.height_box.setMinimum(1)
        self.height_box.setMaximum(4096)
        self.height_box.valueChanged.connect(self.height_changed)
        layout.addWidget(self.height_box)

    def add_goto_button(self, layout):
        goto_button = QtWidgets.QPushButton("&Go to... [G]")
        goto_button.setDefault(True)
        goto_button.clicked.connect(self.change_address)
        layout.addWidget(goto_button)

    def add_address_label(self, layout):
        address_label1 = QtWidgets.QLabel("Address:")
        address_label2 = QtWidgets.QLabel("...")
        layout.addWidget(address_label1)
        layout.addWidget(address_label2)
        self.address_label = address_label2

    def add_save_button(self, layout):
        save_button = QtWidgets.QPushButton("&Save...")
        save_button.clicked.connect(self.save)
        layout.addWidget(save_button)

    def add_redraw_button(self, layout):
        redraw_button = QtWidgets.QPushButton("&Redraw")
        redraw_button.clicked.connect(self.draw)
        layout.addWidget(redraw_button)

    def define_shortcut(self, shortcut, widget, func):
        # pylint: disable=unnecessary-lambda
        # shortcuts don't get triggered if the func isn't wrapped in a lambda
        QtWidgets.QShortcut(
            QtGui.QKeySequence(shortcut), widget, lambda: func()
        )

    def flip_changed(self, state):
        self.params.flip = state == QtCore.Qt.Checked

    def brightness_changed(self, value):
        self.params.brightness = value

    def width_changed(self, value):
        self.params.width = value

    def height_changed(self, value):
        self.params.height = value

    def format_changed(self, _index):
        self.params.format = self.format_box.itemData(
            self.format_box.currentIndex()
        )

    def change_address(self):
        address = self.ask_address(self.params.reader.address)
        if address is not None:
            self.params.reader.address = address
            self.params.fire_redraw()

    def save(self):
        path = self.ask_file()
        if path is not None:
            self.image_label.pixmap().save(path, "PNG")

    def draw(self):
        self.params.draw_cb = None

        if self.params.reader is None:
            self.address_label.setText("UNAVAILABLE")
        else:
            self.address_label.setText(self.params.reader.address_text)
        self.flip_checkbox.setCheckState(
            QtCore.Qt.Checked if self.params.flip else QtCore.Qt.Unchecked
        )
        self.brightness_box.setValue(self.params.brightness)
        self.width_box.setValue(self.params.width)
        self.height_box.setValue(self.params.height)
        self.format_box.setCurrentIndex(
            self.format_box.findData(self.params.format)
        )

        pixmap = Renderer(self.params).get_pixmap()
        self.image_label.setPixmap(pixmap)

        self.params.draw_cb = self.draw

    def ask_address(self, address):
        text, confirmed = QtWidgets.QInputDialog.getText(
            None,
            "Input Dialog",
            "Please enter an hexadecimal address:",
            text="%X" % address,
        )
        if confirmed:
            return int(text, 16)
        return None

    def ask_file(self):
        ret, _ = QtWidgets.QFileDialog.getSaveFileName(
            caption="Save the image as...", filter="*.png"
        )
        return ret
