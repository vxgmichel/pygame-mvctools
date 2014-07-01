import pygame
from mvc.control import BaseControl
from examples.loadingscreen import LoadingState
from examples.menuscreen import MenuState
from examples.isometricboard import BoardState


class Example(BaseControl):
    ressource_dir = "resource"
    window_title = "Example v1.0"

    def pre_run(self) :
        pygame.mouse.set_visible(False)
        
Example.first_state = LoadingState
LoadingState.next_state = MenuState
MenuState.state_dct["Play"] = BoardState
MenuState.state_dct["Settings"] = MenuState
MenuState.state_dct["Credits"] = MenuState
MenuState.state_dct["Quit"] = None
BoardState.next_state = MenuState
    
if __name__ == "__main__":
    example = Example()
    example.run()
