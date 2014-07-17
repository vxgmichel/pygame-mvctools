from mvctools.state import BaseState, NextStateException
from mvctools.model import BaseModel
from mvctools.controller import BaseController
from mvctools.view import BaseView, AutoSprite

from pygame import Color, Rect, Surface
import pygame as pg

# Controller

class PauseController(BaseController):

    def handle_event(self, event):
        if event.type == pg.KEYDOWN and \
           event.key in [pg.K_SPACE, pg.K_RETURN, pg.K_ESCAPE]:
            self.model.register_validation()
        

# Model

class PauseModel(BaseModel):

    text = "Pause"
        
    def register_validation(self):
        raise NextStateException
    

# Sprite classes

class PauseSprite(AutoSprite):
    
    font_ratio = 0.05
    font_name = "visitor2"
    font_color = Color("white")
    position_ratio = (0.5, 0.5)
  
    def init(self):
        self.renderer = self.build_renderer(self.font_size)
        self.image = self.renderer(self.model.text)
        self.rect = self.image.get_rect(center=self.center)

    @property
    def font_size(self):
        return int(self.settings.width * self.font_ratio)

    @property
    def center(self):
        return (self.settings.size * self.position_ratio).map(int)

    def build_renderer(self, size):
        font = self.resource.font.getfile(self.font_name, size)
        return lambda text: font.render(text, False, self.font_color)


# View class

class PauseView(BaseView):
    sprite_class_dct = {PauseModel:PauseSprite}

    def get_background(self):
        previous = self.screen.copy()
        previous.set_alpha(255/2)
        bgd = Surface(previous.get_size())
        bgd.blit(previous, previous.get_rect())
        return bgd

# Loading state              

class PauseState(BaseState):
    model_class = PauseModel
    controller_class = PauseController
    view_class = PauseView

