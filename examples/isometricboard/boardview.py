# MVC imports
from mvctools.view import BaseView, AutoSprite, Animation
from mvctools.common import xytuple

# Model imports
from boardmodel import BlockModel, FloorModel, BlackHoleModel, \
                       BorderModel, PlayerModel, GoalModel

# Pygame imports
from pygame import Color
import pygame as pg

# Sprite classes

class TileSprite(AutoSprite):

    basesize_ratio = 0.08, 0.065

    def init(self):
        self.basesize = (self.settings.size*self.basesize_ratio).map(int)
        center = self.model.parent.max_coordinate * (0.5,0.5)
        shift = self.settings.size/(2,2) - self.isoconvert(center)
        shift += (0, self.basesize.y * 0.5)
        self.shift = shift.map(int)
    
    def get_rect(self):
        pos = self.isoconvert(self.model.pos)
        return self.image.get_rect(midbottom=pos+self.shift)

    def get_layer(self):
        pos = self.model.pos
        return pos.x * self.model.parent.nb_column + pos.y

    def isoconvert(self, pos):
        pos = xytuple(pos.y-pos.x, pos.x+pos.y)
        pos *= self.basesize * (0.5, 0.5)
        return pos.map(int)

    def scale_resource(self, folder, name):
        raw_image = folder.getfile(name)
        if raw_image:
            raw_ratio = float(raw_image.get_height()) / raw_image.get_width()
            size = self.get_size(raw_ratio)
        return folder.getfile(name, size)

    def build_animation(self, resource, timer=None, inf=None, sup=None, looping=True):
        if timer is None:
            timer = self.model.lifetime
        filenames = resource.getfilenames()
        resource = [self.scale_resource(resource, name) for name in filenames] 
        return Animation(resource, timer, inf, sup, looping)

    def get_size(self, raw_ratio):
        size = self.basesize * (1, raw_ratio * 3**0.5)
        return size.map(int)

class FloorSprite(TileSprite):

    color_dct = {0: "grey",
                 1: "red",
                 2: "green",
                 3: "yellow",}
    
    def init(self):
        super(FloorSprite, self).init()
        self.resource_dct = {key: self.get_resource(key)
                             for key in self.color_dct}

    def get_resource(self, key):
        filename = "_".join(("floor", self.color_dct[key]))
        folder = self.resource.image.floor
        return self.scale_resource(folder, filename)

    def get_image(self):
        return self.resource_dct[sum(self.model.activation_dct)]

class BlockSprite(TileSprite):

    def init(self):
        super(BlockSprite, self).init()
        self.image = self.scale_resource(self.resource.image, "block")

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
        return self.resource.image.getdir(name)

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
        self.animation = self.build_animation(self.folder, self.model.timer,
                                              looping = False)
        
    @property
    def folder(self):
        color = self.color_dct[self.model.id]
        name = "_".join(("goal", color))
        return getattr(self.resource.image, name)

    def get_layer(self):
        return super(GoalSprite, self).get_layer() + 0.5

    def get_image(self):
        return self.animation.get()

class BorderSprite(TileSprite):

    def init(self):
        super(BorderSprite, self).init()
        self.image = self.scale_resource(self.resource.image, "border")


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

