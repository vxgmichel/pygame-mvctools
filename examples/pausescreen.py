from mvctools import BaseState, BaseModel, BaseController, BaseView
from mvctools import AutoSprite, NextStateException
from mvctools.utils import TextSprite

from pygame import Surface
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

class PauseSprite(TextSprite):
    
    font_ratio = 0.05
    font_name = "visitor2"
    color = "white"
    position_ratio = (0.5, 0.5)

    @property
    def text(self):
        return self.model.text

    @property
    def font_size(self):
        return int(self.screen_height * self.font_ratio)

    @property
    def pos(self):
        return (self.screen_size * self.position_ratio).map(int)

# View class

class PauseView(BaseView):
    shade_ratio = 0.5
    sprite_class_dct = {PauseModel:PauseSprite}

    def create_background(self):
        bgd = self.screen.copy()
        color = (255*self.shade_ratio,)*3
        bgd.fill(color, special_flags=pg.BLEND_MULT)
        return bgd

# Loading state              

class PauseState(BaseState):
    model_class = PauseModel
    controller_class = PauseController
    view_class = PauseView

