
import pygame
from mvc.model import BaseModel
from mvc.controller import BaseController
from mvc.view import BaseView


class NextStateException(Exception):
    pass

class BaseState:
    model_class = BaseModel
    controller_class = BaseController
    view_class = BaseView
    clock_class = pygame.time.Clock
    
    def __init__(self, control):
        self.control = control
        self.model = self.model_class(control)
        self.controller = self.controller_class(control, self.model)
        self.view = self.view_class(control, self.model)

    def tick(self):
        mvc = self.controller, self.model, self.view
        try:
            return any(entity.update() for entity in mvc)
        except NextStateException:
            return False

    def run(self):
        clock = self.clock_class()
        fps_func = self.control.get_fps
        self.view.check_screen()
        while not self.tick():
            clock.tick(fps_func())

        
