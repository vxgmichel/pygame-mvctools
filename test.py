from mvc.state import BaseState
from mvc.control import BaseControl
from mvc.model import BaseModel
from mvc.controller import BaseController
from mvc.view import BaseView

class StageModel(BaseModel):
    pass

class StageController(BaseController):
    pass

class StageView(BaseView):
    pass

class StageState(BaseState):
    model_class = StageModel
    controller_class = StageController
    view_class = StageView

class PortTales(BaseControl):
    first_state_type = StageState

    
if __name__ == "__main__":
    import pygame
    pygame.display.set_mode((100,200))
    PortTales().run()
