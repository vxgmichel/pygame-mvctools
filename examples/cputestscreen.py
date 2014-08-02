from mvctools import BaseState, BaseModel, BaseController, BaseView
from mvctools import NextStateException, Timer, AutoSprite
from mvctools import cursoredlist, xytuple


from examples.menuscreen import MenuController, MenuView, MenuModel, \
                                EntryModel, EntrySprite, BackgroundModel, \
                                TitleSprite
from examples.settingscreen import SettingController, SettingModel, ChoiceModel, \
                                   SettingView
from examples.common import RendererSprite

import operator
from collections import OrderedDict, defaultdict
from time import sleep
from pygame import Color, Rect
import pygame as pg


# Model

class CpuTestModel(SettingModel):

    title = "CPUTEST"

    setting_dct = OrderedDict()
    setting_dct["CPU LOAD"] = ('NO', 'LOW', 'MEDIUM', 'HIGH')

    def init(self):
        self.background = BackgroundModel(self)
        self.timer = DisplayedTimer(self, stop=60, periodic=True).start()
        iterator = enumerate(self.setting_dct.iteritems())
        self.entries = [ChoiceLoadModel(self, i, entry, values)
                        for i, (entry, values) in iterator]
        
        iterator = enumerate(self.state.state_dct.iteritems(),
                             len(self.entries))
        self.entries += [EntryModel(self, i, entry, state)
                         for i, (entry, state) in iterator]
        
        self.cursor = cursoredlist(self.entries)
        self.cursor.get().selected = True

class DisplayedTimer(Timer):
    pass


class ChoiceLoadModel(ChoiceModel):

    dct = OrderedDict()
    dct["NO"] = 0
    dct["LOW"] = 0.01
    dct["MEDIUM"] = 0.05
    dct["HIGH"] = 0.1

    def init(self, pos, text, values):
        super(ChoiceLoadModel, self).init(pos, text, values)
        self.apply()

    def apply(self):
        self.current = self.cursor.get()

    def update(self):
        sleep(self.dct[self.current])
    

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

class TimerSprite(RendererSprite):
    
    font_ratio = 0.1
    font_name = "visitor2"
    font_color = Color("black")
    position_ratio = (0.7, 0.9)
    native_ratio = 4/3.0
  
    def init(self):
        self.renderer = self.build_renderer()
        self.digits = [DigitSprite(self, self.midleft)]
        for x in range(4):
            midleft = self.digits[x].rect.midright
            self.digits.append(DigitSprite(self, midleft))

    @property
    def midleft(self):
        return (self.settings.size * self.position_ratio).map(int)

    def update(self):
        time = self.model.get()
        text = "{:05.2f}".format(time).replace(".",":")
        for digits, value in zip(self.digits, text):
            digits.value = value

class DigitSprite(AutoSprite):
  
    def init(self, midleft, value="0"):
        self.value = value
        self.rect = self.get_image().get_rect(midleft=midleft)

    def get_rect(self):
        return self.image.get_rect(center=self.center)
        
    def get_image(self):
        return self.parent.renderer(self.value)


# View class

class CpuTestView(SettingView):
    pass
CpuTestView.register_sprite_class(ChoiceLoadModel, ChoiceSprite)
CpuTestView.register_sprite_class(CpuTestModel, TitleSprite)
CpuTestView.register_sprite_class(DisplayedTimer, TimerSprite)
                        

# Loading state              

class CpuTestState(BaseState):
    model_class = CpuTestModel
    controller_class = SettingController
    view_class = CpuTestView
    state_dct = OrderedDict()

