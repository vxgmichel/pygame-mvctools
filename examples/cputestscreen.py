from mvctools.utils import BaseMenuView, BaseMenuState, BaseMenuSprite

from examples.common import DisplayedTimer, TimerSprite
from examples.common import ChoiceModel, ChoiceSprite
from examples.common import EntrySprite, EntryModel
from examples.common import BackgroundModel, BackgroundSprite

from examples.settingscreen import SettingModel

from collections import OrderedDict
from time import sleep

# Model

class LoadChoiceModel(ChoiceModel):

    sleep_dct = {"NO": 0,
                 "LOW": 0.01,
                 "MEDIUM": 0.05,
                 "HIGH": 0.1}

    def init(self, *args, **kwargs):
        ChoiceModel.init(self, *args, **kwargs)
        self.current_load = 0

    def validate(self):
        self.current_load = self.sleep_dct[self.current]

    def update(self):
        sleep(self.current_load)

class CpuTestModel(SettingModel):

    title = "CPUTEST"

    setting_dct = OrderedDict()
    setting_dct["CPU LOAD"] = ('NO', 'LOW', 'MEDIUM', 'HIGH')

    choice_model_class = LoadChoiceModel

    def init(self):
        SettingModel.init(self)
        self.timer = DisplayedTimer(self, stop=60, periodic=True).start()


# Sprite classes

class CpuTestSprite(BaseMenuSprite):
    
    font_ratio = 0.15
    font_name = "visitor2"
    font_color = "black"
    position_ratio = (0.5, 0.3)
    
# View class

class CpuTestView(BaseMenuView):
    bgd_color = "grey"
    bgd_image = None
    sprite_class_dct = {LoadChoiceModel: ChoiceSprite,
                        CpuTestModel: CpuTestSprite,
                        EntryModel : EntrySprite,
                        BackgroundModel: BackgroundSprite,
                        DisplayedTimer: TimerSprite}
                        

# Loading state              

class CpuTestState(BaseMenuState):
    model_class = CpuTestModel
    view_class = CpuTestView
    state_dct = {"Back": None}

