import pygame as pg
from pygame.sprite import DirtySprite
from pygame import Rect, Surface, transform
from mvctools.common import xytuple, cachedict, scale_dirty
from mvctools import BaseView


class AutoSprite(DirtySprite):

    has_view = False

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
        self.dirty_rects = None
        self.group = parent.group
        self.group.add(self)
        # State
        self.state = self.parent.state
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
        for child in self.children:
            child.kill()
        self.group = None
        super(AutoSprite, self).kill()

    def delete(self):
        self.kill()
        for child in self.children:
            child.delete()
        self.children = []
        self.parent = None

    def register_child(self, child):
        self.children.append(child)

    # Access autorect properties

    def __getattr__(self, attr):
        if hasattr(Autorect, attr) and \
           isinstance(getattr(Autorect, attr), property):
            return getattr(self.rect, attr)
        raise AttributeError(attr)

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

    def scale_resource(self, resource, name, size=None):
        size = self.size if size is None else None
        return resource.getfile(name, size)

    @property
    def size(self):
        return xytuple(*self.image.get_size())

    @property
    def screen_size(self):
        return self.parent.screen_size

    @property
    def screen_width(self):
        return self.parent.screen_width

    @property
    def screen_height(self):
        return self.parent.screen_height

    # Layer property

    @property
    def layer(self):
        return self._layer

    @layer.setter
    def layer(self, layer):
        if layer is None:
            layer = 0
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
        if image is None:
            image = Surface((0,0))
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
        if rect is None:
            rest = Autorect(self.image.get_rect())
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

    # Visible property

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, visible):
        visible = bool(visible)
        if self.visible != visible:
            self._visible = visible
            self.set_dirty()

    @visible.deleter
    def visible(self):
        del self._visible

class ViewSprite(AutoSprite):

    view_cls = BaseView
    has_view = True

    def init(self, view_cls=None):
        if view_cls:
            self.view_cls = view_cls
        self.view = self.view_cls(self, self.model)

    def transform(self, screen, dirty):
        screen_size = screen.get_size()
        # No scaling needed
        if screen_size == self.size:
            return screen, dirty
        # Scalable screen
        if all(screen.get_size()):
            # Scale all
            if self.image.get_size() != self.size:
                self.image = Surface(self.size, screen.get_flags())
            # Scale dirty
            dirty = scale_dirty(screen, self.image, dirty)
            return self.image, dirty
        # Not scalable screen
        image = Surface(self.size, screen.get_flags())
        return image, None

    def get_image(self):
        # Get screen
        screen, dirty = self.view._update()
        # Transform
        image, dirty = self.transform(screen, dirty)
        # Dirtyness
        self.dirty_rects = dirty
        # Return
        return image

    def convert_position(self, pos):
        new_pos = xytuple(pos) - self.rect.topleft
        new_pos *= self.view.screen_size
        return new_pos / self.size

    def gen_sprites_at(self, pos):
        pos = self.convert_position(pos).map(round)
        return self.view.gen_sprites_at(pos)

    @property
    def size(self):
        return self.view.screen_size

    @property
    def transparent(self):
        return self.view.transparent

    def get_surface(self):
        msg = "no size or surface to provide"
        raise NotImplementedError(msg)

    def delete(self):
        self.view.delete()
        AutoSprite.delete(self)



class Animation(object):

    def __init__(self, resource, timer,
                 inf=None, sup=None, looping=True, size=None):
        # Set attributes
        self.resource = resource
        self.size = size
        self.timer = timer
        start, stop = timer.interval
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
