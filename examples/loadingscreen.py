from mvc.state import BaseState
from mvc.model import BaseModel
from mvc.controller import BaseController
from mvc.view import BaseView, AutoSprite

from pygame import Surface

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

    def init(self):
        self.font = self.resource.font.visitor2(45)
        self.renderer = lambda text: self.font.render(text, False, (0,0,0))
        self.image = self.renderer("Loading")
        width, height = self.settings.size
        br = width-60, height-10
        self.rect = self.image.get_rect(bottomright=br)
        self.logo = LoadingLogoSprite(self)
 

class LoadingLogoSprite(AutoSprite):

    def init(self):
        self.images = []
        self.renderer = self.parent.renderer
        self.images = [self.renderer("."*i) for i in xrange(1,6)]

    def get_image(self):
        factor = float(len(self.images) * 3)/self.model.total
        index = int(factor*self.model.index)%len(self.images)
        return self.images[index]

    def get_rect(self):
        return self.image.get_rect(topleft=self.parent.rect.topright)

# View class

class LoadingView(BaseView):
    sprite_class_dct = {LoadingModel: LoadingSprite}

    def get_background(self):
        white = (255, 255, 255)
        background = self.resource.image.ashred
        return self.control.settings.scale_as_background(background, white)

# Loading state              

class LoadingState(BaseState):
    model_class = LoadingModel
    controller_class = BaseController
    view_class = LoadingView

