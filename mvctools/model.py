"""Module containing the model base class."""

# Imports
from itertools import count, chain


# Base model class
class BaseModel(object):
    """Model base class.

    Args:
        parent (BaseModel or BaseControl): the parent of the model
        args (list): custom arguments
        kwargs (dict): custom keyword arguments

    Note the following:
     - To a given state corresponds a main model.
     - It is possible for a model to have children.
     - A children is automatically registered at initialization.
     - A children is automatically unregistered at deletion.
     - The state automatically update every model registered.

    A subclass of BaseModel may override the following method:
     - **init**: called at initialization
       (default: create a timer **self.lifetime**)
     - **reload**: called when the state is reloaded
       (default: do nothing)
     - **update**: called at each tick of the state
       (default: do nothing)

    An instance has the following attributes:
     - **self.state**: the state that uses the controller
     - **self.control**: the game that uses the controller
     - **self.gamedata**: the game data of the control
     - **self.key**: a unique identifier for the model
     - **self.parent**: the parent of the model
     - **self.children**: the children dictionary
     - **self.isroot**: True if it is the main model
    """

    time_speed = 1.0

    def __init__(self, parent, *args, **kargs):
        """Initialize the model with its parent and register itself.

        Args:
            parent (BaseModel or BaseControl): the parent of the model
            args (list): custom arguments
            kwargs (dict): custom keyword arguments
        """
        self.isroot = not isinstance(parent, BaseModel)
        # Attributes to higher instances
        self.state = parent if self.isroot else parent.state
        self.control = parent.control
        self.gamedata = self.control.gamedata
        # Semi private attribute
        self._keygen = count() if self.isroot else parent._keygen
        # Useful attributes
        self.key = next(self._keygen)
        # Children and parent handling
        self.parent = parent
        self.children = {}
        if not self.isroot:
            self.parent._register_child(self)
        # Call user initialisation
        self.init(*args, **kargs)

    def init(self, *args, **kwargs):
        """Method to override.

        Called at initialization with the same arguments as the **__init__**
        method, but without the parent. If a model has to be initialized with
        custom arguments, this is where they should be handled.

        The base implementation also start a timer call **self.lifetime**.
        It is a non periodic timer with no upper limit and no callback.
        """
        self.lifetime = Timer(self).start()

    def _register_child(self, child):
        """Register a new child.

        Args:
            child (BaseModel): the child to register
        """
        self.children[child.key] = child

    def _unregister_child(self, child):
        """Unregister a child if registered.

        Args:
            child (BaseModel): the child to unregister
        """
        self.children.pop(child.key, None)

    def _update_children(self):
        """Update all the children.

        Return:
            bool: True if any of their updates returned True
        """
        return any(child._update() for child in self.children.values())

    def _update(self):
        """Update the model and its children.

        Return:
            bool: True to stop the current state, False otherwise.
        """
        return self.update() or self._update_children() or self.post_update()

    def update(self):
        """Empty method to override.

        Called at each tick of the state before updating the children.

        Return:
            bool: True to stop the current state, False otherwise.
        """
        pass

    def post_update(self):
        """Empty method to override.

        Called at each tick of the state after updating the children

        Return:
            bool: True to stop the current state, False otherwise.
        """
        pass

    def gen_model_dct(self):
        """Recursively generate the dictionnary of all models with
        their associated key (including itself).

        Return:
            dict: the (key, model) dictionnary
        """
        yield self.key, self
        for child in self.children.values():
            for value in child.gen_model_dct():
                yield value

    def get_children(self):
        """Return the list of the current children model."""
        return self.children.values()

    def get_image(self):
        """Get the current image.

        Warning: this breaks the model independance.
        Use with care.
        """
        sprite = self.state.view.get_sprite_from(self)
        return sprite.get_image() if sprite else None

    def register(self, action, *args, **kwargs):
        """Register an action.

        Args:
            action (str): name of the action to register
            args (list): arguments to pass to the model method
            kwargs (dict): keywords arguments to pass to the model method
        Return:
            bool: True to stop the current state, False otherwise.

        Warning: no exception is raised if no handler is found.
        It will be silently ignored and False will be returned

        This choice has been made on purpose, considering the controller
        might register more types of actions than the model can handle.
        """
        method_name = "_".join(("register", action.lower()))
        # Ignore if no corresponding method
        if not hasattr(self, method_name):
            return False
        # Call the corresponding method
        return getattr(self, method_name)(*args, **kwargs)

    @property
    def delta(self):
        """Time difference with last update."""
        return self.time_speed * self.parent.delta

    def __iter__(self):
        """Iterator support.

        Return:
            list: the direct children.
        """
        return self.children.values()

    def delete(self):
        """Delete the model."""
        self.parent._unregister_child(self)
        for child in self.children.values():
            child.delete()
        self.children.clear()
        self.parent = None


