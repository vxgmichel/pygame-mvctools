from mvctools.state import BaseState, NextStateException
from mvctools.model import BaseModel, property_from_gamedata
from mvctools.controller import BaseController
from mvctools.view import BaseView, AutoSprite
from mvctools.common import cursoredlist, xytuple

import operator
from collections import OrderedDict

from pygame import Color, Rect
import pygame as pg

# Controller

class MenuController(BaseController):

    def init(self):
        self.key_dct = {pg.K_SPACE: self.model.register_validation,
                        pg.K_RETURN: self.model.register_validation,
                        pg.K_UP: self.model.register_up,
                        pg.K_DOWN: self.model.register_down,
                        pg.K_LEFT: self.model.register_up,
                        pg.K_RIGHT: self.model.register_down,}

    def handle_event(self, event):
        if event.type == pg.KEYDOWN and event.key in self.key_dct:
            self.key_dct[event.key]()
        

# Model

class MenuModel(BaseModel):

    title = "Example v1.0"

    def init(self):
        # Background Model
        self.background = BackgroundModel(self)
        # Entry models
        iterator = enumerate(self.state.state_dct.iteritems())
        self.entry_dct = [EntryModel(self, i, entry, state)
                          for i, (entry, state) in iterator]
        # Cursor
        self.cursor = cursoredlist(self.entry_dct)
        self.cursor.get().selected = True
        
    def register_validation(self):
        self.cursor.get().register_validation()

    def register_up(self):
        self.cursor.get().selected = False
        self.cursor.inc(-1).selected = True

    def register_down(self):
        self.cursor.get().selected = False
        self.cursor.inc(1).selected = True

class BackgroundModel(BaseModel):

    size_ratio = 4, 4
    speed_ratio = 0.001, 0.002
    background = "box_stripes_grey"

    def init(self):
        self.low = xytuple(0,0).map(float)
        self.high = xytuple(*self.size_ratio).map(float) - (1,1)

    @property_from_gamedata("background_pos")
    def pos(self):
        # Return default value
        return (self.high-self.low)*(0.5, 0.5)


    @property_from_gamedata("background_step")
    def step(self):
        # Return default value
        return -xytuple(*self.speed_ratio)

    def is_valid_pos(self, pos):
        return all(map(operator.le, self.low, pos) + \
                   map(operator.le, pos, self.high))

    def update(self):
        for i in (1,-1):
            for j in (1,-1):
                new_pos = self.pos + self.step * (i,j)
                if self.is_valid_pos(new_pos):
                    self.pos = new_pos
                    self.step *= (i,j)
                    return
                              

class EntryModel(BaseModel):
    
    def init(self, pos, text, state):
        self.text = text
        self.pos = pos
        self.selected = False
        self.state = state

    def register_validation(self):
        self.control.register_next_state(self.state)
        raise NextStateException

    def register_left(self):
        pass

    def register_right(self):
        pass
    

# Sprite classes

class EntrySprite(AutoSprite):
    
    font_ratios = {False: 0.07,
                   True: 0.1,}
    font_name = "visitor2"
    font_color = Color("black")
    first_entry_position_ratio = (0.2, 0.6)
    relative_position_ratio = (0.1, 0.07)
    
    def init(self):
        self.images = {}
        for selection, ratio in self.font_ratios.items():
            height = int(self.settings.size.y * ratio)
            renderer = self.build_renderer(height)
            image = renderer(self.model.text)
            self.images[selection] = image
                        
    def get_image(self):
        return self.images[self.model.selected]

    def get_rect(self):
        return self.image.get_rect(midleft=self.midleft)

    @property
    def midleft(self):
        first = (self.settings.size * self.first_entry_position_ratio)
        shift =  (self.settings.size * self.relative_position_ratio)
        return (first + shift * ((self.model.pos,)*2)).map(int)

    def build_renderer(self, size=None):
        font = self.resource.font.getfile(self.font_name, size)
        return lambda text: font.render(text, False, self.font_color)

class TitleSprite(AutoSprite):
    
    font_ratio = 0.15
    font_name = "visitor2"
    font_color = Color("black")
    position_ratio = (0.5, 0.3)
    
    def init(self):
        self.renderer = self.build_renderer(self.font_size)
        self.image = self.renderer(self.model.title)
        self.rect = self.image.get_rect(center=self.center)
        self.layer = 1

    @property
    def font_size(self):
        return int(self.settings.width * self.font_ratio)

    @property
    def center(self):
        return (self.settings.size * self.position_ratio).map(int)

    def build_renderer(self, size):
        font = self.resource.font.getfile(self.font_name, size)
        return lambda text: font.render(text, False, self.font_color)

class BackgroundSprite(AutoSprite):

    background = "box_stripes_grey"

    def init(self):
        self.size_ratio = self.model.size_ratio
        self.image = self.resource.image.getfile(self.background, self.size).copy()

    def get_rect(self):
        topleft = -self.model.pos*self.settings.size
        return self.image.get_rect(topleft=topleft)

# View class

class MenuView(BaseView):
    
    bgd_color = Color("lightblue")
    sprite_class_dct = {EntryModel: EntrySprite,
                        MenuModel: TitleSprite,
                        BackgroundModel: BackgroundSprite}

    def get_background(self):
        return self.settings.scale_as_background(color=self.bgd_color)

# Loading state              

class MenuState(BaseState):
    model_class = MenuModel
    controller_class = MenuController
    view_class = MenuView
    state_dct = OrderedDict([])

