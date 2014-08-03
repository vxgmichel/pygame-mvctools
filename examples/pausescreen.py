from mvctools import BaseState, BaseModel, BaseController, BaseView
from mvctools import AutoSprite, NextStateException
from mvctools.utils import RendererSprite

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

class PauseSprite(RendererSprite):
    
    font_ratio = 0.05
    font_name = "visitor2"
    font_color = "white"
    position_ratio = (0.5, 0.5)
  
    def init(self):
        RendererSprite.init(self)
        self.image = self.renderer(self.model.text)
        self.rect = self.image.get_rect(center=self.center)

    @property
    def center(self):
        return (self.settings.size * self.position_ratio).map(int)

# View class

class PauseView(BaseView):
    shade_ratio = 0.5
    sprite_class_dct = {PauseModel:PauseSprite}

    def get_background(self):
        bgd = self.screen.copy()
        color = (255*self.shade_ratio,)*3
        bgd.fill(color, special_flags=pg.BLEND_MULT)
        return bgd

# Loading state              

class PauseState(BaseState):
    model_class = PauseModel
    controller_class = PauseController
    view_class = PauseView

