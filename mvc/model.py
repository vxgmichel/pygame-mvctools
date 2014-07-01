from itertools import count, chain

class BaseModel:
    def __init__(self, parent, *args, **kargs):
        self.isroot = not isinstance(parent, BaseModel)
        # Attributes to higher instances
        self.state = parent if self.isroot else parent.state
        self.control = parent.control
        # Semi private attribute
        self._keygen = count() if self.isroot else parent._keygen
        self._counter = count()
        # Useful attributes
        self.key = next(self._keygen)
        self.count = 0
        # Children and parent handling
        self.parent = parent
        self.children = {}
        if not self.isroot:
            self.parent.register_child(self)
        # Call user initialisation
        self.init(*args, **kargs)

    def init(self, *args, **kwargs):
        pass

    def register_child(self, child):
        self.children[child.key] = child
        
    def update_children(self):
        [obj._update() for obj in self.children.values()]

    def _update(self):
        self.count = next(self._counter)
        return self.update_children() or self.update()

    def update(self):
        pass
            
    def __iter__(self):
        iterators = [iter(child) for child in self.children.values()]
        value = (self.key, self)
        return chain([value], *iterators)
