"""Module for the state control related objects."""

# Imports
import pygame, argparse, os
from mvctools.gamedata import BaseGamedata
from mvctools.state import BaseState, NextStateException
from mvctools.settings import BaseSettings
from mvctools.resource import ResourceHandler


# Base class
class BaseControl(object):
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
     - **resource_dir** : name of the resource folder
       (default is "resource")
     - **window_title** : title of the window
       (default is "Pygame")

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
                super(Example, self).pre_run()
                pygame.mouse.set_visible(False)

        # Run the main control
        example = Example()
        example.run()
    """

    # Class attributes
    settings_class = BaseSettings
    gamedata_class = BaseGamedata
    first_state = None
    resource_dir = "resource"
    window_title = "Pygame"
    version = None
    description = None

    def __init__(self):
        """Initialize the state control."""
        self.next_state = self.first_state
        self.settings = self.settings_class(self)
        self.gamedata = self.gamedata_class()
        resource_dir = os.path.join(self.root_dir, self.resource_dir)
        self.resource = ResourceHandler(resource_dir)
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
            self.current_state.reload()
        else:
            self.current_state = None
        return self.current_state

    def reload_state(self, fully=True):
        """Fully reload the current state."""
        if not self.current_state:
            return
        if fully:
            self.register_next_state(type(self.current_state))
        else:
            self.push_current_state()
        if self.current_state.ticking:
            raise NextStateException

    def main(self):
        """Parse the command line arguments and run the game."""
        description = self.description or self.__doc__
        formatter_class = argparse.RawDescriptionHelpFormatter
        parser = argparse.ArgumentParser(description=description,
                                         formatter_class=formatter_class)
        if self.version:
            parser.add_argument('--version',
                                action='version',
                                version=self.version)
        self.settings.parse_arguments(parser)
        return self.run()


    def run(self):
        """Run the game."""
        # Prepare the run
        self.pre_run()
        # Loop over the states
        while self.load_next_state():
            try:
                self.current_state.run()
                self.current_state.clean()
            except SystemExit:
                break
            self.debug()
        # Exit safely
        self.safe_exit()


    def debug(self):
        import gc, pprint
        from mvctools import AutoSprite
        pp = pprint.PrettyPrinter(indent=4)
        for s in gc.get_objects():
            if isinstance(s, AutoSprite):
                print s, len(gc.get_referrers(s))

    def pre_run(self):
        """Method to override.

        This initializes the video mode.
        """
        flag = pygame.FULLSCREEN if self.settings.fullscreen else 0
        pygame.display.set_mode(self.settings.size, flag)
        pygame.display.set_caption(self.window_title)

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

    @property
    def root_dir(self):
        """Get the parent directory of the top-level package."""
        if not self.__module__:
            return ""
        root_module = __import__(self.__module__.split(".")[0])
        return os.path.join(root_module.__path__[0], os.pardir)

    @classmethod
    def setup(cls, **kwargs):
        """Convenience setup script based on setuptools.setup."""
        from setuptools import setup, find_packages
        # Get data
        script_name = cls.__name__
        main = ":".join((cls.__module__.split('.')[0], "main"))
        script = "=".join((script_name, main))
        # Set missing keyword arguments
        kwargs.setdefault("version", cls.version)
        kwargs.setdefault("description", cls.description or cls.__doc__)
        kwargs.setdefault("entry_points", {'gui_scripts': [script]})
        kwargs.setdefault("packages", find_packages())
        kwargs.setdefault("data_files", cls.find_data_files())
        # Run setup
        setup(**kwargs)

    @classmethod
    def find_data_files(cls):
        """Enumerate all files in the resource directory."""
        return [(path, [path+os.sep+f for f in files])
                for path, _, files in os.walk(cls.resource_dir)]

    @staticmethod
    def safe_exit():
        """Exit pygame safely."""
        pygame.quit()


