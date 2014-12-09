from mvctools import NextStateException, BaseModel, Timer
from mvctools import xytuple, cursoredlist, from_gamedata
from collections import defaultdict
from functools import partial


# Tile Models

class TileModel(BaseModel):
    
    def init(self, pos):
        self.pos = pos

    @property
    def pos(self):
        return xytuple(*self._pos)

    @pos.setter
    def pos(self, value):
        self._pos = xytuple(*value)
        
class FloorModel(TileModel):

    def init(self, pos):
        super(FloorModel, self).init(pos)
        self.activation_dct = defaultdict(bool)

    def set_activation(self, pid, value=True):
        self.activation_dct[pid] = value

    def reset(self):
        self.activation_dct.clear()

class PlayerModel(TileModel):

    period = 1.5
    moving_period = 0.1
    transfrom_period = 0.1
    dying_period = 0.1

    # Inititalization

    def init(self, pos, pid):
        super(PlayerModel, self).init(pos)
        # Create timers
        self.timer = Timer(self,
                           stop=self.period,
                           periodic=True)
        self.transform_timer = Timer(self,
                                     stop=self.transfrom_period,
                                     callback=self.transform_callback)
        self.moving_timer = Timer(self,
                                  stop=self.moving_period,
                                  callback=self.moving_callback)
        self.dying_timer = Timer(self,
                                 stop=self.dying_period,
                                 callback=self.dying_callback)
        self.timer.start()
        # Set attributes
        self.id = pid
        self.dir = xytuple(0,1)
        self.activedir = False
        self.is_dead = False

    # Generator

    def projection(self):
        # Yield current tile
        board = self.parent
        init_pos = self.round_pos if self.is_busy else self.pos
        if isinstance(board.tile_dct[init_pos], FloorModel):
            yield board.tile_dct[init_pos]
        # Break if direction not active
        if not self.activedir:
            return
        # Get stop positions
        if self.is_busy:
            stop_pos = [self.real_pos + self.dir]
        else:
            stop_pos = [p.real_pos for p in board.player_dct.values()]
        # Yield tiles over the projection
        current = board.tile_dct[init_pos + self.dir]
        while isinstance(current, (FloorModel, BlackHoleModel)) \
          and current.pos not in stop_pos:
            yield current
            if isinstance(current, BlackHoleModel):
                break
            current = board.tile_dct[current.pos+self.dir]

    # Properties

    @property
    def pos(self):
        if not self.is_busy:
            return xytuple(*self.real_pos)
        if self.is_dying:
            ratio = self.dying_timer.get(normalized=True)
            return self.round_pos + (ratio * 0.8,) * 2
        ratio = self.moving_timer.get(normalized=True)
        return self.round_pos + self.dir * (ratio, ratio)

    @pos.setter
    def pos(self, value):
        self.real_pos = xytuple(*value).map(int)

    @property
    def goal(self):
        return self.parent.goal_dct[self.id]

    # Status properties

    @property
    def on_black_hole(self):
        tile = self.parent.tile_dct[self.pos]
        return isinstance(tile, BlackHoleModel)

    @property
    def on_goal(self):
        return self.pos == self.goal.pos and not self.is_busy

    @property
    def is_moving(self):
        return not self.moving_timer.is_paused

    @property
    def is_transforming(self):
        return not self.transform_timer.is_paused

    @property
    def is_dying(self):
        return not self.dying_timer.is_paused

    @property
    def is_busy(self):
        return self.is_transforming or self.is_moving or self.is_dying

    # Timer handling

    def transform_callback(self, timer):
        if timer.is_set:
            self.moving_timer.reset().start()
        else:
            self.timer.reset().start()
            self.activedir = self.activedir and not self.on_goal

    def moving_callback(self, timer):
        # Handle position
        if self.round_pos != self.real_pos:
            self.round_pos += self.dir
        timer.reset()
        # What's next?
        if self.round_pos != self.real_pos:
            timer.start()
        elif self.on_black_hole:
            self.dying_timer.start()
            self.active_dir = False
        else:
            self.transform_timer.start(-1)

    def dying_callback(self, timer):
        self.parent.load_next_board(win=False)

    # Update
    
    def update(self):
        ratio = (-1, +1)[self.on_goal]
        self.goal.timer.start(ratio)

    # Register methods
        
    def register_validation(self):
        if self.is_busy:
            return
        # Get destination
        dest = list(self.projection())[-1]
        if dest.pos == self.pos:
            return
        # Set up move
        self.round_pos = self.pos
        self.transform_timer.start()
        # Set position
        self.real_pos = dest.pos
        
    def register_direction(self, dirx, diry):
        if self.is_busy:
            return
        self.activedir = True
        self.dir = xytuple(dirx,diry)

