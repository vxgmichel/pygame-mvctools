import pygame as pg

class BaseController:
    def __init__(self, control, model):
        self.control = control
        self.model = model
    
    def update(self):
        for ev in pg.event.get():
            if self.is_quit_event(ev):
                return True

    def is_quit_event(self, event):
        return event.type == pg.QUIT
