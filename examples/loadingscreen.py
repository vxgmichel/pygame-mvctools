from mvc.state import BaseState
from mvc.model import BaseModel
from mvc.controller import BaseController
from mvc.view import BaseView, AutoSprite
from pygame import Color

# Model

class LoadingModel(BaseModel):

    def init(self):
        # Simulate a resource loader
        self.total = 500
        self.resource_loader = iter(xrange(self.total))
        self.index = 0
        
    def update(self):
        # Load a ressource
        self.index = next(self.resource_loader, None)
        # Stop case
        if self.index is None:
            self.control.register_next_state(LoadingState)
            return True
        

# Sprite classes

class LoadingSprite(AutoSprite):
    
    font_ratio = 0.05
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
        return int(self.settings.width * self.font_ratio)

    @property
    def center(self):
        return (self.settings.size * self.position_ratio).map(int)

    def build_renderer(self):
        font = getattr(self.resource.font, self.font_name)(self.font_size)
        return lambda text: font.render(text, False, self.font_color)
 

class LoadingLogoSprite(AutoSprite):

    nb_dot = 5
    nb_cycle = 3
    
    def init(self):
        self.images = []
        self.renderer = self.parent.renderer
        self.images = [self.renderer("."*i) for i in xrange(1, self.nb_dot+1)]

    def get_image(self):
        factor = float(len(self.images) * self.nb_cycle)/self.model.total
        index = int(factor*self.model.index)%len(self.images)
        return self.images[index]

    def get_rect(self):
        return self.image.get_rect(topleft=self.parent.rect.topright)

# View class

class LoadingView(BaseView):
    sprite_class_dct = {LoadingModel: LoadingSprite}
    bgd_color = Color("white")
    bgd_name = "ashred"

    def get_background(self):
        background = getattr(self.resource.image, self.bgd_name)
        return self.settings.scale_as_background(background, self.bgd_color)

# Loading state              

class LoadingState(BaseState):
    model_class = LoadingModel
    controller_class = BaseController
    view_class = LoadingView

