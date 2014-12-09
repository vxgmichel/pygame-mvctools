import os, sys
import pygame 
from itertools import chain, ifilter
from collections import defaultdict
import threading

# Loaders

def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)
    return relative

def walk(path):
    return os.walk(resource_path(path))


# Handler

class ResourceHandler:

    scale = pygame.transform.scale
    
    def __init__(self, directory):
        # Check directory
        directory = os.path.normpath(directory)
        if not os.path.isdir(directory):
            raise IOError("'{0}' directory not found".format(directory))
        # Walk directory
        self._dir, self._subdirs, self._files = next(walk(directory))
        self._files = [os.path.splitext(f)
                           for f in self._files
                               if not f.startswith(".")]
        self._subdir_dict = {subdir: ResourceHandler(self._join(subdir))
                             for subdir in self._subdirs}
        self._resource_dict = defaultdict(dict)
        # Sort files and dirs
        self._subdirs.sort()
        self._files.sort()

    # User methods

    def getdirnames(self):
        return sorted(self._subdir_dict)

    def getfilenames(self, filtered=True):
        return sorted(r+e for r,e in self._files)

    def load(self, recursive=True, threaded=False, callback=None):
        iterator = self.reciterator() if recursive else iter(self)
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

    def getfile(self, name, formatting=None, default=None):
        root, ext = os.path.splitext(name)
        # Look for an already loaded resource
        if formatting in self._resource_dict[root]:
            return self._resource_dict[root][formatting]
        # Look for valid filenames
        valid_files = [(r, e) for r, e in self._files
                       if r == root and e.startswith(ext)]
        # Raise AttributeError
        if not valid_files:
            return default
        # Look for matching extension
        for root, ext in valid_files:
            loader = self._get_loader(self._format_ext(ext))
            if loader:
                if formatting is None:
                    resource = loader(root+ext)
                    default = loader.func_defaults[0]
                    self._resource_dict[root][default] = resource
                else:
                    resource = loader(root+ext, formatting)
                self._resource_dict[root][formatting] = resource
                return resource
        # Return default
        return default

    def getdir(self, name, default=None):
        if name in self._subdir_dict:
            return self._subdir_dict[name]
        return default

    def unloadfile(self, name, formatting=None):
        # Look for an already loaded resource
        if attr in self._resource_dict:
            if formatting is None:
                del self._resource_dict[name]
            else:
                del self._resource_dict[name][formatting]
        # Look for valid filenames
        valid_files = (r+e for r, e in self._files if name==r)
        return next(valid_files, None)

    def unloaddir(self, name):
        if attr in self._subdir_dict:
            self._subdir_dict[attr].unload()
            return self._subdir_dict[attr]
    
    def iterator(self, formatting=None):
        """ Iter lazily over the sorted loadable files """
        files = (self.getfile(root, formatting) for root, ext in self._files)
        return ifilter(lambda x: x is not None, files)

    def reciterator(self, formatting=None):
        """ Iter recursively over the files of the directories """
        subiterators = (sub.reciterator(formatting)
                        for sub in self._subdir_dict.itervalues())
        return chain(self.iterator(formatting), *subiterators)

    # Private methods

    def _join(self, name, ext=""):
        return os.path.join(self._dir, name+ext)

    def _resource_path(self, name, ext=""):
        path = self._join(name, ext)
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, path)
        return path

    def _format_ext(self, ext):
        """ Format the extension """
        if ext.startswith("."):
            ext = ext[1:]
        return ext.lower()

    def _get_loader(self, ext, default=None):
        loader_dict = {"ttf":self.load_font,
                       "png":self.load_image,
                       "jpg":self.load_image,
                       "bmp":self.load_image,
                       "txt":self.load_file,}
        return loader_dict.get(ext, default)
        
    # Special methods

    def __getattr__(self, attr):
        # Look for a resource
        result = self.get(attr)
        if result is not None:
            return result
        # Raise AttributeError
        msg = "Ressource '{}*' cannot be found or loaded"
        msg = msg.format(self._join(attr))
        raise AttributeError(msg)

    def __delattr__(self, attr):
        # Look for a sub directory
        if self.unloaddir(attr):
            return
        # Look for an already loaded resource
        if self.unloadfile(attr):
            return
        # Raise AttributeError
        msg = "Ressource '{}*' cannot be found".format(self._join(attr))
        raise AttributeError(msg)

    def __len__(self):
        return len(self._files)

    def __getitem__(self, index):
        formatting = None
        if isinstance(index, tuple):
            index, formatting = index
        root, ext = self._files[index]
        return self.getfile(root+ext, formatting)

    def __detitem__(self, index):
        formatting = None
        if isinstance(index, tuple):
            index, formatting = index
        root, ext = self._files[index]
        return self.self.unloadfile(root+ext)

    def __iter__(self):
        return self.iterator()

    def __str__(self):
        return "RessourceHandler : {}".format(self._dir)

    __repr__ = __str__

    # Loaders

    def load_image(self, name, size=None):
        # Native image requested
        if size is None:
            image = pygame.image.load(self._resource_path(name))
            return image.convert_alpha()
        # Get native image
        raw_image = self.getfile(name)
        # No transformation case
        if size == raw_image.get_size():
            return raw_image
        # Scale image
        return self.scale(raw_image, size)

    def load_font(self, name, size=72):
        if not pygame.font.get_init():
            pygame.font.init()
        return pygame.font.Font(self._resource_path(name), size)

    def load_music(self, name, formatting=None):
        return pygame.mixer.music.load(self._resource_path(name))

    def load_file(self, name, spliter='\n'):
        string = open(self._resource_path(name)).read()
        if spliter is None:
            return string
        return string.split(spliter)

    
        
