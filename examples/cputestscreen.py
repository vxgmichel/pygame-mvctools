from mvctools.state import BaseState, NextStateException
from mvctools.model import BaseModel, Timer
from mvctools.controller import BaseController
from mvctools.view import BaseView, AutoSprite
from mvctools.common import cursoredlist, xytuple

from examples.menuscreen import MenuController, MenuView, MenuModel, \
                                EntryModel, EntrySprite, BackgroundModel, \
                                TitleSprite
from examples.settingscreen import SettingController, SettingModel, ChoiceModel, \
                                   SettingView

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

class TimerSprite(AutoSprite):
    
    font_ratio = 0.05
    font_name = "visitor2"
    font_color = Color("black")
    position_ratio = (0.9, 0.9)
  
    def init(self):
        self.renderer = self.build_renderer(self.font_size)
        
    def get_image(self):
        time = self.model.get()
        text = "{:05.2f}".format(time)
        text = text.replace("1","I")
        return self.renderer(text)

    def get_rect(self):
        return self.image.get_rect(center=self.center)

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

class CpuTestView(SettingView):
    pass

SettingView.sprite_class_dct[ChoiceLoadModel] = ChoiceSprite
SettingView.sprite_class_dct[CpuTestModel] = TitleSprite
SettingView.sprite_class_dct[DisplayedTimer] = TimerSprite
                        

# Loading state              

class CpuTestState(BaseState):
    model_class = CpuTestModel
    controller_class = SettingController
    view_class = CpuTestView
    state_dct = OrderedDict()

