from mvctools.utils.menu import BaseMenuModel, BaseMenuView, BaseEntryModel
from mvctools.utils.menu import BaseMenuState, BaseMenuSprite, BaseEntrySprite

from examples.common import EntryModel, EntrySprite, ChoiceModel, ChoiceSprite
from examples.common import BackgroundModel, BackgroundSprite

from mvctools import NextStateException
from collections import OrderedDict

# Model

class SettingChoiceModel(ChoiceModel):

    def register_validation(self):
        attr = self.text.lower()
        setattr(self.control.settings, attr, self.current)

class SettingModel(BaseMenuModel):

    title = "Settings"

    setting_dct = OrderedDict()
    setting_dct["SIZE"] = ('800x600', '1024x768', "1280x720")
    setting_dct["MODE"] = ('WINDOWED', 'FULL')
    setting_dct["FPS"] = ('40', '60')

    choice_model_class = SettingChoiceModel
    entry_model_class = EntryModel

    def init(self):
        BaseMenuModel.init(self)
        self.bgd = BackgroundModel(self)
    
    @property
    def entry_data(self):
        # Choice model data
        iterator = enumerate(self.setting_dct.items())
        data = {pos: (self.choice_model_class, name, settings)
                    for pos, (name, settings) in iterator}
        # Entry model data
        iterator = enumerate(self.state.state_dct.items(), len(data))
        data.update({pos: (self.entry_model_class, name, state)
                         for pos, (name, state) in iterator})
        # Return data
        return data


# Sprite classes


class SettingSprite(BaseMenuSprite):
    
    font_ratio = 0.15
    font_name = "visitor2"
    font_color = "black"
    position_ratio = (0.5, 0.3)


# View class

class SettingView(BaseMenuView):
    bgd_color = "gray"
    bgd_image = None
    sprite_class_dct = {SettingChoiceModel: ChoiceSprite,
                        SettingModel: SettingSprite,
                        BackgroundModel: BackgroundSprite,
                        EntryModel : EntrySprite}
                        

# Loading state              

class SettingState(BaseMenuState):
    model_class = SettingModel
    view_class = SettingView
    state_dct = OrderedDict()