class GoalModel(TileModel):

    period = 3.0

    def init(self, pos, pid):
        super(GoalModel, self).init(pos)
        self.id = pid
        self.activated = False
        self.timer = Timer(self, stop=self.period, callback=self.callback)

    def callback(self, timer):
        self.activated = timer.is_set
        

class BlackHoleModel(TileModel):

    period = 2.0

    def init(self, pos):
        super(BlackHoleModel, self).init(pos)
        self.timer = Timer(self, stop=self.period, periodic=True)
        self.timer.start()

class BorderModel(TileModel):
    pass

class BlockModel(TileModel):
    pass
        

# Board Model

class BoardModel(BaseModel):

    # Initialize
    
    @from_gamedata("board_level")
    def level(self):
        return 0

    def init(self):
        # Build the board and tiles
        self.player_dct = {}
        self.goal_dct = {}
        self.resource_lst = list(self.control.resource.map)
        try: self.board = self.resource_lst[self.level]
        except IndexError: self.load_next_board()
        self.tile_dct = self.build_tiles(self.board)
        # Useful attributes
        self.max_coordinate = xytuple(*max(self.tile_dct))
        self.nb_line = self.max_coordinate.x + 1
        self.nb_column = self.max_coordinate.x + 1

    # Events
    
    def load_next_board(self, win):
        if win:
            self.level += 1
        try:
            self.resource_lst[self.level]
        except IndexError:
            self.level = 0
            next_state = self.state.next_state
        else:
            next_state = type(self.state)
        self.control.register_next_state(next_state)
        raise NextStateException

    def register_validation(self, pid):
        player = self.player_dct.get(pid)
        if player:
            player.register_validation()

    def register_direction(self, pid, dirx, diry):
        player = self.player_dct.get(pid)
        if player:
            player.register_direction(dirx, diry)

    def register_pause(self):
        self.control.push_current_state()
        self.control.register_next_state(self.state.pause_state)
        raise NextStateException

    # Update

    def update(self):
        if all(goal.activated for goal in self.goal_dct.values()):
            self.load_next_board(win=True)
        self.update_floors()

    def update_floors(self):
        # Rest floors
        for tile in self.tile_dct.values():
            if isinstance(tile, FloorModel):
                tile.reset()
        # Activate floors
        for player in self.player_dct.values():
            for tile in player.projection():
                if isinstance(tile, FloorModel):
                    tile.set_activation(player.id)

    # Build
    
    def build_tiles(self, resource):
        mat = self.parse(resource)
        mat = self.add_border(mat)
        return {(i,j): self.type_dct[element](self, (i,j))
                    for i, line in enumerate(mat)
                        for j, element in enumerate(line)}

    @staticmethod
    def parse(resource):
        resource = iter(resource)
        next(line for line in resource if line.startswith("data="))
        parseline = lambda line: [int(x) for x in line.strip().split(",") if x]
        return [parseline(line) for line in resource if "," in line]

    @staticmethod
    def add_border(mat):
        first = last = [[-1] * (2 + len(mat[0]))]
        middle = [[-1] + x + [-1] for x in mat]
        return first + middle + last

    def build_goal(self, pos, pid):
        self.goal_dct[pid] = GoalModel(self, pos, pid)
        return FloorModel(self, pos)

    def build_player(self, pos, pid):
        self.player_dct[pid] = PlayerModel(self, pos, pid)
        floor = FloorModel(self, pos)
        floor.set_activation(pid, True)
        return floor

    type_dct = {-1: BorderModel,
                 1: FloorModel,
                 2: partial(build_goal, pid=1),
                 3: partial(build_goal, pid=2),
                 4: partial(build_player, pid=1),
                 5: partial(build_player, pid=2),
                 6: BlockModel,
                 7: BlackHoleModel}   
                                           
                    
