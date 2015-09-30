class PixelFormats(object):
    RGB888    = 'RGB (8-8-8)'
    RGB565    = 'RGB (5-6-5)'
    RGBA8888  = 'RGBA (8-8-8-8)'
    RGBA8888i = 'RGBA (8-8-8-8, invert alpha)'
    RGBA8888x = 'RGBA (8-8-8-8, ignore alpha)'
    RGBA5658  = 'RGBA (5-6-5-8)'
    RGBA5658i = 'RGBA (5-6-5-8, invert alpha)'
    RGBA5658  = 'RGBA (5-6-5-8)'
    BGR888    = 'BGR (8-8-8)'
    BGR565    = 'BGR (5-6-5)'
    BGRA8888  = 'BGRA (8-8-8-8)'
    BGRA8888i = 'BGRA (8-8-8-8, invert alpha)'
    BGRA8888x = 'BGRA (8-8-8-8, ignore alpha)'
    BGRA5658  = 'BGRA (5-6-5-8)'
    BGRA5658i = 'BGRA (5-6-5-8, invert alpha)'
    BGRA5658  = 'BGRA (5-6-5-8)'
    GRAY8     = 'Grayscale (8)'

    @staticmethod
    def get_short_names():
        return [v for v in dir(PixelFormats) if not '_' in v]

    @staticmethod
    def get_long_names():
        short_names = PixelFormats.get_short_names()
        return [PixelFormats.from_short_name(text) for text in short_names]

    @staticmethod
    def from_short_name(text):
        return getattr(PixelFormats, text)
