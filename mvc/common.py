import operator
from collections import namedtuple

""" Tuple for x,y coordinates and their transformations """
XY = namedtuple("XY",("x","y"))
XY.__iadd__ = XY.__add__ = lambda x, y: XY(*map(operator.add, x, y))
XY.__isub__ = XY.__sub__ = lambda x, y: XY(*map(operator.sub, x, y))
XY.__imul__ = XY.__mul__ = lambda x, y: XY(*map(operator.mul, x, y))
XY.__idiv__ = XY.__div__ = lambda x, y: XY(*map(operator.div, x, y))
XY.__abs__ = lambda x: abs(complex(*x))
XY.map = lambda x,func: XY(*map(func, x))

class Cursor:
    def __init__(self, iterator, pos=0):
        self._lst = list(iterator)
        self._pos = pos
        self._mod = len(self._lst)

    def get(self):
        return self._lst[self._pos]

    def inc(self, inc):
        self._pos += inc
        self._pos %= self._mod
        return self.get()
