import pygame
from mvc.control import BaseControl
from examples.loadingscreen import LoadingState, LoadingModel
from examples.menuscreen import MenuState, MenuModel
from examples.isometricboard import BoardState, BoardModel


class Example(BaseControl):
    first_state_type = LoadingState
    ressource_dir = "resource"
    window_title = "Example v1.0"

    def pre_run(self):
        pygame.mouse.set_visible(False)

LoadingModel.next_state = MenuState
MenuModel.state_dct["Play"] = BoardState
MenuModel.state_dct["Settings"] = MenuState
MenuModel.state_dct["Credits"] = MenuState
MenuModel.state_dct["Quit"] = None
BoardModel.next_state = MenuState
    
if __name__ == "__main__":
    example = Example()
    example.run()
