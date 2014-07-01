from mvc.state import BaseState, NextStateException
from mvc.model import BaseModel
from mvc.controller import BaseController
from mvc.view import BaseView, AutoSprite
from mvc.common import Cursor, XY

from pygame import Color, Rect
import pygame as pg

# Controller

class BoardController(BaseController):

    def handle_event(self, event):
        if event.type == pg.KEYDOWN and \
           event.key in [pg.K_SPACE, pg.K_RETURN]:
            self.model.register_validation()

# Model

class TileModel(BaseModel):
    
    def init(self, pos):
        self._pos = pos

    @property
    def pos(self):
        return XY(*self._pos)

    @pos.setter
    def pos(self, value):
        self._pos = XY(*value)
        

class BlockModel(TileModel):
    pass

class FloorModel(TileModel):
    pass

class BorderModel(TileModel):
    pass

class BoardModel(BaseModel):

    next_state = None
    type_dct = {-1: BorderModel,
                 1: FloorModel,
                 6: BlockModel}
    board = [[6,1,1,6],
             [1,1,1,1],
             [1,1,1,6]]

    def init(self):
        self.tile_dct = self.build_tiles(self.board)
        self.max_coordinate = XY(*max(self.tile_dct))
        self.nb_line = self.max_coordinate.x + 1
        self.nb_column = self.max_coordinate.x + 1
    
    def register_validation(self):
        self.control.register_next_state(self.next_state)
        raise NextStateException

    def build_tiles(self, mat):
        if mat[0][0] != -1:
            mat = self.add_border(mat)
        return {(i,j): self.type_dct[element](self, (i,j))
                    for i, line in enumerate(mat)
                        for j, element in enumerate(line)}

    @staticmethod
    def parse(filename):
        with open_resource(filename) as f:
            next(line for line in f if line.startswith("data="))
            parse_line = lambda line: [int(x) for x in line.strip().split(",") if x]
            return [parse_line(line) for line in f if "," in line]

    @staticmethod
    def add_border(mat):
        res = [[-1] * (2 + len(mat[0]))]
        for x in mat:
            res.append([-1] + x + [-1])
        res.append([-1] * (2 + len(mat[0])))
        return res
                              
# Sprite classes

class TileSprite(AutoSprite):

    adjustment = 0.75
    size_ratio = 0.15, 0.1
    initial_ratio = 141.0/216

    def init(self):
        self.size = (self.settings.size*self.size_ratio).map(int)
        center = self.model.parent.max_coordinate * (0.5,0.5)
        center += (self.adjustment,)*2
        shift = self.settings.size/(2,2) - self.isoconvert(center)
        self.shift = shift.map(int)
    
    def get_rect(self):
        pos = self.isoconvert(self.model.pos)
        return self.image.get_rect(center=pos+self.shift)

    def get_layer(self):
        pos = self.model.pos
        return pos.x * self.model.parent.nb_column + pos.y

    def isoconvert(self, pos):
        pos = XY(pos.y-pos.x, pos.x+pos.y)
        pos *= self.size * (0.5, 0.5)
        return pos.map(int)

    def scale(self, image):
        ratio = float(image.get_height())/image.get_width()
        size = self.size * (1, ratio * 3**0.5)
        return pg.transform.smoothscale(image, size.map(int))

class FloorSprite(TileSprite):
    
    def init(self):
        super(FloorSprite, self).init()
        self.image = self.scale(self.resource.image.floor)

class BlockSprite(TileSprite):

    def init(self):
        super(BlockSprite, self).init()
        self.image = self.scale(self.resource.image.block)

class BorderSprite(TileSprite):

    def init(self):
        super(BorderSprite, self).init()
        self.image = self.scale(self.resource.image.border)


# View class

class BoardView(BaseView):
    bgd_color = Color("white")
    sprite_class_dct = {BlockModel: BlockSprite,
                        FloorModel: FloorSprite,
                        BorderModel: BorderSprite}

    def get_background(self):
        return self.settings.scale_as_background(color = self.bgd_color)

# Loading state              

class BoardState(BaseState):
    model_class = BoardModel
    controller_class = BoardController
    view_class = BoardView

