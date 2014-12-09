"""Module with useful classes and functions."""

# Imports
import operator
from math import ceil
from fractions import gcd
from functools import wraps
from weakref import WeakKeyDictionary
from collections import namedtuple, defaultdict
from pygame import Color, Rect


# XY namedtuple
class xytuple(namedtuple("xytuple",("x","y"))):
    """Tuple for x,y coordinates and their transformations.

    This class supports the following operators:
     - addition and inplace addition (+, +=)
     - substraction and inplace substraction (-, -=)
     - multiplication and inplace multiplication (* , * =)
     - division and inplace division (/, /=)

    These are all term-to-term operations.
    Hence, the argument has two be a two-elements iterable.
    They all return an xytuple.

    Also, the absolute value operation is supported (abs).
    It returned a float corrsponding to the norm of the coordinates.

    To apply a specific function on both coordinates, use the method map.
    It returns an xytuple.
    """

    def __new__(cls, x, y=None):
        """Create a new xytuple."""
        if y is None: x, y = x
        return super(xytuple, cls).__new__(cls, x, y)

    def map(self, func, *args):
        """Map the coordinates with the given function a return an xytuple."""
        return xytuple(map(func, self, *args))

    __add__ = __iadd__ = lambda self, it: self.map(operator.add, it)
    __add__.__doc__ = """Add a 2-elements iterable and return an xytuple.
                      """
    __sub__ = __isub__ = lambda self, it: self.map(operator.sub, it)
    __sub__.__doc__ = """Substract a 2-elements iterable and return an xytuple.
                      """
    __mul__ = __imul__ = lambda self, it: self.map(operator.mul, it)
    __mul__.__doc__ = """Product by a 2-elements iterable and return an xytuple.
                      """
    __div__ = __idiv__ = lambda self, it: self.map(operator.div, it)
    __div__.__doc__ = """Divide by a 2-elements iterable and return an xytuple.
                      """
    __neg__ = lambda self: self * (-1,-1)
    __neg__.__doc__ = """Return the additive inverse of an xytuple.
                      """
    __abs__ = lambda self: abs(complex(*self))
    __abs__.__doc__ = """Return a float, the norm of the coordinates.
                      """


# Direction enumeration
class Dir:

    # Directions

    NONE = xytuple(0,0)
    UP = xytuple(0,-1)
    DOWN = xytuple(0,+1)
    LEFT = xytuple(-1,0)
    RIGHT = xytuple(+1,0)
    UPLEFT = UP + LEFT
    UPRIGHT = UP + RIGHT
    DOWNLEFT = DOWN + LEFT
    DOWNRIGHT = DOWN + RIGHT

    #: Direction to Rect attribute
    DIR_TO_ATTR = {NONE: "center",
                   UP: "midtop",
                   DOWN: "midbottom",
                   LEFT: "midleft",
                   RIGHT: "midright",
                   UPLEFT: "topleft",
                   UPRIGHT: "topright",
                   DOWNLEFT: "bottomleft",
                   DOWNRIGHT: "bottomright",}

    #: Rect attribute to direction
    ATTR_TO_DIR = dict(map(reversed, DIR_TO_ATTR.items()))

    #: List of all directions
    DIRS = [xytuple(x,y) for x in range(-1,2) for y in range(-1,2)]

    #: List of all normalized directions
    NORMALIZED_DIRS = [direct/(2*(abs(direct),))
                       for direct in DIRS if any(direct)]

    # Class methods

    @classmethod
    def closest_dir(cls, vector, normalized=True, include_none=False):
        """Return the closest dir to a given vector.

        By default, the normalized directions are used to check
        the distances, but a standard direction is always returned.

        By default, the NONE direction is excluded from the results.
        """
        dirs = cls.NORMALIZED_DIRS if normalized else cls.DIRS
        _, direct = min((abs(direct - vector), direct) for direct in dirs
                        if include_none or any(direct))
        if not normalized:
            return direct
        return direct.map(round).map(int)

    # Class generators

    @classmethod
    def generate_steps(cls, old, new):
        """Generate all the directions to go from one position
        to another.
        """
        new, current = xytuple(new), xytuple(old)
        while current != new:
            step = cls.closest_dir(new - current)
            current += step
            yield step, current

    @classmethod
    def generate_positions(cls, old, new):
        """Generate all the intermediate position to go from
        one position to another. They're both included.
        """
        yield xytuple(old)
        for step, current in cls.generate_steps(old, new):
            yield current

    @classmethod
    def generate_rects(cls, old, new):
        """Generate all the intermediate rectangles to go from
        one rectangle to another. They're both included.
        However, all rectangles have the first rectangle size.
        """
        for position in cls.generate_positions(old.center, new.center):
            copy = old.copy()
            copy.center = position
            yield copy


