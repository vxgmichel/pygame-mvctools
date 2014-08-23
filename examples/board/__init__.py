from mvctools.state import BaseState
from boardmodel import BoardModel
from boardcontroller import BoardController
from boardview import BoardView
              
class BoardState(BaseState):
    model_class = BoardModel
    controller_class = BoardController
    view_class = BoardView
    next_state = None
    pause_state = None

