#!/usr/bin/python3
from PySide import QtCore, QtGui
import idaapi
import librgb


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

        class MainWindow(idaapi.PluginForm):
            def __init__(self, params):
                super(MainWindow, self).__init__()
                self.params = params

            def OnCreate(self, form):
                self.parent = self.FormToPySideWidget(form)

                adapter = IdaWindowAdapter(params)
                shortcut_manager = librgb.ShortcutManager(adapter, self.params)
                shortcut_manager.register(self.parent)

                layout = adapter.createLayout()
                self.parent.setLayout(layout)
                adapter.draw()

        params = librgb.RendererParams()
        params.reader = librgb.MemoryReader()
        params.format = librgb.PixelFormats.GRAY8
        params.width = 800
        params.height = 600
        params.address = params.reader.min_address
        params.flip = False
        params.brightness = 50
        image_preview_form = MainWindow(params)
        image_preview_form.Show('Image preview')

def PLUGIN_ENTRY():
    return ImagePreviewPlugin()

if __name__ == '__main__':
    ImagePreviewPlugin().run(0)
