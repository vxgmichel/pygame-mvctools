import pygame

class BaseSettings:
    def __init__(self):
        self.fps = 40
        self.width = 800
        self.height = 600

    @property
    def size(self):
        return self.width, self.height

    @size.setter
    def size(self, size):
        self.width, self.height = size
        
    def get_fps(self):
        return self.fps

    def scale_as_background(self, image, color=None):
        scaled = pygame.transform.smoothscale(image, self.size)
        if not color:
            return scaled
        bgd = pygame.Surface(self.size)
        bgd.fill(color)
        bgd.blit(scaled, scaled.get_rect())
        return bgd
