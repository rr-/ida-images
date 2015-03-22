# ida-images
Image preview plugin for Ida disassembler.

## Application

I made this plugin to ease finding image decoding routines - I can run some
complex code and see if the memory contains the image I'm looking for
afterwards.

## Features

- Multiple pixel formats to choose from: RGB, BGR, alpha channels, etc.
- Memory exploration made convenient with keyboard shortcuts:
    - <kbd>G</kbd> - go to address
    - <kbd>Ctrl</kbd>+<kbd>&larr;</kbd> - seek to previous memory chunk
    - <kbd>Ctrl</kbd>+<kbd>&rarr;</kbd> - seek to next memory chunk
- Saving as PNG

Additionally, I'm open to feature requests, as long as they won't make the code
too bloated.

## Installation

Either drop the `.py` file in `C:\Program Files (x86)\IDA 6.6\plugins` (or
similar) and then run it via <kbd>Ctrl</kbd>+<kbd>3</kbd>, or run the script
manually with <kbd>Alt</kbd>+<kbd>F9</kbd>.

Note that if you plan on modifying the script, the first option requires you to
restart Ida after making every change, while the second one doesn't.

## Seeing it in action

#### Viewing program code

![A piece of code](https://cloud.githubusercontent.com/assets/1045476/6769003/9be65a98-d088-11e4-8f89-2d6550f1cd37.png)

I have no idea what the gradients are there for, but it's certainly interesting!

#### Viewing actual bitmap

![A bitmap](https://cloud.githubusercontent.com/assets/1045476/6769004/9dbc1812-d088-11e4-8444-4e269dcc3efd.png)

Now all that's left is to localize the exact function that allocated this
segment... and voilà.
