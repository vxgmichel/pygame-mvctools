from mvctools.model import BaseModel
from mvctools.view import AutoSprite
from pygame import Color, transform       

def cache(func):
    dct = {}
    def wrapper(arg):
        if arg not in dct:
            dct[arg] = func(arg)
        return dct[arg]
    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    return wrapper

class RendererSprite(AutoSprite):
    
    font_name = ""
    font_ratio = 0.0
    font_color = Color("black")
    native_ratio = None
  
    def init(self):
        self.renderer = self.build_renderer()

    @property
    def font_size(self):
        return int(self.settings.height * self.font_ratio)

    def build_renderer(self, name=None, size=None, color=None,
                             native_ratio=None, cached=True):
        # Check arguments
        name = self.font_name if name is None else name
        size = self.font_size if size is None else size
        color = self.font_color if color is None else color
        native_ratio = self.native_ratio if native_ratio is None else native
        # Load the font
        font = self.resource.font.getfile(name, size)
        # Get the renderer
        def renderer(text, native_ratio=native_ratio):
            # Render the text
            raw = font.render(text, False, color).convert_alpha()
            # No native ratio case
            if native_ratio is None:
                return raw
            # Ratio between native ratio and current ratio
            current_ratio = float(self.settings.width)/self.settings.height
            ratio = current_ratio/native_ratio
            # Already native case
            if ratio == 1:
                return raw
            # Scaling
            img_size = int(raw.get_width() * ratio), raw.get_height()
            return transform.smoothscale(raw, img_size)
        # Activate caching if needed
        if cached:
            return cache(renderer)
        return renderer
