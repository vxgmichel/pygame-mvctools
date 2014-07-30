import pygame as pg
from pygame.sprite import LayeredDirty, DirtySprite
from pygame import Rect, Surface, transform
from functools import partial
from mvctools.common import xytuple, cachedict

AutoGroup = partial(LayeredDirty, _use_updates = True, _time_threshold = 1000)

class BaseView(object):

    sprite_class_dct = {}

    def __init__(self, state, model):
        # Attributes to higher instances
        self.state = state
        self.model = model
        self.control = self.state.control
        self.resource = self.control.resource
        self.settings = self.control.settings
        # View-related attributes
        self.sprite_dct = {}
        self.group = AutoGroup()
        self.screen = pg.display.get_surface()
        self.background = self.get_background()
        self.first_update = True
        # Call user initialisation
        self.init()

    def init(self):
        pass

    def get_background(self):
        return None

    def _reload(self):
        self.__init__(self, self.model)

    def _update(self):
        # Handle parameter
        self.group._use_update = not self.first_update
        self.first_update = False
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
                    self.sprite_dct[key] = cls(self, model=obj)

    def get_sprite_class(self, obj):
        return self.sprite_class_dct.get(obj.__class__, None)

    @classmethod
    def register_sprite_class(cls, obj_cls, sprite_cls):
        cls.sprite_class_dct[obj_cls] = sprite_cls
        

class AutoSprite(DirtySprite):

    size_ratio = None

    def __init__(self, parent, *args, **kwargs):
        super(AutoSprite, self).__init__()
        # Model default kwarg
        model = kwargs.pop("model", None)
        # Internal variables
        self._image = Surface((0,0))
        self._rect = Autorect(self.image.get_rect())
        self._layer = 0
        # Parent handling
        self.parent = parent
        if isinstance(parent, AutoSprite):
            parent.register_child(self)
            self._layer = parent.layer
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
        self.init(*args, **kwargs)

    def init(self, *args, **kwargs):
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

    # Access autorect properties

    def __getattr__(self, name):
        if hasattr(Autorect, name) and \
           isinstance(getattr(Autorect, name), property):
            return getattr(self.rect, name)
        return super(AutoSprite, self).__getattr__(name)

##    def __setattr__(self, name, value):
##        if hasattr(Autorect, name) and \
##           isinstance(getattr(Autorect, name), property):
##            return setattr(self.rect, name, value)
##        return super(AutoSprite, self).__setattr__(name, value)

    # Method to override

    def get_rect(self):
        return self.rect
    
    def get_image(self):
        return self.image

    def get_layer(self):
        return self.layer

    # Dirty flagging

    def set_dirty(self):
        self.dirty = self.dirty if self.dirty else 1

    # Conveniance methods
    
    def build_animation(self, resource, timer=None,
                        inf=None, sup=None, looping=True, resize=False):
        if timer is None:
            timer = self.model.lifetime
        size = self.size if resize else None
        return Animation(resource, timer, inf, sup, looping, size)
    
    @property
    def size(self):
        if not self.size_ratio:
            return xytuple(*self.image.get_size())
        return (self.settings.size * self.size_ratio).map(int)
            

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
        is_autorect = isinstance(rect, Autorect)
        if rect != self._rect:
            self.set_dirty()
            if not is_autorect:
                self._rect.size = rect.size
                self._rect.topleft = rect.topleft
        if is_autorect and rect is not self._rect:
            rect.register(self)
            self._rect = rect

    @rect.deleter
    def rect(self):
        del self._rect


class Animation(object):

    def __init__(self, resource, timer,
                 inf=None, sup=None, looping=True, size=None):
        # Set attributes
        self.resource = resource
        self.size = size
        self.timer = timer
        start, stop = timer.get_interval()
        self.inf = start if inf is None else inf
        self.sup = stop if sup is None else sup
        self.looping = looping
        # Set cache
        if isinstance(resource, list):
            self.cache = cachedict(self.scale_image)
        else:
            self.cache = self.resource

    def scale_image(self, index, size):
        raw = self.resource[index]
        if not size or size == raw.get_size():
            return raw
        return transform.smoothscale(raw, size)

    def get(self):
        normalized = (self.timer.get() - self.inf) / (self.sup - self.inf)
        index = int(normalized * len(self))
        if self.looping:
            index %= len(self)
        elif normalized >= 1:
            index = -1
        elif normalized <= 0:
            index = 0
        return self[index]

    def __len__(self):
        return len(self.resource)

    def __getitem__(self, index):
        return self.cache[index, self.size]



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
        
    
class Autorect(Rect):

    def __init__(self, *args, **kwargs):
        super(Autorect, self).__init__(*args, **kwargs)
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
        if not method.__name__.endswith('_ip'):
            return method
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



