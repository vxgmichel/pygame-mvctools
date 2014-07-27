import pygame
from mvctools.common import xytuple

class BaseSettings(object):
    def __init__(self, control):
        self.control = control
        self._fps = 40
        self._width = 800
        self._height = 600
        self._fullscreen = False

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

    def apply(self):
        if pygame.display.get_surface():
            self.set_mode()
            self.control.reload()

    def set_mode(self):
        flag = pygame.FULLSCREEN if self.fullscreen else 0
        pygame.display.set_mode(self.size, flag)
        

    def scale_as_background(self, image=None, color=(0,0,0)):
        bgd = pygame.Surface(self.size)
        bgd.fill(color)
        if image is not None:
            scaled = pygame.transform.smoothscale(image, self.size)
            bgd.blit(scaled, scaled.get_rect())
        return bgd
