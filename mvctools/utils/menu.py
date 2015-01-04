from mvctools import MouseController, BaseModel, BaseView, BaseState
from mvctools.sprite import ViewSprite
from mvctools.common import cursoredlist, from_parent, xytuple
from mvctools.utils.text import LineSprite
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

@from_parent(["font_sizes", "font_name", "antialias",
              "color", "opacity", "reference"])
class EntrySprite(LineSprite):

    margins = 0,0
    alignment = "left"

    def get_max_rect(self):
        font_dir = self.settings.font_dir
        resource = self.resource.getdir(font_dir)
        font = resource.getfile(self.font_name, max(self.font_sizes))
        raw = self.render(font, self.text, self.antialias,
                          self.color, self.background)
        return raw.get_rect()

    @property
    def text(self):
        return self.model.text

    @property
    def font_size(self):
        return self.font_sizes[self.model.selected]

    @property
    def pos(self):
        return self.parent.get_child_pos(self.model.pos)
    
# Entry View

class MenuView(BaseView):

    sprite_class_dct = {EntryModel: EntrySprite}
    
    # Font
    font_sizes = 0, 0
    font_name = ""
    # Renderer
    antialias = True
    color = "black"
    # Processing
    opacity = 1.0
    alignment = "left"
    # Margins
    margins = 0,0
    
    def update(self):
        self.rect_dict = {}
        # Get rects
        for sprite in self.group:
            rect = sprite.get_max_rect()
            pos = xytuple(self.margins)
            pos += 0, rect.h
            pos *= (sprite.model.pos,) * 2
            setattr(rect, self.reference, pos)
            self.rect_dict[sprite.model.pos] = rect
        # Move rects
        if not self.rect_dict:
            return
        x = - min(rect.x for rect in self.rect_dict.values())
        y = - min(rect.y for rect in self.rect_dict.values())
        for rect in self.rect_dict.values():
            rect.move_ip((x,y,))

    @property
    def reference(self):
        if self.alignment in ["center", "centerx"]:
            return "center"
        if self.alignment in ["left", "right"]:
            return "mid" + self.alignment
        raise ValueError('Not a valid alignment')

    def get_child_pos(self, pos):
        try:
            return getattr(self.rect_dict[pos], self.reference)
        except KeyError:
            return 0, 0
    
    @property
    def size(self):
        try:
            rects = self.rect_dict.values()
            rect = rects[0].unionall(rects[1:])
            return rect.size
        except (IndexError, AttributeError):
            return 0, 0


@from_parent(["font_sizes", "font_name", "antialias", "color",
              "opacity", "text", "margins", "alignment"])
class ChildrenMenuView(MenuView):
    """"""
    pass

class MenuSprite(ViewSprite):

    # Font
    font_sizes = 0, 0
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
    view_cls = ChildrenMenuView

    def init(self, **kwargs):
        ViewSprite.init(self)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_rect(self):
        kwargs = {self.reference: self.pos}
        return self.image.get_rect(**kwargs)


