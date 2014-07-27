from mvctools.state import BaseState
from mvctools.model import BaseModel
from mvctools.controller import BaseController
from mvctools.view import BaseView, AutoSprite
from pygame import Color

from menuscreen import MenuState

# Model

class LoadingModel(BaseModel):

    def init(self):
        super(LoadingModel, self).init()
        self.done = False
        self.control.resource.load(threaded=True, callback=self.callback)
        
    def update(self):
        if self.done:
            self.control.register_next_state(self.state.next_state)
            return True

    def callback(self):
        self.done = True

# Sprite classes

class LoadingSprite(AutoSprite):
    
    font_ratio = 0.07
    font_name = "visitor2"
    font_text = "Loading"
    font_color = Color("black")
    position_ratio = (0.85, 0.95)
    
    def init(self):
        self.renderer = self.build_renderer()
        self.image = self.renderer(self.font_text)
        self.rect = self.image.get_rect(center=self.center)
        self.logo = LoadingLogoSprite(self)

    @property
    def font_size(self):
        return int(self.settings.height * self.font_ratio)

    @property
    def center(self):
        return (self.settings.size * self.position_ratio).map(int)

    def build_renderer(self):
        font = self.resource.font.getfile(self.font_name, self.font_size)
        return lambda text: font.render(text, False, self.font_color)
 

class LoadingLogoSprite(AutoSprite):

    nb_dot = 5
    period = 2
    
    def init(self):
        self.images = []
        self.renderer = self.parent.renderer
        self.images = [self.renderer("."*i).convert_alpha()
                       for i in xrange(1, self.nb_dot+1)]
        self.animation = self.build_animation(self.images, sup=self.period)

    def get_image(self):
        return self.animation.get()

    def get_rect(self):
        return self.image.get_rect(topleft=self.parent.rect.topright)

# View class

class LoadingView(BaseView):
    sprite_class_dct = {LoadingModel: LoadingSprite}
    bgd_color = Color("lightblue")
    bgd_name = "ashred"

    def get_background(self):
        background = getattr(self.resource.image, self.bgd_name)
        return self.settings.scale_as_background(background, self.bgd_color)

# Loading state              

class LoadingState(BaseState):
    model_class = LoadingModel
    controller_class = BaseController
    view_class = LoadingView
    next_state = None

