from mvctools import BaseModel, BaseController, BaseView
from mvctools import BaseState, AutoSprite
from mvctools.utils import RendererSprite

# Model

class LoadingModel(BaseModel):

    text = "Loading"

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

# Main sprite class

class LoadingSprite(RendererSprite):
    
    font_ratio = 0.07
    font_name = "visitor2"
    font_color = "black"
    position_ratio = (0.85, 0.95)
    
    def init(self):
        RendererSprite.init(self)
        self.image = self.renderer(self.model.text)
        self.rect = self.image.get_rect(center=self.center)
        self.logo = LoadingLogoSprite(self)

    @property
    def center(self):
        return (self.settings.size * self.position_ratio).map(int)


# Secondary sprite class

class LoadingLogoSprite(AutoSprite):

    nb_dot = 5
    period = 2
    
    def init(self):
        self.renderer = self.parent.renderer
        self.images = [self.renderer("."*i) for i in xrange(1, self.nb_dot+1)]
        self.animation = self.build_animation(self.images, sup=self.period)

    def get_image(self):
        return self.animation.get()

    def get_rect(self):
        return self.image.get_rect(topleft=self.parent.rect.topright)

# View class

class LoadingView(BaseView):
    sprite_class_dct = {LoadingModel: LoadingSprite}
    bgd_color = "lightblue"
    bgd_image = "image/ashred.png"

# Loading state              

class LoadingState(BaseState):
    model_class = LoadingModel
    controller_class = BaseController
    view_class = LoadingView
    next_state = None

