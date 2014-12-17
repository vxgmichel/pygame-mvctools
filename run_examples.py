"""Module to bind and run the different examples"""

# Imports
import pygame
from mvctools import BaseControl
from examples.loadingscreen import LoadingState
from examples.menuscreen import MenuState
from examples.board import BoardState
from examples.pausescreen import PauseState
#from examples.settingscreen import SettingState
#from examples.cputestscreen import CpuTestState

# Create the main control
class Example(BaseControl):
    """Main control for the example"""

    ressource_dir = "resource"
    window_title = "Example v1.0"


# Set the links between the different states
Example.first_state = MenuState
LoadingState.next_state = BoardState

MenuState.state_dct["Play"] = BoardState
MenuState.state_dct["Settings"] = BoardState
MenuState.state_dct["CPUTest"] = BoardState
MenuState.state_dct["Quit"] = None

#BoardState.next_state = MenuState
BoardState.pause_state = PauseState

# Run the example
if __name__ == "__main__":
    example = Example()
    example.gamedata.board_level = 0
    example.main()

