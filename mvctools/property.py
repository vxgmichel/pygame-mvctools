"""Provide useful property classes."""

# Property from game data
def from_gamedata(arg):
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

        @property_from_gamedata("player_score")
        def score(self):
            return 0
    """
    # Test the argument
    if callable(arg):
        method, name = arg, None
    else:
        method, name = None, arg
    # Decorator
    def wrapper(method, name=name):
        """Build a gamedata property from a default method."""
        # Test name
        if name is None:
            name = method.__name__
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
    # Return the decorator or the method
    if method:
        return wrapper(method)
    return wrapper


# Default property
class default_property(property):
    """Property defined by default factory method.

    The getter, setter and deleter use an attribute named
    after the name of the factory preceded with '_'.

    Args:
        factory (method): default factory
    """

    def __init__(self, factory):
        """Initialize with a factory.

        Args:
            factory (method): default factory
        """
        property_name = factory.__name__
        attr_name = "_" + property_name
        # Setter
        def fset(self, value):
            setattr(self, attr_name, value)
        # Getter
        def fget(self):
            try:
                return getattr(self, attr_name)
            except AttributeError:
                value = factory(self)
                fset(self, value)
                return getattr(self, property_name)
        # Deleter
        def fdel(self):
            delattr(self, attr_name)
        # Create property
        property.__init__(self, fget, fset, fdel)
        self.__doc__ = factory.__doc__


# Setting property
class setting(property):
    """Property that provides aditional features for settings.

    It uses three functions:
     - **cast** function to apply before the new value is set
     - **from_string** function to apply if the new value is a string
     - **to_string** function to get the string representation of the value

    Args:
        fget (function): getter for the property
        fset (function): setter for the property
        fdel (function): deleter for the property
        doc  (string)  : documentation for the property
        cast (function): cast the new value
        from_string (function): convert a string
        to_string   (function): convert the value to a string
    """

    def __init__(self, fget=None, fset=None, fdel= None, doc=None,
                 cast=None, from_string=None, to_string=str):
        """Initialize the property.

        Args:
            fget (function): getter for the property
            fset (function): setter for the property
            fdel (function): deleter for the property
            doc  (string)  : documentation for the property
            cast (function): cast the new value
            from_string (function): convert a string
            to_string   (function): convert the value to a string
        """
        property.__init__(self, fget, fset, fdel, doc)
        self.conversions = (cast, from_string, to_string)

    #: Access to cast function
    cast = property(lambda self: self.conversions[0])

    # Access to from_string function
    from_string = property(lambda self: self.conversions[1])

    def to_string(self, owner):
        """Return the current value as a string for the given instance."""
        return self.conversions[2](self.__get__(owner))

    # Decorator methods

    def getter(self, fget):
        """Getter decorator."""
        res = property.getter(self, fget)
        res.conversions = self.conversions
        return res

    def setter(self, fset):
        """Setter decorator."""
        res = property.setter(self, fset)
        res.conversions = self.conversions
        return res

    def deleter(self, fdel):
        """Deleter decorator."""
        res = property.deleter(self, fdel)
        res.conversions = self.conversions
        return res

    def __call__(self, fget):
        """Decorator support."""
        return self.getter(fget)

    # Descriptor methods

    def __set__(self, owner, value):
        """Convert the value before calling the regular setter."""
        # Cast value
        if self.from_string and isinstance(value, basestring):
                value = self.from_string(value)
        if self.cast:
                value = self.cast(value)
        # Set value
        property.__set__(self, owner, value)


# Default setting property
class default_setting(setting, default_property):
    """Property to create a setting from a factory method

    It uses four functions:
     - **factory** function to get a new value if it doesn't exist
     - **cast** function to apply before the new value is set
     - **from_string** function to apply if the new value is a string
     - **to_string** function to get the string representation of the value

    Args:
        factory (method): default factory
        cast (function): cast the new value
        from_string (function): convert a string
        to_string   (function): convert the value to a string
    """

    def __init__(self, factory=None, cast=None, from_string=None, to_string=str):
        """Initializes the property.

        Args:
            factory (method): default factory
            cast (function): cast the new value
            from_string (function): convert a string
            to_string   (function): convert the value to a string
        """
        setting.__init__(self, cast=cast, from_string=from_string,
                         to_string=to_string)
        if factory is not None:
            default_property.__init__(self, factory)
