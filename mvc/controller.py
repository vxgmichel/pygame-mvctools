import pygame as pg

class BaseController:
    def __init__(self, control, model):
        self.control = control
        self.model = model
        self.init()

    def init(self):
        pass
    
    def _update(self):
        for ev in pg.event.get():
            if self.handle_event(ev):
                return True

    def handle_event(self, event):
        if self.is_quit_event(event):
                return True

    def is_quit_event(self, event):
        return event.type == pg.QUIT
