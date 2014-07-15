# MVC imports
from mvctools.view import BaseView, AutoSprite
from mvctools.common import xytuple

# Model imports
from boardmodel import BlockModel, FloorModel, BlackHoleModel, \
                       BorderModel, PlayerModel, GoalModel

# Pygame imports
from pygame import Color
import pygame as pg

# Sprite classes

class TileSprite(AutoSprite):

    adjustment = 0.75
    size_ratio = 0.08, 0.065

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
        pos = xytuple(pos.y-pos.x, pos.x+pos.y)
        pos *= self.size * (0.5, 0.5)
        return pos.map(int)

    def scale(self, image):
        ratio = float(image.get_height())/image.get_width()
        size = self.size * (1, ratio * 3**0.5)
        return pg.transform.smoothscale(image, size.map(int))

class FloorSprite(TileSprite):

    color_dct = {0: "grey",
                 1: "red",
                 2: "green",
                 3: "yellow",}
    
    def init(self):
        super(FloorSprite, self).init()
        self.resource_dct = {key: self.scale(self.get_resource(key))
                             for key in self.color_dct}

    def get_resource(self, key):
        name = "_".join(("floor", self.color_dct[key]))
        return getattr(self.resource.image.floor, name)

    def get_image(self):
        return self.resource_dct[sum(self.model.activation_dct)]

class BlockSprite(TileSprite):

    def init(self):
        super(BlockSprite, self).init()
        self.image = self.scale(self.resource.image.block)

class BlackHoleSprite(TileSprite):

    period = 1.5

    def init(self):
        super(BlackHoleSprite, self).init()
        resource = self.resource.image.black_hole
        self.animation = self.build_animation(resource, sup=self.period)

    def get_image(self):
        return self.animation.get()

class PlayerSprite(TileSprite):

    period = 1.5
    color_dct = {1 : "red",
                 2 : "green",}
    direction_dct = {(1, 0) : "sw",
                     (0, 1) : "se",
                     (-1,0) : "nw",
                     (0,-1) : "ne",}

    def init(self):
        super(PlayerSprite, self).init() 
        resource_dct = {direction: self.get_folder(direction)
                        for direction in self.direction_dct}   
        self.animation_dct = {di: self.build_animation(re, sup=self.period)
                              for di ,re in resource_dct.items()}   

    def get_folder(self, direction):
        color = self.color_dct[self.model.id]
        name = "_".join((color, "player", self.direction_dct[direction]))
        return getattr(self.resource.image, name)

    def get_image(self):
        return self.animation_dct[self.model.dir].get()

    def get_layer(self):
        return super(PlayerSprite, self).get_layer() + 0.5

class GoalSprite(TileSprite):

    period = 1.5
    color_dct = {1 : "red",
                 2 : "green",}

    def init(self):
        super(GoalSprite, self).init() 
        self.images = [self.scale(image) for image in self.folder]
        self.image = self.images[0]
        
    @property
    def folder(self):
        color = self.color_dct[self.model.id]
        name = "_".join(("goal", color))
        return getattr(self.resource.image, name)

    def get_layer(self):
        return super(GoalSprite, self).get_layer() + 0.5

class BorderSprite(TileSprite):

    def init(self):
        super(BorderSprite, self).init()
        self.image = self.scale(self.resource.image.border)


# View class

class BoardView(BaseView):
    bgd_color = Color("lightblue")
    sprite_class_dct = {BlockModel: BlockSprite,
                        FloorModel: FloorSprite,
                        BlackHoleModel: BlackHoleSprite,
                        BorderModel: BorderSprite,
                        PlayerModel: PlayerSprite,
                        GoalModel: GoalSprite}

    def get_background(self):
        return self.settings.scale_as_background(color=self.bgd_color)

