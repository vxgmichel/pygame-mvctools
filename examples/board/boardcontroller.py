from mvctools import BaseController
import pygame as pg

# Controller

class BoardController(BaseController):

    validkey_mapping = {pg.K_SPACE: (1,),
                        pg.K_RETURN : (2,)}

    dirkey_mapping = {pg.K_w:     (1, -1,  0),
                      pg.K_d:     (1,  0,  1),
                      pg.K_s:     (1,  1,  0),
                      pg.K_a:     (1,  0, -1),
                      pg.K_UP:    (2, -1,  0),
                      pg.K_RIGHT: (2,  0,  1),
                      pg.K_DOWN:  (2,  1,  0),
                      pg.K_LEFT:  (2,  0, -1)}

    def handle_event(self, event):
        if event.type == pg.KEYDOWN and \
           event.key in [pg.K_ESCAPE,]:
            self.model.register_pause()
        if event.type == pg.KEYDOWN and \
           event.key in self.validkey_mapping:
            args = self.validkey_mapping[event.key]
            self.model.register_validation(*args)
        if event.type == pg.KEYDOWN and \
           event.key in self.dirkey_mapping:
            args = self.dirkey_mapping[event.key]
            self.model.register_direction(*args)
