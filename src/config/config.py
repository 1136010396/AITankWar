from enum import Enum

# 设置游戏窗口
SCREEN_WIDTH = 630
SCREEN_HEIGHT  = 630

# 0: 上, 1: 右, 2: 下, 3: 左
UP=0
RIGHT=1
DOWN=2
LEFT=3

# 地图块定义
PLAYER=-2
BASE=-1
SPACE=0
BRICK=1
IRON=2
RIVER=3
GRASS=4


def vector_to_direction(dx: int, dy: int) -> int:
    if dx==1 and dy==0:
        return RIGHT
    elif dx==-1 and dy==0:
        return LEFT
    elif dx==0 and dy==1:
        return DOWN
    else:
        return UP

def direction_to_vector(dir: int) -> (int,int):
    if dir==RIGHT:
        return 1,0
    elif dir==LEFT:
        return -1,0
    elif dir==DOWN:
        return 0,1
    else:
        return 0,-1



# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# size
MAP_OFFSET=3
TANK_SIZE=(48,48)
BASE_SIZE=(48,48)
LITTLE_BLOCK=(24,24)

list=["ORIGINAL_MAP","RIVER_MAP"]
LEVEL_DIR={1: "ORIGINAL_MAP", 2: "RIVER_MAP"}


class TankRole(Enum):
    ATTACKER = "attacker"    # 主攻手，负责直接进攻基地
    SUPPORTER = "supporter"  # 支援手，负责清理路障和牵制玩家
    DEFENDER = "defender"    # 防守手，保护进攻路线和阻击玩家

class AttackRoute(Enum):
    LEFT = "left"    # 左侧路线
    RIGHT = "right"  # 右侧路线
    MIDDLE = "middle"  # 中路

