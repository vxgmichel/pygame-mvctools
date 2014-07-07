from mvctools.controller import BaseController
import pygame as pg

# Controller

class BoardController(BaseController):

    def handle_event(self, event):
        if event.type == pg.KEYDOWN and \
           event.key in [pg.K_SPACE, pg.K_RETURN]:
            self.model.register_validation()
