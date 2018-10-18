from librgb.qt_shims import QtGui
from librgb.pixel_formats import PixelFormats

try:
    import numpy
    HAS_NUMPY = True
except ImportError:
    print('[librgb] Brightness adjustment will be slow without numpy')
    HAS_NUMPY = False


_FORMAT_MAP = {
    PixelFormats.GRAY1MSB: (1, QtGui.QImage.Format_Mono, False, False),
    PixelFormats.GRAY1LSB: (1, QtGui.QImage.Format_MonoLSB, False, False),
    PixelFormats.GRAY8: (8, QtGui.QImage.Format_Indexed8, False, False),

    PixelFormats.RGB555: (16, QtGui.QImage.Format_RGB555, True, False),
    PixelFormats.RGB565: (16, QtGui.QImage.Format_RGB16, True, False),
    PixelFormats.RGB888: (24, QtGui.QImage.Format_RGB888, True, False),
    PixelFormats.RGBA8888: (32, QtGui.QImage.Format_ARGB32, True, False),
    PixelFormats.RGBA8888i: (32, QtGui.QImage.Format_ARGB32, True, True),
    PixelFormats.RGBA8888x: (32, QtGui.QImage.Format_RGB32, True, False),

    PixelFormats.BGR555: (16, QtGui.QImage.Format_RGB555, False, False),
    PixelFormats.BGR565: (16, QtGui.QImage.Format_RGB16, False, False),
    PixelFormats.BGR888: (24, QtGui.QImage.Format_RGB888, False, False),
    PixelFormats.BGRA8888: (32, QtGui.QImage.Format_ARGB32, False, False),
    PixelFormats.BGRA8888i: (32, QtGui.QImage.Format_ARGB32, False, True),
    PixelFormats.BGRA8888x: (32, QtGui.QImage.Format_RGB32, False, False),
}


class Renderer(object):
    def __init__(self, params):
        self.params = params

    @staticmethod
    def get_bit_count(pixel_format):
        return _FORMAT_MAP[pixel_format][0]

    def get_pixmap(self):
        params = self.params
        reader = self.params.reader
        if reader is None:
            return QtGui.QPixmap()

        if params.format not in _FORMAT_MAP:
            raise NotImplementedError()

        bits, qt_format, swap_rgb, invert_alpha = \
            _FORMAT_MAP[params.format]

        stride = (params.width * bits) // 8
        data_size = params.height * stride

        data = reader.get_padded_bytes(data_size)
        assert data is not None
        assert len(data) == data_size

        if params.flip:
            output = b''
            for y in range(params.height):
                y2 = params.height - 1 - y
                output += data[y2 * stride:(y2 + 1) * stride]
            data = output

        if params.brightness != 50.0:
            # param   multiplier
            # 0       0 = 2^(-8)
            # 50      1 = 2^0
            # 100     256 = 2^8
            multiplier = 2 ** ((params.brightness - 50) / (50 / 8))
            if HAS_NUMPY:
                arr = numpy.fromstring(data, dtype=numpy.uint8)
                arr = arr.astype(dtype=numpy.float)
                arr *= multiplier
                arr = arr.clip(0, 255)
                arr = arr.astype(dtype=numpy.uint8)
                data = arr.tobytes()
            else:
                output = bytearray(data)
                for i in range(len(data)):
                    output[i] = max(min(int(output[i] * multiplier), 0xFF), 0)
                data = output

        image = QtGui.QImage(
            data,
            params.width,
            params.height,
            stride,
            qt_format)
        assert len(data) == image.byteCount()

        if swap_rgb:
            image = image.rgbSwapped()
        if invert_alpha:
            image.invertPixels(QtGui.QImage.InvertRgba)
            image.invertPixels(QtGui.QImage.InvertRgb)

        # Creating pixmap crashes for RGB32?
        if qt_format == QtGui.QImage.Format_RGB32:
            image = image.convertToFormat(QtGui.QImage.Format_RGB888)

        pixmap = QtGui.QPixmap()
        pixmap.convertFromImage(image)
        return pixmap
