from mvctools.sprite import AutoSprite
from mvctools.common import cache
from pygame import Color, transform


class RendererSprite(AutoSprite):
    
    font_folder = "font"
    font_name = ""
    font_ratio = 0.0
    font_color = "black"
  
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
        color = Color(color)
        if native_ratio is None:
            native_ratio = self.settings.native_ratio
        # Load the font
        font = self.resource.getdir(self.font_folder).getfile(name, size)
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
