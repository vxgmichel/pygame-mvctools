import pygame as pg

class BaseController:
    def __init__(self, state, model):
        self.state = state
        self.control = self.state.control
        self.model = model
        self.init()

    def init(self):
        pass
    
    def _update(self):
        for ev in pg.event.get():
            if self._handle_event(ev):
                return True

    def _handle_event(self, event):
        if self.is_quit_event(event):
                raise SystemExit
        return self.handle_event(event)

    def handle_event(self, event):
        pass

    def is_quit_event(self, event):
        return event.type == pg.QUIT
