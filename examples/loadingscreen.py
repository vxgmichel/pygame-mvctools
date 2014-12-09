from mvctools import BaseModel, BaseController, BaseView
from mvctools import BaseState, AutoSprite, Timer
from mvctools.utils import TextSprite

# Model

class LoadingModel(BaseModel):

    basetext = "Loading"
    period = 1
    length = 5

    def init(self):
        super(LoadingModel, self).init()
        self.done = False
        self.control.resource.load(threaded=True, callback=self.callback)
        self.timer = Timer(self, stop=self.period, periodic=True).start()

    @property
    def text(self):
        nb_dots = int(self.length * self.timer.get(normalized=True))
        return self.basetext + "." * nb_dots
    
    def update(self):
        if self.done:
            self.control.register_next_state(self.state.next_state)
            return True

    def callback(self):
        self.done = True

# Main sprite class

class LoadingSprite(TextSprite):
    
    font_ratio = 0.07
    font_name = "visitor2"
    color = "black"
    reference = "midleft"
    position_ratio = (0.8, 0.95)

    @property
    def text(self):
        return self.model.text

    @property
    def font_size(self):
        return int(self.screen_height * self.font_ratio)

    @property
    def pos(self):
        return (self.screen_size * self.position_ratio).map(int)


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

