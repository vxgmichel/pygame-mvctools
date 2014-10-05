"""mvctools is a high-level set of Python modules designed for writing games
using the model-controller-view design pattern. It is written on top of
Pygame. This allows you to easily design a game as a succession of states.
Each of these states owns its own model, view and controller for which base
classes are provided. Other high level features are available, like the
resource handler and automatically updated sprite.
"""

from mvctools.common import xytuple, cursoredlist, cachedict
from mvctools.control import BaseControl
from mvctools.state import BaseState, NextStateException
from mvctools.controller import BaseController, MouseController
from mvctools.model import BaseModel, property_from_gamedata, Timer
from mvctools.view import BaseView
from mvctools.settings import BaseSettings
from mvctools.gamedata import BaseGamedata
from mvctools.sprite import AutoSprite, Animation


