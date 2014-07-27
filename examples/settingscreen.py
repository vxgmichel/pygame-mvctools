from mvctools.state import BaseState, NextStateException
from mvctools.model import BaseModel
from mvctools.controller import BaseController
from mvctools.view import BaseView, AutoSprite
from mvctools.common import cursoredlist, xytuple

from examples.menuscreen import MenuController, MenuView, MenuModel, \
                                EntryModel, EntrySprite, BackgroundModel, \
                                TitleSprite

import operator
from collections import OrderedDict, defaultdict

from pygame import Color, Rect
import pygame as pg

# Controller

class SettingController(MenuController):

    def init(self):
        self.key_dct = {pg.K_SPACE: self.model.register_validation,
                        pg.K_RETURN: self.model.register_validation,
                        pg.K_UP: self.model.register_up,
                        pg.K_DOWN: self.model.register_down,
                        pg.K_LEFT: self.model.register_left,
                        pg.K_RIGHT: self.model.register_right,}

# Model

class SettingModel(MenuModel):

    title = "Settings"

    setting_dct = OrderedDict()
    setting_dct["SIZE"] = ('800x600', '1024x720')
    setting_dct["MODE"] = ('WINDOWED', 'FULL')
    setting_dct["FPS"] = ('40', '60')

    def init(self):
        self.background = BackgroundModel(self)
        
        iterator = enumerate(self.setting_dct.iteritems())
        self.entries = [ChoiceModel(self, i, entry, values)
                        for i, (entry, values) in iterator]
        
        iterator = enumerate(self.state.state_dct.iteritems(),
                             len(self.entries))
        self.entries += [EntryModel(self, i, entry, state)
                         for i, (entry, state) in iterator]
        
        self.cursor = cursoredlist(self.entries)
        self.cursor.get().selected = True
        
    def register_validation(self):
        self.cursor.get().register_validation()

    def register_left(self):
        self.cursor.get().register_left()
        
    def register_right(self):
        self.cursor.get().register_right()    
                              


class ChoiceModel(EntryModel):
    
    def init(self, pos, text, values):
        super(ChoiceModel, self).init(pos, text, None)
        self.cursor = cursoredlist(values)

    def apply(self):
        attr = self.text.lower()
        value = self.cursor.get()
        setattr(self.control.settings, attr, value)

    def register_validation(self):
        self.apply()

    def register_left(self):
        self.cursor.inc(-1)

    def register_right(self):
        self.cursor.inc(+1)
    

# Sprite classes

class ChoiceSprite(EntrySprite):

    def init(self):
        self.images = defaultdict(dict)
        for value in self.model.cursor:
            text = self.model.text + " : < " + value + " >"
            for selection, ratio in self.font_ratios.items():
                height = int(self.settings.size.y * ratio)
                renderer = self.build_renderer(height)
                image = renderer(text)
                self.images[value][selection] = image

    def get_image(self):
        value = self.model.cursor.get()
        return self.images[value][self.model.selected]


# View class

class SettingView(MenuView):
    pass

SettingView.sprite_class_dct[ChoiceModel] = ChoiceSprite
SettingView.sprite_class_dct[SettingModel] = TitleSprite
                        

# Loading state              

class SettingState(BaseState):
    model_class = SettingModel
    controller_class = SettingController
    view_class = SettingView
    state_dct = OrderedDict()

