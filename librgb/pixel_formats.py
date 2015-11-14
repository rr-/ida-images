from collections import OrderedDict
from enum import Enum


class PixelFormats(object):
    GRAY8 = 0

    BGR888 = 10
    BGRA8888 = 11
    BGRA8888i = 12
    BGRA8888x = 13
    BGR565 = 14

    RGB888 = 20
    RGBA8888 = 21
    RGBA8888i = 22
    RGBA8888x = 23
    RGB565 = 24

name_map = [
    (PixelFormats.GRAY8,     '8:Grayscale (8)',     'G8'),

    (PixelFormats.BGR565,    '16:BGR (5-6-5)',      'BGR565'),
    (PixelFormats.BGR888,    '24:BGR (8-8-8)',      'BGR888'),
    (PixelFormats.BGRA8888,  '32:BGRA (8-8-8-8)',   'BGRA8888'),
    (PixelFormats.BGRA8888i, '32:BGRa (8-8-8-8)',   'BGRa8888'),
    (PixelFormats.BGRA8888x, '32:BGRx (8-8-8-8)',   'BGRx8888'),

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
