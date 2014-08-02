from mvctools import NextStateException, BaseModel, Timer
from mvctools import xytuple, cursoredlist
from collections import defaultdict
from functools import partial


# Tile Models

class TileModel(BaseModel):
    
    def init(self, pos):
        self._pos = pos

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

    def set_activation(self, pid, value):
        self.activation_dct[pid] = value

class PlayerModel(TileModel):

    period = 1.5

    def init(self, pos, pid):
        super(PlayerModel, self).init(pos)
        self.timer = Timer(self, stop=self.period, periodic=True)
        self.timer.start()
        self.id = pid
        self.dir = xytuple(0,1)
        self.activedir = False

class GoalModel(TileModel):

    period = 3.0

    def init(self, pos, pid):
        super(GoalModel, self).init(pos)
        self.id = pid
        self.activated = False
        self.timer = Timer(self, stop=self.period, callback=self.callback)
        self.timer.start()

    def callback(self, timer):
        self.activated = timer.is_set()
        

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

    def init(self):
        # Build the board cursor
        if not hasattr(self.gamedata, "board_clst"):
            resource_lst = list(self.control.resource.map)
            self.gamedata.board_clst = cursoredlist(resource_lst)
        # Build the board and tiles
        self.player_dct = {}
        self.goal_dct = {}
        self.board = self.gamedata.board_clst.get()
        self.tile_dct = self.build_tiles(self.board)
        # Useful attributes
        self.max_coordinate = xytuple(*max(self.tile_dct))
        self.nb_line = self.max_coordinate.x + 1
        self.nb_column = self.max_coordinate.x + 1
    
    def load_next_board(self):
        self.gamedata.board_clst.inc(1)
        isover = not self.gamedata.board_clst.cursor
        next_state = self.state.next_state if isover else type(self.state)
        self.control.register_next_state(next_state)
        raise NextStateException

    def register_validation(self):
        self.load_next_board()

    def register_pause(self):
        self.control.push_current_state()
        self.control.register_next_state(self.state.pause_state)
        raise NextStateException

    def update(self):
        if all(goal.activated for goal in self.goal_dct.values()):
            self.load_next_board()

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
