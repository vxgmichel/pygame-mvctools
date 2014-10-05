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

    def _reload(self):
        """Reload itself and its children.

        Called when the state is reloaded."""
        self.reload()
        [child._reload() for child in self.children.values()]

    def reload(self):
        """Empty method to override if needed.

        Called when the state is reloaded.
        """

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
        return self.update() or self._update_children()

    def update(self):
        """Empty method to override.

        Called at each tick of the state.

        Return:
            bool: True to stop the current state, False otherwise.
        """
        pass

    def get_model_dct(self):
        """Recursively get the dictionnary of all models with
        their associated key (including itself).

        Return:
            dict: the (key, model) dictionnary
        """
        iterators = [child.get_model_dct() for child in self.children.values()]
        value = (self.key, self)
        return chain([value], *iterators)

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

    def __iter__(self):
        """Iterator support.

        Return:
            list: the direct children.
        """
        return self.children.values()

    def __del__(self):
        """Unregister itself."""
        self.parent._unregister_child(self)


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

    def get_interval(self):
        """Return the (start, stop) interval as a tuple."""
        return self._start, self._stop

    def is_set(self):
        """Return True if the timer reached its stop value.
        Return False otherwise.
        """
        return self._current_value == self._stop

    def is_reset(self):
        """Return True if the timer reached its start value.
        Return False otherwise.
        """
        return self._current_value == self._start

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
        delta = 1.0/self.state.current_fps
        self._next_increment = delta*self._ratio


# Property from game data
def property_from_gamedata(name):
    """Build a property from an attribute name in gamedata.

    Here is the behavior of this property:
     - If a read access is made, the gamedata attribute is returned.
     - If that attribute doesn't exist, the decorated function is used
       as a factory, the attribute is set and the value returned.
     - If a write access is made, the dataattribute is simply set.
     - If a deletion is made, the attribute is cleared from the gamedata.

    The main purpose is simplify the communication between the model
    and the gamedata.

    Example: ::

        @property_from_gamedata("player_score"):
        def score(self):
            return 0
    """
    def wrapper(method):
        """Build a gamedata property from a default method."""
        # Setter
        def fset(self, value):
            """Setter for the gamedata property."""
            setattr(self.gamedata, name, value)
        # Getter
        def fget(self):
            """Getter for the gamedata property."""
            try:
                return getattr(self.gamedata, name)
            except AttributeError:
                value = method(self)
                fset(self, value)
                return value
        # Deletter
        def fdel(self):
            """Deletter for the gamedata property."""
            delattr(self.gamedata, name)
        doc = method.__doc__
        return property(fget, fset, fdel, doc)
    return wrapper




