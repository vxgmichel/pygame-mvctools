from itertools import count, chain

class BaseModel(object):
    def __init__(self, parent, *args, **kargs):
        self.isroot = not isinstance(parent, BaseModel)
        # Attributes to higher instances
        self.state = parent if self.isroot else parent.state
        self.control = parent.control
        self.gamedata = self.control.gamedata
        # Semi private attribute
        self._keygen = count() if self.isroot else parent._keygen
        # Useful attributes
        self.key = next(self._keygen)
        # Children and parent handling
        self.parent = parent
        self.children = {}
        if not self.isroot:
            self.parent.register_child(self)
        # Call user initialisation
        self.init(*args, **kargs)

    def init(self, *args, **kwargs):
        self.lifetime = Timer(self).start()

    def _reload(self):
        self.reload()
        [child._reload() for child in self.children.values()]

    def reload(self):
        pass

    def register_child(self, child):
        self.children[child.key] = child
        
    def update_children(self):
        [child._update() for child in self.children.values()]

    def _update(self):
        return self.update() or self.update_children()

    def update(self):
        pass
            
    def __iter__(self):
        iterators = [iter(child) for child in self.children.values()]
        value = (self.key, self)
        return chain([value], *iterators)

class Timer(BaseModel):

    def init(self, start=0, stop=None, periodic=False, callback=None):
        self._start = float("-inf") if start is None else start
        self._stop = float("inf") if stop is None else stop
        if self._start > self._stop:
            raise AttributeError("Invalid Range")
        self._periodic = periodic
        self._callback = callback
        self._ratio = 0.0
        self._current_value = float(start)
        self._next_increment = 0.0

    def get_interval(self):
        return self._start, self._stop

    def is_set(self):
        return self._current_value == self._stop

    def is_reset(self):
        return self._current_value == self._start

    def is_paused(self):
        return self._ratio == 0

    def start(self, ratio=1.0):
        self._ratio = float(ratio)
        return self

    def pause(self):
        self._ratio = 0.0
        return self

    def get(self):
        return self._current_value

    def reset_and_pause(self):
        self._current_value = self._start
        return self.pause()

    def set_and_pause(self, value=None):
        value = self._stop if value is None else value
        if self._start <= value <= self._stop:
            self._current_value = float(value)
            return self.pause()
        raise AttributeError("Invalid value")

    def modulo_adjust(self):
        self._current_value -= self._start
        self._current_value %= self._stop - self._start
        self._current_value += self._start

    def update(self):
        # Increment
        self._current_value += self._next_increment
        # Overflow
        if self._next_increment and \
           not self._start < self._current_value < self._stop:
            if self._periodic:
                self.modulo_adjust()
            elif self._current_value <= self._start:
                self.reset_and_pause()
            else:
                self.set_and_pause()
            if callable(self._callback):
                self._callback(self)
        # Prepare next increment
        delta = 1.0/self.control.settings.fps
        self._next_increment = delta*self._ratio
        
    
