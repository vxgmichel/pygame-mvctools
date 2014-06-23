from itertools import count, chain

class BaseModel:
    def __init__(self, parent=None):
        self.root = not isinstance(parent, BaseModel)
        self.control = parent if self.root else parent.control
        self.parent = None if self.root else parent
        self.keygen = count() if self.root else self.parent.keygen
        self.key = next(self.keygen)
        self.children = {}
        if not self.root:
            self.parent.register_child(self)
        self.init()

    def init(self):
        pass

    def register_child(self, child):
        self.children[child.key] = child
        
    def update_children(self):
        [obj.update() for obj in self.children]

    def _update(self):
        return self.update_children() or self.update()

    def update(self):
        pass
            
    def __iter__(self):
        iterators = [iter(child) for child in self.children]
        value = (self.key, self)
        return chain([value], *iterators)
