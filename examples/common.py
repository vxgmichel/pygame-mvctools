from mvctools import BaseModel, AutoSprite, Timer, NextStateException
from mvctools import BaseView, from_gamedata, xytuple, cursoredlist
from mvctools.utils.menu import EntrySprite, EntryModel
from mvctools.utils.text import TextSprite
from mvctools.utils.camera import CameraSprite, CameraModel
from pygame import Rect
import operator

# Entry

class StateEntryModel(EntryModel):
    
    def init(self, pos, text, state):
        EntryModel.init(self, pos, text)
        self.state = state

    def activate(self):
        if self.state:
            self.control.push_current_state()
        self.control.register_next_state(self.state)
        raise NextStateException
    
class EntrySprite(EntrySprite):
    
    font_name = "visitor2"
    font_color = "black"
    font_ratios = {False: 0.07, True: 0.1,}
    first_entry_position_ratio = (0.2, 0.6)
    relative_position_ratio = (0.1, 0.07)

# Choice

class ChoiceModel(EntryModel):
    
    def init(self, pos, text, values):
        super(ChoiceModel, self).init(pos, text)
        self.cursor = cursoredlist(values)

    @property
    def current(self):
        return self.cursor.get()

    def register_click(self):
        self.shift_right()
        self.activate()

    def shift_left(self):
        self.cursor.inc(-1)

    def shift_right(self):
        self.cursor.inc(+1)


    

class ChoiceSprite(EntrySprite):

    @property
    def text(self):
        value = self.model.cursor.get()
        return self.model.text + " : < " + value + " >"

# Displayed Timer

class DisplayedTimer(Timer):
    pass

class TimerSprite(TextSprite):
    
    font_ratio = 0.1
    font_name = "visitor2"
    color = "black"
    reference = "midleft"
    position_ratio = (0.7, 0.9)
  
    def init(self):
        RendererSprite.init(self)
        self.nb_digits = len(self.get_text())
        self.digits = [DigitSprite(self, 0, self.midleft)]
        for pos in range(1, self.nb_digits):
            midleft = self.digits[-1].rect.midright 
            self.digits.append(DigitSprite(self, pos, midleft))

    @property
    def font_size(self):
        return int(self.screen_height * self.font_ratio)

    @property
    def pos(self):
        return (self.screen_size * self.position_ratio).map(int)

    def update(self):
        self.text = self.get_text()

    def get_text(self):
        time = self.model.get()
        return "{:05.2f}".format(time).replace(".",":")

class DigitSprite(AutoSprite):
  
    def init(self, pos, midleft):
        self.pos = pos
        base_image = self.parent.renderer("0")
        self.rect = base_image.get_rect(midleft=midleft)

    @property
    def value(self):
        return self.parent.text[self.pos]                     

    def get_rect(self):
        return self.image.get_rect(center=self.center)
        
    def get_image(self):
        return self.parent.renderer(self.value)

# Background

class BackgroundModel(CameraModel):

    size_ratio = 4, 4
    speed_ratio = 0.02, 0.05

    def init(self):
        self.init_camera(self.rect)
        self.low = 0, 0
        self.pos = xytuple(0, 0).map(float)
        self.high = self.size - self.rect.size

    @property
    def size(self):
        path = BackgroundSprite.BackgroundView.bgd_image
        size = self.control.resource.get(path).get_size()
        return xytuple(size)

    @from_gamedata("background_rect")
    def rect(self):
        return Rect((0,0), xytuple(self.size) / self.size_ratio)

    @from_gamedata("background_step")
    def step(self):
        return self.size * self.speed_ratio

    def is_valid_pos(self, pos):
        return all(map(operator.le, self.low, pos) + \
                   map(operator.le, pos, self.high))

    def update(self):
        for i in (1,-1):
            for j in (1,-1):
                shift = self.step * (i,j)
                shift *= (self.delta,)*2
                new_pos = xytuple(self.pos) + shift
                if self.is_valid_pos(new_pos):
                    self.rect.topleft = self.pos = new_pos
                    self.set_camera(self.rect)
                    self.step *= (i,j)
                    return

class BackgroundSprite(CameraSprite):

    class BackgroundView(BaseView):
        bgd_image = "image/box_stripes_grey"
        bgd_color = "lightblue"

        @property
        def size(self):
            return self.model.size

    view_cls = BackgroundView