# Timer model class
class Timer(BaseModel):
    """Timer model class.

    Args:
        parent (BaseModel): the parent of the timer
        start (int): start value for the timer (default is 0)
        stop (int or None): stop value for the timer
                            (default is None for no upper limit)
        periodic (bool): True for the timer to start over after it
                         reaches the stop value (default is False)
        callback (func): function to be called when the timer
                         reaches the stop value (default is None)

    It uses the current system FPS value to update accordingly.
    This way, the timer ignore lags or frame rate variations.
    """

    def init(self, start=0, stop=None, periodic=False, callback=None):
        """Initalize the timer.

        Args:
            parent (BaseModel): the parent of the timer
            start (int): start value for the timer (default is 0)
            stop (int or None): stop value for the timer
                                (default is None for no upper limit)
            periodic (bool): True for the timer to start over after it
                             reaches the stop value (default is False)
            callback (func): function to be called when the timer
                             reaches the stop value (default is None)
        """
        self._start = float("-inf") if start is None else start
        self._stop = float("inf") if stop is None else stop
        if self._start > self._stop:
            raise AttributeError("Invalid Range")
        self._periodic = periodic
        self._callback = callback
        self._ratio = 0.0
        self._current_value = float(start)
        self._next_increment = 0.0
        
    @property
    def interval(self):
        """Return the (start, stop) interval as a tuple."""
        return self._start, self._stop

    @property
    def is_set(self):
        """Return True if the timer reached its stop value.
        Return False otherwise.
        """
        return self._current_value == self._stop

    @property
    def is_reset(self):
        """Return True if the timer reached its start value.
        Return False otherwise.
        """
        return self._current_value == self._start

    @property
    def is_paused(self):
        """Return True if the timer is paused, False otherwise."""
        return self._ratio == 0

    def start(self, ratio=1.0):
        """Start the timer.

        Args:
            ratio (float): speed in unit per seconds (default is 1.0)
        Return:
            itself for affectation
        """
        self._ratio = float(ratio)
        return self

    def pause(self):
        """Stop the timer.

        Return:
            itself for affectation
        """
        self._ratio = 0.0
        return self

    def get(self, normalized=False):
        """Get the current value of the timer.

        Args:
            normalized (bool): normalize the value with start
                               and stop value (default is False)
        Return:
            float: current value (between 0 and 1 if normalized.
        """
        if not normalized:
            return self._current_value
        result = self._current_value - self._start
        result /= self._stop - self._start
        return result


    def reset(self):
        """Reset the timer.

        Return:
            itself for affectation
        """
        self._current_value = self._start
        return self.pause()

    def set(self, value=None):
        """Set the timer.

        Args:
            value (float or None): value to set the timer,
                                   set to stop if value is None
        Return:
            model: itself for affectation
        Raises:
            ValueError: if value not between start and stop
        """
        value = self._stop if value is None else value
        if self._start <= value <= self._stop:
            self._current_value = float(value)
            return self.pause()
        raise ValueError("Invalid value")

    def _modulo_adjust(self):
        """Adjust the current value to be between start and stop."""
        self._current_value -= self._start
        self._current_value %= self._stop - self._start
        self._current_value += self._start

    def update(self):
        """Update the timer.

        Use **self.state.current_fps** to update the current value
        accordingly. Also call the callback if needed."""
        # Increment
        self._current_value += self._next_increment
        # Overflow
        if self._next_increment and \
           not self._start < self._current_value < self._stop:
            if self._periodic:
                self._modulo_adjust()
            elif self._current_value <= self._start:
                self.reset()
            else:
                self.set()
            if callable(self._callback):
                self._callback(self)
        # Prepare next increment
        self._next_increment = self.delta*self._ratio
