"""Module to run the different state examples"""

# Imports
import pygame
from mvctools.control import BaseControl
from examples.loadingscreen import LoadingState
from examples.menuscreen import MenuState
from examples.isometricboard import BoardState

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
MenuState.state_dct["Settings"] = MenuState
MenuState.state_dct["Credits"] = MenuState
MenuState.state_dct["Quit"] = None
BoardState.next_state = MenuState

# Run the example  
if __name__ == "__main__":
    example = Example()
    example.run()
