import pygame as pg
from pygame.sprite import LayeredDirty, DirtySprite
from pygame import Rect, Surface
from functools import partial

AutoGroup = partial(LayeredDirty, _use_updates = True, _time_threshold = 1000)

class BaseView:

    sprite_class_dct = {}

    def __init__(self, control, model):
        self.model = model
        self.control = control
        self.resource = self.control.resource
        self.settings = self.control.settings
        self.sprite_dct = {}
        self.group = AutoGroup()
        self.screen = pg.display.get_surface()
        self.background = self.get_background()
        self.init()

    def init(self):
        pass

    def get_background(self):
        return None

    def check_screen(self):
        if self.screen is not pg.display.get_surface():
            self.__init__(self.control, self.model)

    def _update(self):
        # Update, draw and display
        self.gen_sprites()
        self.group.update()
        dirty = self.group.draw(self.screen, self.background)
        pg.display.update(dirty)

    def gen_sprites(self):
        for key,obj in self.model:
            if key not in self.sprite_dct:
                cls = self.get_sprite_class(obj)
                if cls:
                    self.sprite_dct[key] = cls(self, obj)

    def get_sprite_class(self, obj):
        return self.sprite_class_dct.get(obj.__class__, None)

    @classmethod
    def register_sprite_class(cls, obj_cls, sprite_cls):
        cls.sprite_class_dct[obj_cls, sprite_cls]
        

class AutoSprite(DirtySprite):

    def __init__(self, parent, model=None):
        super(AutoSprite, self).__init__()
        # Internal variables
        self._image = Surface((0,0))
        self._rect = AutoRect(self.image.get_rect())
        # Parent handling
        self.parent = parent
        if isinstance(parent, AutoSprite):
            parent.register_child(self)
        # Group handling
        self.group = parent.group
        self.group.add(self)
        # Model
        self.model = model if model else parent.model
        # Resource
        self.resource = parent.resource
        # Settings
        self.settings = parent.settings
        # Children
        self.children = []
        # Init
        self.init()

    def init(self):
        pass

    def update(self):
        self.image = self.get_image()
        self.rect = self.get_rect()
        self.layer = self.get_layer()

    def kill(self):
        [child.kill() for child in self.children]
        super(AutoSprite, self).kill()

    def register_child(self, child):
        self.children.append(child)

    # Method to override

    def get_rect(self):
        return self.rect
    
    def get_image(self):
        return self.image

    def get_layer(self):
        return 0

    # Dirty flagging

    def set_dirty(self):
        self.dirty = self.dirty if self.dirty else 1

    # Layer property

    @property
    def layer(self):
        return self._layer

    @layer.setter
    def layer(self, layer):
        if self._layer != layer:
            self._layer = layer
            self.group.change_layer(self, layer)
            
    @layer.deleter
    def layer(self):
        self.set_layer(-1)

    def force_layer(self):
        layer = self.layer
        del self.layer
        self.layer = layer
    
    # Image property
    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, image):
        if image is not self._image:
            self.set_dirty()
        self._image = image

    @image.deleter
    def image(self):
        del self._image

    # Rect property

    @property
    def rect(self):
        return self._rect

    @rect.setter
    def rect(self, rect):
        if rect != self._rect:
            self.set_dirty()
        if isinstance(rect, AutoRect) and rect is not self._rect:
            rect.register(self)
        self._rect = rect

    @rect.deleter
    def rect(self):
        del self._rect


class UpgradingMetaClass(type):
    def __new__(metacls, name, bases, attrs):
        cls = type(name, bases, attrs)  
        for name in dir(cls):
            attr = getattr(cls, name)
            if type(attr) in cls.upgrade_dict:
                func = cls.upgrade_dict[type(attr)]
                if not callable(func):
                    func = func.__func__
                setattr(cls, name, func(attr))
        return cls
        
    
class AutoRect(Rect):

    def __init__(self, *args, **kwargs):
        super(AutoRect, self).__init__(*args, **kwargs)
        self.sprites = []

    def notify(self):
        [sprite.set_dirty() for sprite in self.sprites]

    def register(self, sprite):
        self.sprites.append(sprite)

    __metaclass__ = UpgradingMetaClass
    
    @staticmethod
    def upgrade_descriptor(descriptor):
        def setter(obj, value):
            if descriptor.__get__(obj) != value:
                obj.notify()
            descriptor.__set__(obj, value)
        return property(descriptor.__get__, setter, descriptor.__delete__)

    @staticmethod
    def upgrade_method(method):
        def wrapper(self, *args, **kwargs):
            temp = Rect.copy(self)
            res = method(self, *args, **kwargs)
            if temp != self:
                self.notify()
            return res
        return wrapper

    descriptor_type = type(Rect.x)
    method_type = type(Rect.move)
    upgrade_dict = {descriptor_type: upgrade_descriptor,
                    method_type: upgrade_method}



