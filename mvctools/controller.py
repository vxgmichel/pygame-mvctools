"""Module containing the base controller class."""

# Imports
import pygame as pg
from mvctools.common import xytuple

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
        return bool(self.model.register(name, *args, **kwargs))

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


# Direction controller
class MappingController(BaseController):
    """COntroller for the main game state."""

    #: Threshold for joysticks
    axis_threshold = 0.5

    #: Key to (action, player) mapping
    #: player can be None if the action is generic
    key_dct = {}

    #: Key to (direction, player) mapping
    dir_dct = {}

    #: Button to (action, as_player) mapping
    #: as_player is False if the action is generic,
    #:              True otherwise
    button_dct = {}

    #: Hat direction factor
    hat_factors =  +1, -1

    #: Axis direction factor
    axis_factors = +1, +1

    #: Direction action
    dir_action = "dir"

    #: Action that requires update on first frame
    special_actions = []

    def init(self):
        """Initialize the joysticks."""
        # Init joystick
        pg.joystick.quit()
        pg.joystick.init()
        # Get joysticks
        self.joysticks = []
        for i in range(pg.joystick.get_count()):
            self.joysticks.append(pg.joystick.Joystick(i))
            self.joysticks[-1].init()
        # Players
        self.nb_players = max(pid for _, pid in self.key_dct.values())
        self.nb_players = max(self.nb_players, len(self.joysticks))
        self.players = range(1, self.nb_players + 1)
        # Init direction
        for player in self.players:
            lst = [self.get_key_direction(player),
                   self.get_axis_direction(player),
                   self.get_hat_direction(player)]
            iterator = (direction for direction in lst if any(direction))
            direction = next(iterator, xytuple(0,0))
            self.register(self.dir_action, player, direction)
        # Special keys
        dct = pg.key.get_pressed()
        special_keys = (key for key, value in self.key_dct.items()
                        if value[0] in self.special_actions)
        for key in special_keys:
            if dct[key]:
                self.register_key(key, dct[key])

    def handle_event(self, event):
        """Process the different type of events."""
        if event.type == pg.KEYDOWN:
            return self.register_key(event.key, True)
        if event.type == pg.KEYUP:
            return self.register_key(event.key, False)
        if event.type == pg.JOYHATMOTION:
            return self.register_hat(event.joy+1)
        if event.type == pg.JOYBUTTONDOWN:
            return self.register_button(event.button, event.joy+1, True)
        if event.type == pg.JOYBUTTONUP:
            return self.register_button(event.button, event.joy+1, False)
        if event.type == pg.JOYAXISMOTION:
            return self.register_axis(event.joy+1)

    def axis_position(self, arg):
        """Convert axis value to position."""
        return cmp(arg, 0) if abs(arg) >= self.axis_threshold else 0

    def get_key_direction(self, player):
        """Get direction from current key state."""
        dct = pg.key.get_pressed()
        gen = (direc for key, (direc, play) in self.dir_dct.items()
               if play == player and dct[key])
        return sum(gen, xytuple(0,0))

    def get_axis_direction(self, player):
        """Get direction from current key state."""
        factors = xytuple(*self.axis_factors)
        try :
            raw_values = [self.joysticks[player-1].get_axis(i) for i in (0,1)]
        except IndexError:
            raw_values = 0,0
        return factors * map(self.axis_position, raw_values)

    def get_hat_direction(self, player):
        """Get direction from current key state."""
        factors = xytuple(*self.hat_factors)
        try:
            return factors * self.joysticks[player-1].get_hat(0)
        except IndexError:
            return factors * (0, 0)

    def get_key_action(self, key):
        """Return action and player corresponding to the given key."""
        if key in self.dir_dct:
            return self.dir_action, self.dir_dct[key][1]
        return self.key_dct.get(key, (None, None))

    def register_key(self, key, down):
        """Register a key strike."""
        action, player = self.get_key_action(key)
        # Ignore
        if action is None:
            return
        # Generic action
        if player is None:
            return self.model.register(action, down)
        # Player related action
        if action != self.dir_action:
            return self.model.register(action, player, down)
        # Direction action
        direction = self.get_key_direction(player)
        return self.register(action, player, direction)

    def register_hat(self, player):
        """Register a hat event."""
        direction = self.get_hat_direction(player)
        return self.register(self.dir_action, player, direction)

    def register_button(self, button, player, down):
        """Register a button event."""
        action, as_player = self.button_dct.get(button, (None,None))
        # Ignore
        if action is None:
            return
        # Generic action
        if not as_player:
            return self.model.register(action, down)
        # Player related action
        return self.model.register(action, player, down)

    def register_axis(self, player):
        """Register an axis event."""
        direction = self.get_axis_direction(player)
        return self.register(self.dir_action, player, direction)


