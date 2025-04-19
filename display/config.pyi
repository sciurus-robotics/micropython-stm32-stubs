
import st7789

def config(rotation=0, buffer_size=0, options=0) ->  st7789.ST7789:
    """Configure the T-DONGLE-S3 display using a custom_init and
    custom_rotations since the display is st7735.

    The custom_init is a list of commands to send to the display during the init() metehod.
    The list contains tuples with a bytes object, optionally followed by a delay specified in ms.
    The first byte of the bytes object contains the command to send optionally followed by data bytes.
    """
    ...
