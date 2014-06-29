from itertools import count, chain

class BaseModel:
    def __init__(self, parent, *args, **kargs):
        self.root = not isinstance(parent, BaseModel)
        self.control = parent if self.root else parent.control
        self.parent = None if self.root else parent
        self.keygen = count() if self.root else self.parent.keygen
        self.key = next(self.keygen)
        self.counter = count()
        self.count = 0
        self.children = {}
        if not self.root:
            self.parent.register_child(self)
        self.init(*args, **kargs)

    def init(self, *args, **kwargs):
        pass

    def register_child(self, child):
        self.children[child.key] = child
        
    def update_children(self):
        [obj.update() for obj in self.children.values()]

    def _update(self):
        self.count = next(self.counter)
        return self.update_children() or self.update()

    def update(self):
        pass
            
    def __iter__(self):
        iterators = [iter(child) for child in self.children.values()]
        value = (self.key, self)
        return chain([value], *iterators)
