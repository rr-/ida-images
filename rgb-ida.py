import idaapi
import librgb
from librgb.qt_shims import QtGui  # important for PySide legacy IDA
from librgb.qt_shims import QtWidgets


try:
    MAJOR, MINOR = map(int, idaapi.get_kernel_version().split("."))
except AttributeError:
    MAJOR, MINOR = 6, 6
USING_IDA7API = (MAJOR > 6)
USING_PYQT5 = USING_IDA7API or (MAJOR == 6 and MINOR >= 9)


class DockableShim(object):
    def __init__(self, title):
        self._title = title

        # IDA 7+ Widgets
        if USING_IDA7API:
            import sip
            self._form = idaapi.create_empty_widget(self._title)
            self.widget = sip.wrapinstance(long(self._form), QtWidgets.QWidget)
        # legacy IDA PluginForm's
        else:
            self._form = idaapi.create_tform(self._title, None)
            if USING_PYQT5:
                self.widget = idaapi.PluginForm.FormToPyQtWidget(self._form)
            else:
                self.widget = idaapi.PluginForm.FormToPySideWidget(self._form)

    def show(self):
        if USING_IDA7API:
            flags = (
                idaapi.PluginForm.WOPN_TAB
                | idaapi.PluginForm.WOPN_MENU
                | idaapi.PluginForm.WOPN_RESTORE
                | idaapi.PluginForm.WOPN_PERSIST)
            idaapi.display_widget(self._form, flags)

        # legacy IDA PluginForm's
        else:
            flags = (
                idaapi.PluginForm.FORM_TAB
                | idaapi.PluginForm.FORM_MENU
                | idaapi.PluginForm.FORM_RESTORE
                | idaapi.PluginForm.FORM_PERSIST
                | 0x80)  # idaapi.PluginForm.FORM_QWIDGET
            idaapi.open_tform(self._form, flags)


class ImagePreviewPlugin(idaapi.plugin_t):
    flags = 0
    wanted_name = 'Image previewer'
    wanted_hotkey = 'Alt + I'
    comment = 'Preview memory as image'
    help = 'https://github.com/rr-/ida-images'

    def init(self):
        return idaapi.PLUGIN_OK

    def term(self):
        pass

    def run(self, arg):
        class IdaWindowAdapter(librgb.GenericWindowAdapter):
            def ask_address(self, address):
                return AskAddr(address, 'Please enter an address')

            def ask_file(self):
                return AskFile(1, '*.png', 'Save the image as...')

        image_preview_form = DockableShim('Image preview')

        params = librgb.RendererParams()
        params.readers = [librgb.MemoryReader()]
        params.format = librgb.PixelFormats.GRAY8
        params.width = 800
        params.height = 600
        params.flip = False
        params.brightness = 50

        adapter = IdaWindowAdapter(params)
        shortcut_manager = librgb.ShortcutManager(adapter, params)
        for shortcut, func in shortcut_manager.shortcuts.items():
            adapter.define_shortcut(shortcut, image_preview_form.widget, func)

        layout = adapter.create_layout()
        image_preview_form.widget.setLayout(layout)
        adapter.draw()
        image_preview_form.show()


def PLUGIN_ENTRY():
    return ImagePreviewPlugin()


if __name__ == '__main__':
    ImagePreviewPlugin().run(0)
