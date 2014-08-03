import pygame
from mvctools.common import xytuple, Color

class BaseSettings(object):
    def __init__(self, control):
        self.control = control
        self._fps = 40
        self._width = 1280
        self._height = 720
        self._fullscreen = False
        self._native_ratio = None

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def size(self):
        return xytuple(self._width, self._height)

    @size.setter
    def size(self, value):
        if isinstance(value, basestring):
            value = value.lower().split('x')
            value = map(int, value)
        if any(self.size-value):
            self._width, self._height = value
            self.apply()

    @property
    def fps(self):
        return self._fps

    @fps.setter
    def fps(self, value):
        if isinstance(value, basestring):
            value = int(value)
        if value != self.fps:
            self._fps = value
            self.apply()

    @property
    def fullscreen(self):
        return self._fullscreen

    @fullscreen.setter
    def fullscreen(self, value):
        if isinstance(value, basestring):
            if value.lower().startswith('full'):
                value = True
            elif value.lower().startswith('window'):
                value = False
        if not isinstance(value, bool):
            raise ValueError
        if value != self.fullscreen:
            self._fullscreen = value
            self.apply()

    # Fullscreen alias
    mode = fullscreen

    @property
    def native_ratio(self):
        return self._native_ratio

    @native_ratio.setter
    def native_ratio(self, value):
        if isinstance(value, tuple):
            w, h = value
            value = float(w)/h
        if value != self.native_ratio:
            self._native_ratio = value
            self.apply()

    def string_setting(self, name, default=None):
        if name in ["size"]:
            return "x".join(map(str, self.size))
        if name in ["fullscreen", "mode"]:
            return {True: "fullscreen", False: "windowed"}.get(self.mode)
        if name in ["fps"]:
            return str(self.fps)
        if name in ["width"]:
            return str(self.width)
        if name in ["height"]:
            return str(self.height)
        return default

    def apply(self):
        if pygame.display.get_surface():
            self.set_mode()
            self.control.reload()

    def set_mode(self):
        flag = pygame.FULLSCREEN if self.fullscreen else 0
        pygame.display.set_mode(self.size, flag)
        

    def scale_as_background(self, image=None, color=None):
        if not image and not color:
            return None
        color = Color(color)
        bgd = pygame.Surface(self.size)
        bgd.fill(color)
        if image is not None:
            scaled = pygame.transform.smoothscale(image, self.size)
            bgd.blit(scaled, scaled.get_rect())
        return bgd
