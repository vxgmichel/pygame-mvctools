"""Module with useful classes and functions."""

import operator
from collections import namedtuple, defaultdict
from pygame import Color


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
    
    __add__ = __iadd__ = lambda self, it: xytuple(*map(operator.add, self, it))
    __add__.__doc__ = """Add a 2-elements iterable and return an xytuple.
                      """
    __sub__ = __isub__ = lambda self, it: xytuple(*map(operator.sub, self, it))
    __sub__.__doc__ = """Substract a 2-elements iterable and return an xytuple.
                      """
    __mul__ = __imul__ = lambda self, it: xytuple(*map(operator.mul, self, it))
    __mul__.__doc__ = """Product by a 2-elements iterable and return an xytuple.
                      """
    __div__ = __idiv__ = lambda self, it: xytuple(*map(operator.div, self, it))
    __div__.__doc__ = """Divide by a 2-elements iterable and return an xytuple.
                      """
    __neg__ = lambda self: self * (-1,-1)
    __neg__.__doc__ = """Return the additive inverse of an xytuple.
                      """
    __abs__ = lambda self: abs(complex(*self))
    __abs__.__doc__ = """Return a float, the norm of the coordinates.
                      """

    def map(self, func):
        """Map the coordinates with the given function a return an xytuple."""
        return xytuple(*map(func, self))


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


class cachedict(defaultdict):

    def __missing__(self, key):
        if isinstance(key, tuple):
            self[key] = self.default_factory(*key)
        else:
            self[key] = self.default_factory(index)
        return self[key]


def cache(func):
    dct = {}
    def wrapper(arg):
        if arg not in dct:
            dct[arg] = func(arg)
        return dct[arg]
    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    return wrapper

class Color(Color):
    """TODO: Enhanced version of pygame.Color."""
    pass
        
