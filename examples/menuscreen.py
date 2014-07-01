from mvc.state import BaseState, NextStateException
from mvc.model import BaseModel
from mvc.controller import BaseController
from mvc.view import BaseView, AutoSprite
from mvc.common import Cursor

from collections import OrderedDict

from pygame import Color, Rect
import pygame as pg

# Controller

class MenuController(BaseController):

    def handle_event(self, event):
        if event.type == pg.KEYDOWN and \
           event.key in [pg.K_SPACE, pg.K_RETURN]:
            self.model.register_validation()
        if event.type == pg.KEYDOWN and \
           event.key in [pg.K_UP, pg.K_LEFT]:
            self.model.register_up()
        if event.type == pg.KEYDOWN and \
           event.key in [pg.K_DOWN, pg.K_RIGHT]:
            self.model.register_down()
        

# Model

class MenuModel(BaseModel):

    state_dct = OrderedDict([])
    title = "Example v1.0"

    def init(self):
        iterator = enumerate(self.state_dct.iteritems())
        self.entry_dct = [EntryModel(self, i, entry, state)
                          for i, (entry, state) in iterator]
        self.cursor = Cursor(self.entry_dct)
        self.cursor.get().selected = True
        
    def register_validation(self):
        state = self.cursor.get().state
        self.control.register_next_state(state)
        raise NextStateException

    def register_up(self):
        self.cursor.get().selected = False
        self.cursor.inc(-1).selected = True

    def register_down(self):
        self.cursor.get().selected = False
        self.cursor.inc(1).selected = True
                              

class EntryModel(BaseModel):
    
    def init(self, pos, text, state):
        self.text = text
        self.pos = pos
        self.selected = False
        self.state = state
    

# Sprite classes

class EntrySprite(AutoSprite):
    
    u_font_ratio = 0.05
    s_font_ratio = 0.1
    font_name = "visitor2"
    font_color = Color("black")
    first_entry_position_ratio = (0.4, 0.6)
    relative_position_ratio = (0.1, 0.07)
    
    def init(self):
        self.u_renderer = self.build_renderer(self.u_font_size)
        self.s_renderer = self.build_renderer(self.s_font_size)
        self.u_image = self.u_renderer(self.model.text)
        self.s_image = self.s_renderer(self.model.text)
        self.layer = 1

    def get_image(self):
        return self.s_image if self.model.selected else self.u_image

    def get_rect(self):
        return self.image.get_rect(center=self.center)

    @property
    def u_font_size(self):
        return int(self.settings.width * self.u_font_ratio)

    @property
    def s_font_size(self):
        return int(self.settings.width * self.s_font_ratio)

    @property
    def center(self):
        first = (self.settings.size * self.first_entry_position_ratio)
        shift =  (self.settings.size * self.relative_position_ratio)
        return (first + shift * ((self.model.pos,)*2)).map(int)

    def build_renderer(self, size):
        font = getattr(self.resource.font, self.font_name)(size)
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
        font = getattr(self.resource.font, self.font_name)(size)
        return lambda text: font.render(text, False, self.font_color)

class BackgroundSprite(AutoSprite):

    size_ratio = 4, 4
    speed_ratio = 0.001, 0.002
    background = "box_stripes_grey"

    def init(self):
        self.title = TitleSprite(self)
        self.image = self.scale(self.resource.image.get(self.background))
        self.screen_rect = Rect((0,0), self.settings.size)
        self.rect = self.image.get_rect(center=self.screen_rect.center)
        self.step = self.settings.size*self.speed_ratio

    def get_rect(self):
        factors = ((1,1), (-1,1), (1,-1), (-1,-1))
        for factor in factors:
            rect = self.rect.move(self.step*factor)
            if rect.contains(self.screen_rect):
                self.step *= factor
                return rect

    def scale(self, image):
        total_size = (self.settings.size*self.size_ratio).map(int)
        return pg.transform.smoothscale(image, total_size)

# View class

class MenuView(BaseView):
    sprite_class_dct = {EntryModel: EntrySprite,
                        MenuModel: BackgroundSprite}

# Loading state              

class MenuState(BaseState):
    model_class = MenuModel
    controller_class = MenuController
    view_class = MenuView
