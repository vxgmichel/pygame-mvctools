"""Provide the base settings class."""

# Imports
import pygame, argparse
from mvctools import xytuple
from mvctools.property import setting, default_setting

# String conversion functions

def bool_to_string(value):
    """Convert a boolean to a string."""
    return {True: 'true', False: 'false'}[value]

def bool_from_string(string):
    """Convert a string to a boolean."""
    if string.lower() in ["1", "t", "true"]:
        return True
    if string.lower() in ["0", "f", "false"]:
        return False
    raise ValueError("not a valid string")

def fullscreen_to_string(value):
    """Convert a boolean to a string."""
    return {True: 'windowed', False: 'fullscreen'}[value]

def fullscreen_from_string(string):
    """Convert a string to a boolean."""
    if string.lower() in ["fullscreen", "full", "1", "t", "true"]:
        return True
    if string.lower() in ["window", "windowed", "0", "f", "false"]:
        return False
    raise ValueError("not a valid string")


# Base settings class
class BaseSettings(object):
    """Base setting class"""

    arg_lst = ['size', 'fps', 'fullscreen']

    def __init__(self, control):
        """Save the control."""
        self.control = control

    # Directories

    @default_setting(cast=str)
    def font_dir(self):
        """Font directory."""
        return "font"

    @default_setting(cast=str)
    def image_dir(self):
        """Image directory."""
        return "image"

    @default_setting(cast=str)
    def sound_dir(self):
        """Sound directory."""
        return "sound"

    # Debug

    @default_setting(cast=float)
    def debug_speed(self):
        """Game speed for debug purposes."""
        return 1.0

    @default_setting(cast=bool,
                     from_string=bool_from_string,
                     to_string=bool_to_string)
    def debug_mode(self):
        """Enable debug mode."""
        return False

    @default_setting(cast=bool,
                     from_string=bool_from_string,
                     to_string=bool_to_string)
    def profile(self):
        """Enable the profiler."""
        return False

    @default_setting(cast=bool,
                     from_string=bool_from_string,
                     to_string=bool_to_string)
    def display_fps(self):
        """Display the frame rate."""
        return False

    # Settings

    @default_setting(cast=int)
    def fps(self):
        """Frame rate in frames per second."""
        return 60

    @default_setting(cast=int)
    def width(self):
        """Width of the screen."""
        return 1280

    @default_setting(cast=int)
    def height(self):
        """Height of the screen."""
        return 720

    @default_setting(cast=bool,
                     from_string=fullscreen_from_string,
                     to_string=fullscreen_to_string)
    def fullscreen(self):
        """Enable fullscreen mode."""
        return False

    @setting(from_string = lambda arg: arg.split('x'),
             to_string   = "{0[0]}x{0[1]}".format)
    def size(self):
        """Size of the screen."""
        return xytuple(self.width, self.height)

    @size.setter
    def size(self, value):
        """Setter for the screen size."""
        self.width, self.height = value

    # Setting to string

    def setting_to_string(self, name):
        """Get the given setting as a string."""
        return getattr(type(self), name).to_string(self)

    # Parse arguments

    def parse_arguments(self, parser):
        """Parse the argments using the given parser."""
        # Loop over settings
        for name in dir(type(self)):
            attr = getattr(type(self), name, None)
            if isinstance(attr, setting):
                # Values
                argname = '--' + name.replace('_', '-')
                metavar = name[:3].upper() if len(name) > 4 else name.upper()
                default = self.setting_to_string(name)
                boolean = attr.cast is bool and not getattr(self, name)
                type_func = lambda value, name=name: setattr(self, name, value)
                if attr.cast: type_func.__name__ = attr.cast.__name__
                # Description
                desc = argparse.SUPPRESS
                if self.arg_lst is None or name in self.arg_lst:
                    desc = attr.__doc__ or ''
                    if desc:
                        desc = desc.split('.')[0]
                        desc = desc[0].lower() + desc[1:]
                    if boolean:
                        desc += " (inactive when omitted)".format(default)
                    else:
                        desc += " (default is {0})".format(default)
                # Boolean property
                if boolean:
                    parser.add_argument(argname,
                                        action="store_true",
                                        default=None,
                                        help=desc)
                # Regular property
                else:
                    parser.add_argument(argname,
                                        metavar=metavar,
                                        default=None,
                                        type=type_func,
                                        help=desc)
        # Apply boolean values
        args = parser.parse_args()
        for key, value in args._get_kwargs():
            if value is not None:
                setattr(self, key, value)
