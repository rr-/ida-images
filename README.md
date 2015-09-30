# ida-images
Image preview plugin for Ida disassembler.

## Application

I made this plugin to ease finding image decoding routines - I can run some
complex code and see if the memory contains the image I'm looking for
afterwards.

## Features

- CLI frontend for analyzing standalone files
- Multiple pixel formats to choose from: RGB, BGR, alpha channels, etc.
- Memory exploration made convenient with keyboard shortcuts:
    - <kbd>G</kbd> - go to address
    - <kbd>Ctrl</kbd>+<kbd>&larr;</kbd> - seek to previous memory chunk
    - <kbd>Ctrl</kbd>+<kbd>&rarr;</kbd> - seek to next memory chunk
- Saving as PNG
- Adjusting brightness (useful for searching for images using palettes)
- Flipping vertically (useful for analyzing images using BMP-like layout)

Additionally, I'm open to feature requests, as long as they won't make the code
too bloated.

## Installation

Either drop the `rgb-ida.py` file and `librgb` directory in `C:\Program Files
(x86)\IDA 6.6\plugins` (or similar) and then run it via
<kbd>Ctrl</kbd>+<kbd>3</kbd>, or run the script manually with
<kbd>Alt</kbd>+<kbd>F9</kbd>. The other file, `./rgb`, is a CLI frontend that
can be used outside Ida and analyzes files rather than process memory.

## Seeing it in action

#### Viewing program code

![A piece of code](https://cloud.githubusercontent.com/assets/1045476/10188909/5caf5f88-6763-11e5-9398-eae1df05b941.png)

I have no idea what the gradients are there for, but it's certainly
interesting!

![Are you LZSS?](https://cloud.githubusercontent.com/assets/1045476/10188952/9f488f36-6763-11e5-91cf-76fd63d47c0d.png)

More mysterious data.

#### Viewing actual bitmap

![A bitmap](https://cloud.githubusercontent.com/assets/1045476/10188916/65e391be-6763-11e5-8388-967cde0c7c6e.png)

Now all that's left is to localize the exact function that allocated this
segment... and voilà.
