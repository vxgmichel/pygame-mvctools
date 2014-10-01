"""Module containing the base controller class."""

# Imports
import pygame as pg

# Base controller class
class BaseController:
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

        Called at each tick the state.
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
            bool: True to stop the current state, False otherwise.

        An overwritten version of this method should regiser actions
        to the model.

        Example: ::
        
            def handle_event(event):
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.model.register_up()
            

        Note: It is probably a bad idea to return True since stopping
        the current state should be the model decision.
        """
        pass

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
