# MVC imports
from mvctools import BaseView, AutoSprite, Animation, xytuple

# Model imports
from boardmodel import BlockModel, FloorModel, BlackHoleModel, \
                       BorderModel, PlayerModel, GoalModel

# Imports
from math import ceil

# Sprite classes

class TileSprite(AutoSprite):

    max_tile_x = 13
    max_tile_y = 14
    fixed = True

    def init(self):
        # Base size
        self.basesize = self.compute_basesize()
        # Shifting
        center = self.model.parent.max_coordinate * (0.5,0.5)
        shift = self.settings.size/(2,2) - self.isoconvert(center)
        shift += (0, self.basesize.y * 0.5)
        self.shift = shift.map(round).map(int)
        # Layer
        self.layer = self.compute_layer()
        # Raw ratio
        self.raw_ratio = None
    
    def get_rect(self):
        if not self.fixed or not self.rect: 
            pos = self.isoconvert(self.model.pos)
            return self.image.get_rect(midbottom=pos+self.shift)
        return self.rect

    def compute_layer(self):
        pos = self.model.pos
        return pos.x + pos.y

    def isoconvert(self, pos):
        pos = xytuple(pos.y-pos.x, pos.x+pos.y)
        pos *= self.basesize * (0.5, 0.5)
        return pos.map(round).map(int)

    def build_animation(self, resource, timer=None,
                        inf=None, sup=None, looping=True):
        self.raw_ratio = self.compute_raw_ratio(resource)
        return super(TileSprite, self).build_animation(resource, timer, inf,
                                                       sup, looping, True)

    def scale_resource(self, resource, name):
        self.raw_ratio = self.compute_raw_ratio(resource, name)
        return super(TileSprite, self).scale_resource(resource, name)
         
    @property
    def size(self):
        if self.rect.size != (0,0):
            return self.rect.size
        if self.raw_ratio is None:
            return xytuple(0,0)
        size = self.basesize * (1, self.raw_ratio * 3**0.5)
        return size.map(ceil).map(int)
    
    def compute_raw_ratio(self, resource, name=None):
        raw = resource.getfile(name) if name else resource[0]
        return float(raw.get_height()) / raw.get_width()

    def compute_basesize(self):
        width = float(self.settings.width)/self.max_tile_x
        coresponding_height = width / (3**0.5)
        height = float(self.settings.height)/self.max_tile_y
        if height > coresponding_height:
            return xytuple(width, coresponding_height)
        coresponding_width = height * (3**0.5)
        return xytuple(coresponding_width, height)

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

    def init(self):
        super(BlackHoleSprite, self).init()
        resource = self.resource.image.black_hole
        timer = self.model.timer
        self.animation = self.build_animation(resource, timer)

    def get_image(self):
        return self.animation.get()

class PlayerSprite(TileSprite):

    fixed = False
    moving_name = "moving_player"
    transform_name = "transforming_player"
    color_dct = {1 : "red",
                 2 : "green",}
    direction_dct = {(1, 0) : "sw",
                     (0, 1) : "se",
                     (0,-1) : "nw",
                     (-1,0) : "ne",}

    def init(self):
        super(PlayerSprite, self).init()
        # Base animation
        timer = self.model.timer
        resource_dct = {direction: self.get_folder(direction)
                        for direction in self.direction_dct}   
        self.animation_dct = {di: self.build_animation(re, timer)
                              for di ,re in resource_dct.items()}
        # Moving image
        self.moving_image = self.scale_resource(self.resource.image,
                                                self.moving_name)
        # Transforming animation
        transorm_resource = self.resource.image.getdir(self.transform_name)
        transform_timer  = self.model.transform_timer
        self.transform_animation = self.build_animation(transorm_resource,
                                                        transform_timer,
                                                        looping=False)

    def get_folder(self, direction):
        color = self.color_dct[self.model.id]
        name = "_".join((color, "player", self.direction_dct[direction]))
        return self.resource.image.getdir(name)

    def get_image(self):
        if self.model.on_goal:
            return
        if self.model.is_moving:
            return self.moving_image
        if self.model.is_transforming:
            return self.transform_animation.get()
        return self.animation_dct[self.model.dir].get()

    def get_layer(self):
        return self.compute_layer() + 0.5

class GoalSprite(TileSprite):

    period = 1.5
    color_dct = {1 : "red",
                 2 : "green",}

    def init(self):
        super(GoalSprite, self).init()
        self.layer += 0.001
        self.animation = self.build_animation(self.folder, self.model.timer,
                                              looping = False)
        
    @property
    def folder(self):
        color = self.color_dct[self.model.id]
        name = "_".join(("goal", color))
        return getattr(self.resource.image, name)

    def get_image(self):
        return self.animation.get()

class BorderSprite(TileSprite):

    def init(self):
        super(BorderSprite, self).init()
        self.image = self.scale_resource(self.resource.image, "border")


# View class

class BoardView(BaseView):
    bgd_color = "lightblue"
    sprite_class_dct = {BlockModel: BlockSprite,
                        FloorModel: FloorSprite,
                        BlackHoleModel: BlackHoleSprite,
                        BorderModel: BorderSprite,
                        PlayerModel: PlayerSprite,
                        GoalModel: GoalSprite}


