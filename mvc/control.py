import pygame, sys
from mvc.gamedata import BaseGamedata
from mvc.state import BaseState
from mvc.settings import BaseSettings
from mvc.resource import ResourceHandler

class BaseControl:

    settings_class = BaseSettings
    game_data_class = BaseGamedata
    first_state = None
    resource_dict = "resource"
    window_title = "Pygame"
    display_fps = True
    
    def __init__(self):
        self.next_state = self.first_state
        self.settings = BaseSettings()
        self.resource = ResourceHandler(self.resource_dict)
        self.current_state = None
        self.state_stack = []

    def load_next_state(self):
        if self.next_state:
            self.current_state = self.next_state(self)
            self.next_state = None
        elif self.state_stack:
            self.current_state = self.pop_state()
        else:
            self.current_state = None
        return self.current_state
        
    def run(self):
        # Prepare the run
        pygame.display.set_mode(self.settings.size)
        self.pre_run()
        # Loop over the states
        while self.load_next_state():
            try:
                self.current_state.run()
            except SystemExit:
                break
        self.safe_exit()

    def pre_run(self):
        pass

    def register_next_state(self, state):
        self.next_state = state

    def push_current_state(self):
        self.state_stack.append(self.current_state)

    def pop_state(self):
        try:
            return self.state_stack.pop()
        except IndexError:
            return None

    def get_fps(self):
        return self.settings.get_fps()

    @staticmethod
    def safe_exit():
        pygame.quit()
        


