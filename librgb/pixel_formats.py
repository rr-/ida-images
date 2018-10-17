from collections import OrderedDict


class PixelFormats(object):
    GRAY8 = 0
    GRAY1 = 3

    BGR555 = 100
    BGR565 = 110
    BGR888 = 120
    BGRA8888 = 130
    BGRA8888i = 131
    BGRA8888x = 132

    RGB555 = 200
    RGB565 = 210
    RGB888 = 220
    RGBA8888 = 230
    RGBA8888i = 231
    RGBA8888x = 232

    _NAME_MAP = [
        (GRAY1, '1:Image1Bit (1)', 'G1'),
        (GRAY8, '8:Grayscale (8)', 'G8'),

        (BGR555, '16:BGR (5-5-5)', 'BGR555'),
        (BGR565, '16:BGR (5-6-5)', 'BGR565'),
        (BGR888, '24:BGR (8-8-8)', 'BGR888'),
        (BGRA8888, '32:BGRA (8-8-8-8)', 'BGRA8888'),
        (BGRA8888i, '32:BGRa (8-8-8-8)', 'BGRa8888'),
        (BGRA8888x, '32:BGRx (8-8-8-8)', 'BGRx8888'),

        (RGB555, '16:RGB (5-5-5)', 'RGB555'),
        (RGB565, '16:RGB (5-6-5)', 'RGB565'),
        (RGB888, '24:RGB (8-8-8)', 'RGB888'),
        (RGBA8888, '32:RGBA (8-8-8-8)', 'RGBA8888'),
        (RGBA8888i, '32:RGBa (8-8-8-8)', 'RGBa8888'),
        (RGBA8888x, '32:RGBx (8-8-8-8)', 'RGBx8888'),
    ]

    @staticmethod
    def get_short_names():
        return OrderedDict([
            (item[0], item[2])
            for item in PixelFormats._NAME_MAP])

    @staticmethod
    def get_long_names():
        return OrderedDict([
            (item[0], item[1])
            for item in PixelFormats._NAME_MAP])

    @staticmethod
    def from_short_name(fmt):
        for key, item in PixelFormats.get_short_names().items():
            if item == fmt:
                return key
        raise RuntimeError('Unknown pixel format: ' + fmt)
