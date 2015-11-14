from collections import OrderedDict
from enum import Enum


class PixelFormats(object):
    GRAY8 = 0

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

name_map = [
    (PixelFormats.GRAY8,     '8:Grayscale (8)',     'G8'),

    (PixelFormats.BGR555,    '16:BGR (5-5-5)',      'BGR555'),
    (PixelFormats.BGR565,    '16:BGR (5-6-5)',      'BGR565'),
    (PixelFormats.BGR888,    '24:BGR (8-8-8)',      'BGR888'),
    (PixelFormats.BGRA8888,  '32:BGRA (8-8-8-8)',   'BGRA8888'),
    (PixelFormats.BGRA8888i, '32:BGRa (8-8-8-8)',   'BGRa8888'),
    (PixelFormats.BGRA8888x, '32:BGRx (8-8-8-8)',   'BGRx8888'),

    (PixelFormats.RGB555,    '16:RGB (5-5-5)',      'RGB555'),
    (PixelFormats.RGB565,    '16:RGB (5-6-5)',      'RGB565'),
    (PixelFormats.RGB888,    '24:RGB (8-8-8)',      'RGB888'),
    (PixelFormats.RGBA8888,  '32:RGBA (8-8-8-8)',   'RGBA8888'),
    (PixelFormats.RGBA8888i, '32:RGBa (8-8-8-8)',   'RGBa8888'),
    (PixelFormats.RGBA8888x, '32:RGBx (8-8-8-8)',   'RGBx8888'),
]

def get_short_names():
    return OrderedDict([(v[0], v[2]) for v in name_map])

def get_long_names():
    return OrderedDict([(v[0], v[1]) for v in name_map])

def from_short_name(fmt):
    for k, v in PixelFormats.get_short_names().items():
        if v == fmt:
            return k
    raise RuntimeError('Unknown pixel format: ' + fmt)

PixelFormats.get_short_names = get_short_names
PixelFormats.get_long_names = get_long_names
PixelFormats.from_short_name = from_short_name
