from mvctools import BaseController, BaseModel, BaseView, BaseState
from mvctools import cursoredlist
from mvctools.utils.renderer import RendererSprite

import pygame as pg

# Controller

class BaseMenuController(BaseController):

    def init(self):
        self.key_dct = {pg.K_SPACE: self.model.register_validation,
                        pg.K_RETURN: self.model.register_validation,
                        pg.K_UP: self.model.register_up,
                        pg.K_DOWN: self.model.register_down,
                        pg.K_LEFT: self.model.register_left,
                        pg.K_RIGHT: self.model.register_right,}

    def handle_event(self, event):
        if event.type == pg.KEYDOWN and event.key in self.key_dct:
            self.key_dct[event.key]()


# Secondary model

class BaseEntryModel(BaseModel):
    
    def init(self, pos, text):
        self.text = text
        self.pos = pos

    @property
    def selected(self):
        return self is self.parent.cursor.get()

    def register_validation(self):
        if self.selected:
            self.validate()

    def register_validation(self):
        if self.selected:
            self.validate()

    def register_validation(self):
        if self.selected:
            self.validate()

    def validate(self):
        pass
        

# Main Model

class BaseMenuModel(BaseModel):

    title = "Title"
    entry_data = {0: (BaseEntryModel, "First Entry"),
                  1: (BaseEntryModel, "Second Entry")}

    def init(self):
        self.entry_dct = {pos: self.generate_entry(pos, data)
                          for pos, data in self.entry_data.items()}
        entry_lst = (value for _, value in sorted(self.entry_dct.items()))
        self.cursor = cursoredlist(entry_lst)

    def generate_entry(self, pos, data):
        model = data[0]
        args = (pos,) + data[1:]
        return model(self, *args)

    def register_up(self):
        self.cursor.inc(-1)

    def register_down(self):
        self.cursor.inc(1)

    def register_left(self):
        self.cursor.get().register_left()

    def register_right(self):
        self.cursor.get().register_right()

    def register_validation(self):
        self.cursor.get().register_validation()


# Main Sprite

class BaseMenuSprite(RendererSprite):
    
    font_ratio = 0.15
    font_name = "visitor2"
    font_color = "black"
    position_ratio = (0.5, 0.3)
    
    def init(self):
        super(BaseMenuSprite, self).init()
        self.image = self.renderer(self.model.title)
        self.rect = self.image.get_rect(center=self.center)

    @property
    def center(self):
        return (self.settings.size * self.position_ratio).map(int)
        
# Secondary sprite

class BaseEntrySprite(RendererSprite):
    
    font_name = "visitor2"
    font_color = "black"
    font_ratios = {False: 0.07, True: 0.1,}
    first_entry_position_ratio = (0.2, 0.6)
    relative_position_ratio = (0.1, 0.07)
    
    def init(self):
        self.renderers = {selection: self.build_renderer(selection)
                            for selection in (True, False)}
                        
    def get_image(self):
        return self.renderers[self.model.selected](self.text)

    def get_rect(self):
        return self.image.get_rect(midleft=self.midleft)

    @property
    def text(self):
        return self.model.text

    @property
    def midleft(self):
        first = (self.settings.size * self.first_entry_position_ratio)
        shift =  (self.settings.size * self.relative_position_ratio)
        return (first + shift * ((self.model.pos,)*2)).map(int)

    def build_renderer(self, selection):
        size = int(self.settings.size.y * self.font_ratios[selection])
        return super(BaseEntrySprite, self).build_renderer(size=size)

# View

class BaseMenuView(BaseView):
    
    bgd_color = "white"
    bgd_image = None
    sprite_class_dct = {BaseEntryModel: BaseEntrySprite,
                        BaseMenuModel: BaseMenuSprite}

# State

class BaseMenuState(BaseState):
    controller_class = BaseMenuController
    model_class = BaseMenuModel
    view_class = BaseMenuView
    
