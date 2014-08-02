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
        





