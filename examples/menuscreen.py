from mvctools.utils.menu import BaseMenuModel, BaseMenuView, BaseEntryModel
from mvctools.utils.menu import BaseMenuState, BaseMenuSprite, BaseEntrySprite

from examples.common import EntryModel, EntrySprite
from examples.common import BackgroundModel, BackgroundSprite 

from collections import OrderedDict


# Model class

class MenuModel(BaseMenuModel):

    title = "Example v1.0"

    def init(self):
        BaseMenuModel.init(self)
        self.bgd = BackgroundModel(self)

    @property
    def entry_data(self):
        iterator = enumerate(self.state.state_dct.items())
        return {pos: (EntryModel, name, state)
                for pos, (name, state) in iterator}
            
# Sprite class


class MenuSprite(BaseMenuSprite):
    
    font_ratio = 0.15
    font_name = "visitor2"
    font_color = "black"
    position_ratio = (0.5, 0.3)
    

# View class

class MenuView(BaseMenuView):
    bgd_color = "lightblue"
    sprite_class_dct = {EntryModel: EntrySprite,
                        BackgroundModel: BackgroundSprite,
                        MenuModel: MenuSprite}

# Loading state              

class MenuState(BaseMenuState):
    model_class = MenuModel
    view_class = MenuView
    state_dct = OrderedDict([])

