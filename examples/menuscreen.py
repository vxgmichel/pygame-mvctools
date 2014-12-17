from mvctools.utils import MenuModel, MenuSprite, EntrySprite, LineSprite
from mvctools import BaseState, MouseController, BaseView, BaseModel
from examples.common import BackgroundModel, BackgroundSprite, StateEntryModel 

from collections import OrderedDict


# Model class

class TitleModel(BaseModel):

    title = "Example v1.0"

    def init(self):
        self.bgd = BackgroundModel(self)
        self.menu = StateMenuModel(self)


class StateMenuModel(MenuModel):

    @property
    def entry_data(self):
        iterator = enumerate(self.state.state_dct.items())
        return {pos: (StateEntryModel, name, state)
                for pos, (name, state) in iterator}
            
# Sprite class


class StateMenuSprite(MenuSprite):
    
    # Entries
    font_sizes = 100, 150
    font_name = "visitor2"
    font_color = "black"
    margins = 100, 0

    # Position
    reference = "center"
    position_ratio = 0.5, 0.65
    size_ratio = 0.4, 0.4
    
    @property
    def pos(self):
        return (self.screen_size * self.position_ratio).map(int)

    @property
    def size(self):
        return (self.screen_size * self.size_ratio).map(int)

class TitleSprite(LineSprite):
    
    # Entries
    size_ratio = 0.2
    font_name = "visitor2"
    color = "black"

    # Position
    reference = "center"
    position_ratio = 0.5, 0.25
    
    @property
    def pos(self):
        return (self.screen_size * self.position_ratio).map(int)

    @property
    def font_size(self):
        return int(self.screen_height * self.size_ratio)

    @property
    def text(self):
        return self.model.title
    

# View class

class TitleView(BaseView):
    bgd_color = "lightblue"
    sprite_class_dct = {TitleModel: TitleSprite,
                        BackgroundModel: BackgroundSprite,
                        StateMenuModel: StateMenuSprite}

# Loading state              

class MenuState(BaseState):
    model_class = TitleModel
    view_class = TitleView
    controller_class = MouseController
    state_dct = OrderedDict([])