# Cursored list
class cursoredlist(list):
    """Enhanced list with a cursor attribute

    Args:
        iterator (any iterable): Iterator to build the list from
        pos (int): Initial cursor value (default is 0)
    """

    def __init__(self, iterator, cursor=0):
        """Inititalize the cursor."""
        list.__init__(self, iterator)
        self.cursor = cursor

    def get(self, default=None):
        """Get the current object."""
        if len(self):
            self.cursor %= len(self)
        try:
            return self[self.cursor]
        except IndexError:
            return default

    def inc(self, inc):
        """Increment the cursor and return the new current object.

        Args:
            inc (int): Number of incrementation of the cursor
        """
        self.cursor += inc
        return self.get()

    def dec(self, dec):
        """Decrement the cursor and return the new current object.

        Args:
            dec (int): Number of decrementation of the cursor
        """
        self.cursor -= dec
        return self.get()

    def set(self, index):
        """Set the cursor to an arbitrary index value."""
        if len(self):
            self.cursor = index % len(self)


def scale_dirty(source, dest, dirty, scale):
    if not all(source.get_size()):
        return
    if dirty is None:
        scale(source, dest.get_size(), dest)
        return [dest.get_rect()]
    dest_rects = scale_rects(dirty, source.get_rect(), dest.get_rect())
    for source_rect, dest_rect in zip(dirty, dest_rects):
        subsource = source.subsurface(source_rect)
        subdest = dest.subsurface(dest_rect)
        scale(subsource, dest_rect.size, subdest)
    return dest_rects


# Scale rectangles function
def scale_rects(rects, source, dest):
    # Initialize
    gcds = xytuple(dest.size).map(gcd, source.size)
    ratios = gcds.map(float)/source.size
    size_ratios = xytuple(dest.size).map(float) / source.size
    source_lst, dest_lst = [], []
    # Update source rectangles
    for rect in rects:
        topleft = (ratios * rect.topleft).map(int) / ratios
        bottomright = (ratios * rect.bottomright).map(ceil) / ratios
        rect.topleft, rect.size = topleft, bottomright - topleft
        update_rect_list(rect, source_lst, source)
    rects[:] = source_lst
    # Get dest recangles
    for rect in source_lst:
        topleft = size_ratios * rect.topleft
        bottomright = size_ratios * rect.bottomright
        dest_lst.append(Rect(topleft, bottomright - topleft))
    # Return
    return dest_lst


# Update rect list
def update_rect_list(rect, lst, clip):
    """Append a rectangle to a list using union and clip."""
    i = rect.collidelist(lst)
    while -1 < i:
        rect.union_ip(lst[i])
        del lst[i]
        i = rect.collidelist(lst)
    lst.append(rect.clip(clip))


# Cache dictionary
class cachedict(defaultdict):

    def __missing__(self, key):
        if isinstance(key, tuple):
            self[key] = self.default_factory(*key)
        else:
            self[key] = self.default_factory(index)
        return self[key]


# Cache decorator
def cache_method(func, static=False):
    weak_dct = WeakKeyDictionary()
    @wraps(func)
    def wrapper(self, *args):
        dct = weak_dct.setdefault(self, {})
        if args not in dct:
            f_args = args
            if not static:
                f_args = (self,) + args
            dct[args] = func(*f_args)
        return dct[args]
    return wrapper

# Cache decorator
def cache(func):
    dct = {}
    @wraps(func)
    def wrapper(*args):
        if args not in dct:
            dct[args] = func(*args)
        return dct[args]
    return wrapper

# From parent decorator
def from_parent(lst):
    # Getter generator
    gen_getter = lambda attr: lambda self: getattr(self.parent, attr)
    # Decorator
    def decorator(cls):
        # Loop over attributes
        for attr in lst:
            # Set property
            setattr(cls, attr, property(gen_getter(attr)))
        return cls
    # Return
    return decorator


# Color class
class Color(Color):
    """TODO: Enhanced version of pygame.Color."""
    pass

