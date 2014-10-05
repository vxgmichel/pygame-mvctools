from mvctools import MouseController, BaseModel, BaseView, BaseState
from mvctools import cursoredlist
from mvctools.utils.renderer import RendererSprite
from collections import defaultdict
import pygame as pg

# Controller

class BaseMenuController(MouseController):

    axis_threshold = 0.5

    key_dct = {pg.K_SPACE: "validation",
               pg.K_RETURN: "validation",
               pg.K_ESCAPE: "back",
               pg.K_UP: "up",
               pg.K_DOWN: "down",
               pg.K_LEFT: "left",
               pg.K_RIGHT: "right",}

    axis_dct = {(0,-1): "left",
                (0,+1): "right",
                (1,-1): "up",
                (1,+1): "down",}

    hat_dct = {(0,-1): "down",
               (0,+1): "up",
               (-1,0): "left",
               (+1,0): "right",}

    button_dct = {0: "validation",
                  1: "back",
                  2: "validation",
                  3: "back",}

    def init(self):
        factory = lambda: None
        self.cache_dct = defaultdict(factory)
        pg.joystick.quit()
        pg.joystick.init()
        for i in range(pg.joystick.get_count()):
            pg.joystick.Joystick(i).init() 

    def handle_event(self, event):
        if super(BaseMenuController, self).handle_event(event):
            return True
        if event.type == pg.KEYDOWN:
            self.register(self.key_dct, event.key)
        if event.type == pg.JOYHATMOTION:
            self.register(self.hat_dct, event.value)
        if event.type == pg.JOYBUTTONDOWN:
            self.register(self.button_dct, event.button)
        if event.type == pg.JOYAXISMOTION:
            key = (event.axis, self.axis_position(event.value))
            self.register(self.axis_dct, key, "axis")

    def axis_position(self, arg):
        return cmp(arg, 0) if abs(arg) >= self.axis_threshold else 0

    def register(self, dct, key, cache=None):
        # Caching
        if cache == "axis":
            if self.cache_dct[cache, key[0]] == key[1]:
                return
            self.cache_dct[cache, key[0]] = key[1]
        # Register
        name = dct.get(key)
        if name:
            getattr(self.model, "register_"+name)()

# Secondary model

class BaseEntryModel(BaseModel):
    
    def init(self, pos, text):
        self.text = text
        self.pos = pos

    @property
    def selected(self):
        return self is self.parent.cursor.get()

    def select(self):
        self.parent.cursor.cursor = self.pos

    def validate(self):
        pass

    def shift_left(self):
        pass

    def shift_right(self):
        pass

    def register_hover(self):
        self.select()

    def register_click(self):
        self.validate()
        

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
        self.cursor.get().shift_left()

    def register_right(self):
        self.cursor.get().shift_right()

    def register_validation(self):
        self.cursor.get().validate()

    def register_back(self):
        self.cursor[-1].validate()


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
    
