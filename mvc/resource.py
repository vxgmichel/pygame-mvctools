import os, sys
import pygame
from itertools import chain, ifilter
import threading

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

    _loader_dict = {".ttf":load_font,
                    ".png":load_image,
                    ".jpg":load_image,
                    ".bmp":load_image,}
    
    def __init__(self, directory):
        self._dir, self._subdirs, self._files = next(walk(directory))
        self._files = [os.path.splitext(f) for f in self._files]
        self._subdir_dict = {subdir: ResourceHandler(self._join(subdir))
                             for subdir in self._subdirs}
        self._resource_dict = {}
        self._subdirs.sort()
        self._files.sort()

    def load(self, recursive=True, threaded=False, callback=None):
        iterator = self.recursive_iterator() if recursive else iter(self)
        # Not threaded case
        if not threaded:
            list(iterator)
            return
        # Threaded
        if not callable(callback):
            callback = lambda:None
        func = lambda : (list(iterator), callback())
        threading.Thread(target=func).start()
    
        
    def unload(self, recursive=True, threaded=False, callback=None):
        unloaders = [self._resource_dict.clear]
        if recursive:
            unloaders += [sub.unload for sub in self._subdir_dict.values()]
        iterator = (unloader() for unloader in unloaders)
        # Not threaded case
        if not threaded:
            list(iterator)
            return
        # Threaded
        if not callable(callback):
            callback = lambda:None
        func = lambda : (list(iterator), callback())
        threading.Thread(target=func).start()
        

    def get(self, path, default=None):
        # Parsing path
        if isinstance(path, basestring):
            path = os.path.normpath(path).split(os.path.sep)
        # Test length
        if len(path)<2:
            result = self.getdir(path[0], default)
            if result is default:
                result = self.getfile(path[0], default)
            return result
        # Directory case
        try:
            return self.getdir(path[0]).get(path[1:], default)
        except AttributeError:
            return default

    def getfile(self, name, default=None):
        root, ext = os.path.splitext(name)
        # Look for an already loaded resource
        if root in self._resource_dict:
            return self._resource_dict[root]
        # Look for valid filenames
        valid_files = [(r, e) for r, e in self._files
                       if r == root and e.startswith(ext)]
        # Raise AttributeError
        if not valid_files:
            return default
        # Look for matching extension
        try:
            resource = next(self._loader_dict[ext.lower()](self._join(root, ext))
                            for root, ext in valid_files
                            if ext.lower() in self._loader_dict)
            self._resource_dict[root] = resource
            return resource
        except StopIteration:
            return default

    def getdir(self, name, default=None):
        if name in self._subdir_dict:
            return self._subdir_dict[name]
        return default

    def recursive_iterator(self):
        """ Iter recursively over the files of the directories """
        subiterators = (sub.recursive_iterator()
                        for sub in self._subdir_dict.itervalues())
        return chain(iter(self), *subiterators)

    def _join(self, path, ext=""):
        return os.path.join(self._dir, path+ext)

    def __getattr__(self, attr):
        result = self.get(attr)
        if result is not None:
            return result
        msg = "Ressource '{}.*' cannot be found or loaded".format(self._join(attr))
        raise AttributeError(msg)

    def __delattr__(self, attr):
        # Look for a sub directory
        if attr in self._subdir_dict:
            self._subdir_dict[attr].unload()
            return
        # Look for an already loaded resource
        if attr in self._resource_dict:
            del(self._resource_dict[attr])
            return
        # Look for valid filenames
        valid_files = [(r, e) for r, e in self._files if attr==r]
        if valid_files:
            return
        # Raise AttributeError
        msg = "Ressource '{}.*' cannot be found".format(self._join(attr))
        raise AttributeError(msg)

    def __iter__(self):
        """ Iter lazily over the sorted loadable files """
        files = (self.get(root) for root, ext in self._files)
        return ifilter(lambda x: x is not None, files)

    def __del__(self):
        self.unload()

    
        
