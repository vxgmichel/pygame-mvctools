from mvctools import MouseController, BaseModel, BaseView, BaseState
from mvctools import cursoredlist
from mvctools.utils.text import TextSprite
from collections import defaultdict
import pygame as pg


# Entry model

class EntryModel(BaseModel):
    
    def init(self, pos, text):
        self.text = text
        self.pos = pos

    @property
    def selected(self):
        return self is self.parent.cursor.get()

    def select(self):
        self.parent.cursor.cursor = self.pos

    def activate(self):
        pass

    def shift(self, shift):
        pass

    def register_hover(self):
        self.select()

    def register_click(self):
        self.activate()
        

# Main Model

class MenuModel(BaseModel):

    entry_data = {}

    def init(self):
        self.entry_dct = {pos: self.generate_entry(pos, data)
                          for pos, data in self.entry_data.items()}
        entry_lst = (value for _, value in sorted(self.entry_dct.items()))
        self.cursor = cursoredlist(entry_lst)

    def generate_entry(self, pos, data):
        model = data[0]
        args = (pos,) + data[1:]
        return model(self, *args)

    def register_dir(self, direct, player=None):
        x,y = direct
        self.cursor.inc(x)
        self.cursor.get.shift(y)

    def register_activate(self):
        self.cursor.get().activate()

    def register_back(self):
        self.cursor[-1].activate()
        
# Entry sprite

@from_parent(["font_size_dict", "font_name", "antialias", "color", "opacity"])
class EntrySprite(LineSprite):

    margins = 0,0
    alignment = "left"

    def get_max_size(self):
        font_dir = self.settings.font_dir
        resource = self.resource.getdir(font_dir)
        size = max(self.font_size_dict.values())
        font = resource.getfile(self.font_name, size)
        raw = self.render(font, self.text, self.antialias,
                          self.color, self.background)
        return raw.get_size()

    @property
    def text(self):
        return self.model.text

    @property
    def font_size(self):
        return self.font_size_dict[self.model.selected]

    @property
    def reference(self):
        return self.parent.get_child_reference(self.model.pos)

    @property
    def pos(self):
        return self.parent.get_child_pos(self.model.pos)
    
# Entry View

class EntryView(BaseView):

    sprite_class_dct = {EntryModel: EntrySprite}
    
    # Font
    font_size = 0
    font_name = ""
    # Renderer
    antialias = True
    color = "black"
    # Processing
    opacity = 1.0
    # Position
    pos = 0,0
    reference = "center"
    alignment = "left"
    # Margins
    margins = 0,0

    def update(self):
        for sprite in self.group:
            max_size = sprite.get_max_size()
            dct +=

    @property
    def get_child_reference(self, pos):
        if self.alignment in ["center", "centerx"]:
            return "center"
        if self.alignment in ["left", "right"]:
            return "mid" + self.alignment
        raise ValueError('Not a valid alignment')

    @property
    def get_child_pos(self, pos):
        return self.position_dict[pos]
    
    @property
    def size(self):
        try:
            return self.max_size
        except AttributeError:
            return xytuple(0, 0)


@from_parent(["font_size", "font_name", "antialias", "color",
              "opacity", "text", "margins", "alignment"])
class ChildrenTextView(TextView):
    """"""
    pass

class MenuSprite(ViewSprite):

    # Font
    font_size = 0
    font_name = ""
    # Renderer
    antialias = True
    color = "black"
    # Processing
    opacity = 1.0
    # Position
    pos = 0, 0
    reference = "center"
    alignment = "left"
    # Margin
    margins = 0, 0
    

    # View
    view_cls = ChildrenEntryView

    def init(self, **kwargs):
        ViewSprite.init(self)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_rect(self):
        kwargs = {self.reference: self.pos}
        return self.image.get_rect(**kwargs)


