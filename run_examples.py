"""Module to bind and run the different examples"""

# Imports
import pygame
from mvctools.control import BaseControl
from examples.loadingscreen import LoadingState
from examples.menuscreen import MenuState
from examples.board import BoardState
from examples.pausescreen import PauseState
from examples.settingscreen import SettingState
from examples.cputestscreen import CpuTestState

# Create the main control
class Example(BaseControl):
    """Main control for the example"""

    ressource_dir = "resource"
    window_title = "Example v1.0"

    def pre_run(self) :
        """Hide the mouse"""
        pygame.mouse.set_visible(False)


# Set the links between the different states
Example.first_state = LoadingState

LoadingState.next_state = MenuState

MenuState.state_dct["Play"] = BoardState
MenuState.state_dct["Settings"] = SettingState
MenuState.state_dct["CPUTest"] = CpuTestState
MenuState.state_dct["Quit"] = None


SettingState.state_dct["Back"] = MenuState

CpuTestState.state_dct["Back"] = MenuState

BoardState.next_state = MenuState
BoardState.pause_state = PauseState

# Run the example
if __name__ == "__main__":
    example = Example()
    example.gamedata.board_level = 0
    example.run()

