
import pygame
from mvctools.model import BaseModel
from mvctools.controller import BaseController
from mvctools.view import BaseView


class NextStateException(Exception):
    pass

class BaseState:
    model_class = BaseModel
    controller_class = BaseController
    view_class = BaseView
    clock_class = pygame.time.Clock
    
    def __init__(self, control):
        self.control = control
        self.model = self.model_class(self)
        self.controller = self.controller_class(self, self.model)
        self.view = self.view_class(self, self.model)

    def tick(self):
        mvc = self.controller, self.model, self.view
        try:
            return any(entity._update() for entity in mvc)
        except NextStateException:
            return True

    def run(self):
        # Display fps
        if self.control.display_fps:
            string = self.control.window_title + "   FPS = {:3}"
        else:
            string = None
        clock = self.clock_class()
        self.view.check_screen()
        while not self.tick():
            clock.tick(self.control.settings.fps)
            if string:
                caption = string.format(int(clock.get_fps()))
                pygame.display.set_caption(caption)
            

        
