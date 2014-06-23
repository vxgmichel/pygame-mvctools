import os, sys
import pygame

# Loaders

def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return relative

def walk(path):
    return os.walk(resource_path(path))

def load_image(path):
    return pygame.image.load(resource_path(path)).convert_alpha()

def load_font(path):
    if not pygame.font.get_init():
        pygame.font.init()
    return lambda size: pygame.font.Font(resource_path(path), size)

def load_music(path):
    return pygame.mixer.music.load(resource_path(path))

def load_file(path):
    return open(resource_path(path))

# Handler

class ResourceHandler:

    _loader_dict = {"ttf":load_font,
                    "png":load_image,
                    "jpg":load_image,
                    "bmp":load_image,}
    
    def __init__(self, directory):
        self._dir, self._subdirs, self._files = next(walk(directory))
        self._subdir_dict = {subdir: ResourceHandler(self._join(subdir))
                             for subdir in self._subdirs}
        self._resource_dict = {}

    def _join(self, path):
        return os.path.join(self._dir, path)

    def __getattr__(self, attr):
        # Look for a sub directory
        if attr in self._subdir_dict:
            return self._subdir_dict[attr]
        # Look for an already loaded resource
        if attr in self._resource_dict:
            return self._resource_dict[attr]
        # Look for valid filenames
        valid_files = [f for f in self._files if f.startswith(attr+".")]
        # Raise AttributeError
        if not valid_files:
            msg = "Ressource '{}.*' cannot be found".format(self._join(attr))
            raise AttributeError(msg)
        # Look for matching extension
        for valid_file in valid_files:
            ext = valid_file.split(".")[-1]
            if ext.lower() in self._loader_dict:
                resource = self._loader_dict[ext](self._join(valid_file))
                self._resource_dict[attr] = resource
                return resource
        msg = "No loader can be found for file(s) '{}.*'".format(self._join(attr))
        raise AttributeError(msg)
        
