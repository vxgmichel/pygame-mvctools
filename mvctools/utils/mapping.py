"""Proposition of mapping for controllers."""

# Imports
import pygame as pg
from mvctools.controller import MappingController
from mvctools.common import Dir


# Player action enumeration
class PlayerAction:
    """Enumeration of player actions."""
    #: Validation action (A button typically)
    ACTIVATE = "activate"
    #: Cancellation action (B button typically)
    BACK = "back"
    #: Start action (start button typically)
    START = "start"
    #: Select action (select button typically)
    SELECT = "select"
    #: Escape (escape key typically)
    ESCAPE = "escape"
    #: Direction action (arrows or stick typically)
    DIR = MappingController.dir_action


# One player controller
class PlayerController(MappingController):
    """Proposition of player key mapping."""

    # Key to action mapping
    key_dct = {pg.K_x:         (PlayerAction.ACTIVATE, 1),
               pg.K_SPACE:     (PlayerAction.ACTIVATE, 1),
               pg.K_s:         (PlayerAction.BACK, 1),
               pg.K_n:         (PlayerAction.BACK, 1),
               pg.K_p:         (PlayerAction.ACTIVATE, 1),
               pg.K_KP_ENTER:  (PlayerAction.ACTIVATE, 1),
               pg.K_o:         (PlayerAction.BACK, 1),
               pg.K_KP_PERIOD: (PlayerAction.BACK, 1),
               pg.K_u:         (PlayerAction.START,  None),
               pg.K_j:         (PlayerAction.SELECT, None),
               pg.K_ESCAPE:    (PlayerAction.ESCAPE, None),}

    # Key to direction mapping
    dir_dct = {pg.K_r:     (Dir.UP,    1),
               pg.K_d:     (Dir.LEFT,  1),
               pg.K_f:     (Dir.DOWN,  1),
               pg.K_g:     (Dir.RIGHT, 1),
               pg.K_UP:    (Dir.UP,    1),
               pg.K_LEFT:  (Dir.LEFT,  1),
               pg.K_DOWN:  (Dir.DOWN,  1),
               pg.K_RIGHT: (Dir.RIGHT, 1),}

    # Button to action mapping
    button_dct = {0: (PlayerAction.ACTIVATE, True),
                  1: (PlayerAction.BACK,     True),
                  7: (PlayerAction.START,    False),
                  6: (PlayerAction.SELECT,   False),}


# Two players controller
class TwoPlayersController(PlayerController):
    """Proposition of two player key mapping."""

    # Key to action mapping
    key_dct = {pg.K_x:         (PlayerAction.ACTIVATE, 1),
               pg.K_SPACE:     (PlayerAction.ACTIVATE, 1),
               pg.K_s:         (PlayerAction.BACK, 1),
               pg.K_n:         (PlayerAction.BACK, 1),
               pg.K_p:         (PlayerAction.ACTIVATE, 2),
               pg.K_KP_ENTER:  (PlayerAction.ACTIVATE, 2),
               pg.K_o:         (PlayerAction.BACK, 2),
               pg.K_KP_PERIOD: (PlayerAction.BACK, 2),
               pg.K_u:         (PlayerAction.START,  None),
               pg.K_j:         (PlayerAction.SELECT, None),
               pg.K_ESCAPE:    (PlayerAction.ESCAPE, None),}

    # Key to direction mapping
    dir_dct = {pg.K_r:     (Dir.UP,    1),
               pg.K_d:     (Dir.LEFT,  1),
               pg.K_f:     (Dir.DOWN,  1),
               pg.K_g:     (Dir.RIGHT, 1),
               pg.K_UP:    (Dir.UP,    2),
               pg.K_LEFT:  (Dir.LEFT,  2),
               pg.K_DOWN:  (Dir.DOWN,  2),
               pg.K_RIGHT: (Dir.RIGHT, 2),}
