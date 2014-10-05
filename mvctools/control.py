"""Module for the state control related objects."""

# Imports
import pygame, sys
from mvctools.gamedata import BaseGamedata
from mvctools.state import BaseState, NextStateException
from mvctools.settings import BaseSettings
from mvctools.resource import ResourceHandler


# Base class
class BaseControl:
    """Base class for the state control.

    Its main puprpose is to run the states and handle the transitions between
    them. It provides for instance a method to register the next state to run.
    It also allows to stack/unstack states for purpose of menuing.

    It owns the data common to all the states such as:
     - **self.settings**: the game settings
     - **self.gamedata**: the data shared between the states
     - **self.resource**: the game resources

    These class attributes may be useful to override:
     - **settings_class** : Class to handle the settings
       (default is BaseSettings)
     - **gamedata_class** : Class to handle the settings
       (default is BaseGamedata)
     - **fist_state** : Class of the first state to instantiate and run.
       (default is None)
     - **resource_dict** : name of the resource folder
       (default is "resource")
     - **window_title** : title of the window
       (default is "Pygame")
     - **display_fps** : display the fps rate in the window title
       (default is True)

    This method may also be useful to override:
     - **pre_run** : code to run after the video mode is set and before the
       first state is instantiated

    These methods can be called from the states or their mvc:
     - **push_current_state** : push the current state into the stack
     - **register_next_state** : register the class of the next state to
       instantiate and run
    
    Some important points to know about the control creating the next state:
     - The registered state is automatically unregistered when instanciated
     - If no state is registered, the next state is poped from the stack
     - In that case, if the stack is empty, the program ends properly

    To launch the game, simply call the method run.

    Example: ::
    
        # Create the main control
        class Example(BaseControl):

            window_title = "Example v1.0"
            first_state = SomeState
            
            def pre_run(self) :
                pygame.mouse.set_visible(False)
            
        # Run the main control
        example = Example()
        example.run()
    """

    # Class attributes
    settings_class = BaseSettings
    gamedata_class = BaseGamedata
    first_state = None
    resource_dict = "resource"
    window_title = "Pygame"
    display_fps = True
    
    def __init__(self):
        """Initialize the state control."""
        self.next_state = self.first_state
        self.settings = self.settings_class(self)
        self.gamedata = self.gamedata_class()
        self.resource = ResourceHandler(self.resource_dict)
        self.current_state = None
        self.state_stack = []

    def load_next_state(self):
        """Load the next state.

        Note the following:
         - The registered state is automatically unregistered when instanciated
         - If no state is registered, the next state is poped from the stack
         - In that case, if the stack is empty, the program ends properly
        """
        if self.next_state:
            self.current_state = self.next_state(self)
            self.next_state = None
        elif self.state_stack:
            self.current_state = self.pop_state()
            self.reload()
        else:
            self.current_state = None
        return self.current_state

    def reload(self):
        """Reload current state."""
        if self.current_state:
            self.current_state.reload()

    def full_reload(self):
        """Fully reload current state if it is active."""
        if self.current_state and self.current_state.ticking:
            self.push_current_state()
            raise NextStateException
        
    def run(self):
        """Run the game."""
        # Prepare the run
        self.settings.set_mode()
        self.pre_run()
        # Loop over the states
        while self.load_next_state():
            try:
                self.current_state.run()
            except SystemExit:
                break
        # Exit safely
        self.safe_exit()

    def pre_run(self):
        """ Empty method to override.

        This code is executed after the video mode is set and before the first
        state is instantiated.
        """
        pass

    def register_next_state(self, state):
        """Register the class of the next state to instantiate and run.

        Args:
            state (type): the class of the next state to instantiate and run
        """
        self.next_state = state

    def push_current_state(self):
        """Push the current state into the stack."""
        self.state_stack.append(self.current_state)

    def pop_state(self):
        """Pop the last-in state from the stack."""
        try:
            return self.state_stack.pop()
        except IndexError:
            return None

    def get_fps(self):
        """Get the current fps rate setting."""
        return self.settings.get_fps()

    @staticmethod
    def safe_exit():
        """Exit pygame safely."""
        pygame.quit()
        

