
import pygame, gc
from collections import deque
from mvctools.model import BaseModel
from mvctools.controller import BaseController
from mvctools.view import BaseView
from mvctools.common import scale_dirty


class NextStateException(Exception):
    pass

class TickContext(object):
    def __init__(self, state):
        self.state = state

    def __enter__(self):
        self.state.ticking = True

    def __exit__(self, error, value, traceback):
        self.state.ticking = False
        if error is NextStateException:
            return True


class BaseState(object):
    model_class = BaseModel
    controller_class = BaseController
    view_class = BaseView
    clock_class = pygame.time.Clock

    def __init__(self, control):
        self.control = control
        self.model = self.model_class(self)
        self.controller = self.controller_class(self, self.model)
        self.view = self.view_class(self, self.model)
        self.current_fps = None
        self.ticking = False

    def clean(self):
        self.view.delete()
        self.controller = None
        self.view = None
        gc.collect()

    def reload(self):
        self.controller = self.controller_class(self, self.model)
        self.view = self.view_class(self, self.model)
        self.current_fps = None
        self.ticking = False

    def tick(self):
        mvc = self.controller, self.model, self.view
        with TickContext(self):
            return self.controller._update() or \
                   self.model._update() or \
                   self.update_view()
        return True

    def update_view(self):
        # Get the screens
        actual_screen = self.get_surface()
        screen, dirty = self.view._update()
        # Scale
        if actual_screen != screen:
            dirty = scale_dirty(screen, actual_screen, dirty)
        # Update
        pygame.display.update(dirty)

    def get_surface(self):
        return pygame.display.get_surface()

    @property
    def delta(self):
        return 1.0 / self.current_fps

    def run(self):
        # Get settings
        string = None
        limit_fps = float(self.control.settings.fps)
        debug_speed = float(self.control.settings.debug_speed)
        if self.control.settings.display_fps:
            string = self.control.window_title + "   FPS = {:3}"
        # Init time
        queue = deque(maxlen=3)
        clock = self.clock_class()
        # Freeze current fps for the first two ticks
        self.current_fps = limit_fps
        if self.tick():
            return
        # Time control
        tick = limit_fps
        tick *= debug_speed
        millisec = clock.tick(tick)
        # Profile
        if self.control.settings.profile:
            import cProfile, pstats
            profiler = cProfile.Profile()
            profiler.enable()
            clock.tick()
        # Loop over the state ticks
        while not self.tick():
            # Time control
            millisec = clock.tick(tick)
            # Update current FPS
            if millisec:
                queue.append(1000.0/millisec)
                queue[-1] /= debug_speed
                # Median filter of size 3
                new_fps = sorted(queue)[len(queue)//2]
                self.current_fps = new_fps
            # Update window caption
            rate = clock.get_fps()
            if rate and string:
                    caption = string.format(int(rate))
                    pygame.display.set_caption(caption)
        # Profile
        if self.control.settings.profile:
            profiler.disable()
            ps = pstats.Stats(profiler).sort_stats('tottime')
            ps.print_stats()

