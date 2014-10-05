"""Module containing the base controller class."""

# Imports
import pygame as pg

# Base controller class
class BaseController(object):
    """ Base controller class for the MVC pattern implementation.

    Shouldn't be instanciated manually but
    subclassed then registered in a State class.

    A subclass of BaseController may override the following method:
     - **init**: called at initialization
       (default: do nothing)
     - **is_quit_event**: define what a quit event is
       (default: pygame.QUIT and Alt+f4)
     - **handle_event**: process a given event
       (default: do nothing)

    An instance has the following attributes:
     - **self.state**: the state that uses the controller
     - **self.control**: the game that uses the controller
     - **self.model**: the model associated with the controller
    """
    
    def __init__(self, state, model):
        """Inititalize the controller.

        Args:
            state (BaseState): the state that uses the controller
            model (BaseModel): the model associated with the controller
        """
        self.state = state
        self.control = self.state.control
        self.model = model
        self.init()

    def init(self):
        """Empty method to override if needed.

        Called at initialization.
        """
        pass

    def _reload(self):
        """Reinitialize the controller.

        Called when the state is reloaded.
        """
        self.init()
    
    def _update(self):
        """Process the events.

        Called at each tick of the state.
        """
        for ev in pg.event.get():
            if self._handle_event(ev):
                return True

    def _handle_event(self, event):
        """Handle an event.

        Args:
            event (Event): a pygame event
        Return:
            bool: True to stop the current state, False otherwise.
        Raise:
            SystemExit: when the given event is a quit event
        """
        if self.is_quit_event(event):
            raise SystemExit
        return self.handle_event(event)

    def handle_event(self, event):
        """Empty method to override.

        Args:
            event (Event): a pygame event
        Return:
            bool: True to stop the current state, False (or None) otherwise.

        An overwritten version of this method should regiser actions
        to the model.

        Example: ::
        
            def handle_event(event):
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        return self.model.register_up() # OR
                        # return self.register("up")
            

        Note: It is probably a bad idea to return directly True since
        stopping the current state should be the model decision.
        """
        pass

    def register(self, name, *args, **kwargs):
        """Convenience function to register an action to the model.

        Args:
            name (str): name of the action to register
            args (list): arguments to pass to the model method
            kwargs (dict): keywords arguments to pass to the model method 
        Return:
            bool: True to indicate that the model wants to stop
            the current state, False otherwise.
        """
        method = getattr(self.model, 'register_' + name)
        return bool(method(*args, **kwargs))

    def is_quit_event(self, event):
        """Define what a quit event is. Include pygame.Quit and Alt+F4.

        Can be overriden to include more quit events.

        Args:
            event (Event): a pygame event
        Return:
            bool: True if event is a quit event
        """
        altf4_event = (event.type == pg.KEYDOWN and \
                       event.key == pg.K_F4 and \
                       event.mod == pg.KMOD_LALT)
        pgquit_event = (event.type == pg.QUIT)
        return altf4_event or pgquit_event


class MouseAction:
    """Enumeration of mouse actions."""
    #: When the left button is released on a sprite
    CLICK = "click"
    #: When the middle button is released on a sprite
    MIDDLECLICK = "middleclick"
    #: When the right button is released on a sprite
    RIGHTCLICK = "rightclick"
    #: When the wheel is rolled up on a sprite
    WHEELUP = "wheelup"
    #: When the wheel is rolled down on a sprite
    WHEELDOWN = "wheeldown"
    #: When a sprite is hovered
    HOVER = "hover"

    
class MouseController(BaseController):
    """ Base controller class processing mouse events.

    All the actions in MouseAction are handled here.
    """

    mouse_button_mapping = {1: MouseAction.CLICK,
                            2: MouseAction.MIDDLECLICK,
                            3: MouseAction.RIGHTCLICK,
                            4: MouseAction.WHEELUP,
                            5: MouseAction.WHEELDOWN}
    
    def handle_event(self, event):
        """Handle button up and motion mouse events."""
        if event.type == pg.MOUSEBUTTONUP:
            action = self.mouse_button_mapping[event.button]
            model = self.get_model_at(event.pos)
            if model: return model.register(action)
        if event.type == pg.MOUSEMOTION:
            model = self.get_model_at(event.pos)
            if model: return model.register(MouseAction.HOVER)

    def get_models_at(self, pos):
        """Get the list of models corresponding to a given position.

        Args:
            pos (tuple): the position on screen
        Returns:
            list: models from top to bottom
        """
        return self.state.view.get_models_at(pos)

    def get_model_at(self, pos):
        """Get the model corresponding to a given position.

        Args:
            pos (tuple): the position on screen
        Returns:
            BaseModel: topmost model or None if doesn't exist
        """
        try: return self.get_models_at(pos)[0]
        except IndexError: return None
