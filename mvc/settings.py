import pygame
from mvc.common import XY

class BaseSettings(object):
    def __init__(self):
        self.fps = 40
        self.width = 800
        self.height = 600

    @property
    def size(self):
        return XY(self.width, self.height)

    @size.setter
    def size(self, value):
        self.width, self.height = value
        
    def get_fps(self):
        return self.fps

    def scale_as_background(self, image=None, color=(0,0,0)):
        bgd = pygame.Surface(self.size)
        bgd.fill(color)
        if image is not None:
            scaled = pygame.transform.smoothscale(image, self.size)
            bgd.blit(scaled, scaled.get_rect())
        return bgd
