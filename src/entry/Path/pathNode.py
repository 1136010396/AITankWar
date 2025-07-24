import heapq
import pygame
from src.config import config as C
from src.control.map_manager import TerrainType

class PathNode:
    """A* 寻路算法的节点类"""

    def __init__(self, x, y, parent=None):
        self.x = x  # 节点x坐标
        self.y = y  # 节点y坐标
        self.parent = parent  # 父节点
        self.g = 0  # 从起点到当前节点的实际代价
        self.h = 0  # 从当前节点到目标的估计代价
        self.f = 0  # f = g + h，节点的总代价

    def calculate_f(self):
        """计算节点的f值"""
        self.f = self.g + self.h

    def __lt__(self, other):
        """堆排序比较函数"""
        if self.f == other.f:
            return self.h < other.h
        return self.f < other.f

    def __eq__(self, other):
        """相等比较"""
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        """哈希函数，用于集合操作"""
        return hash((self.x, self.y))


class PathFinder:
    """A* 寻路算法实现类"""

    def __init__(self,game, width, height):
        self.game = game
        self.width = width  # 地图宽度
        self.height = height  # 地图高度
        self.directions = [  # 可移动的方向
            (0, -1),  # 上
            (1, 0),  # 右
            (0, 1),  # 下
            (-1, 0)  # 左
        ]

        # 地形代价
        self.terrain_costs = {
            TerrainType.BRICK: 5,  # 可以打破，但需要时间
            TerrainType.IRON: 999,  # 基本不可通过
            TerrainType.RIVER: 999,  # 不可通过
            TerrainType.GRASS: 1,  # 可以通过，且提供掩护
            'empty': 1  # 空地
        }



    @staticmethod
    def manhattan_distance(x1, y1, x2, y2):
        """计算曼哈顿距离"""
        return abs(x2 - x1) + abs(y2 - y1)

    def get_pixel_position(self, grid_x, grid_y):
        """将网格坐标转换为像素坐标"""
        return grid_x * 24 + 3, grid_y * 24 + 3

    # 寻路划分为网格
    def get_grid_position(self, pixel_x, pixel_y):
        """将像素坐标转换为网格坐标"""
        return (pixel_x - 3) // 24, (pixel_y - 3) // 24

    def get_terrain_at(self, grid_x, grid_y):
        """获取指定网格位置的地形类型"""
        pixel_x, pixel_y = self.get_pixel_position(grid_x, grid_y)
        rect = pygame.Rect(pixel_x, pixel_y, 24, 24)

        # 检查各种地形
        for terrain_type, group in self.game.map_manager.terrain_groups.items():
            for terrain in group:
                if terrain.rect.colliderect(rect):
                    return terrain_type
        return None

    def get_terrain_cost(self, x, y, target_pos, enemy):
        """获取地形代价的回调函数"""
        terrain_type = self.get_terrain_at(x, y)
        base_cost = self.terrain_costs.get(terrain_type, self.terrain_costs['empty'])

        # 特殊情况处理
        if terrain_type == TerrainType.BRICK:
            if (x, y) == target_pos:
                base_cost = 2
            elif enemy and enemy.role == C.TankRole.ATTACKER:
                base_cost = 3

        if terrain_type == TerrainType.GRASS and \
                enemy and enemy.role == C.TankRole.SUPPORTER:
            base_cost *= 0.5

        return base_cost if base_cost < 999 else float('inf')

    # def get_neighbors(self, current_node, target_pos, context=None):
    #     """获取相邻节点"""
    #     neighbors = []
    #     for dx, dy in self.directions:
    #         new_x = current_node.x + dx
    #         new_y = current_node.y + dy
    #
    #         # 检查边界
    #         if not (0 <= new_x < self.width and 0 <= new_y < self.height):
    #             continue
    #
    #         # 获取地形代价（通过回调函数）
    #         base_cost = self.get_terrain_cost(new_x, new_y, target_pos, context)
    #
    #         # 如果可通行，创建新节点
    #         if base_cost < float('inf'):
    #             neighbor = PathNode(new_x, new_y, current_node)
    #             neighbor.g = current_node.g + base_cost
    #             neighbor.h = self.manhattan_distance(new_x, new_y,
    #                                                  target_pos[0], target_pos[1])
    #             neighbor.calculate_f()
    #             neighbors.append(neighbor)
    #
    #     return neighbors

    def get_neighbors(self, current_node, target_pos, context=None):
        """获取相邻节点，考虑2x2物体尺寸"""
        neighbors = []
        for dx, dy in self.directions:
            new_x = current_node.x + dx
            new_y = current_node.y + dy

            # 检查2x2区域是否都在边界内
            if not (0 <= new_x < self.width - 1 and 0 <= new_y < self.height - 1):
                continue

            # 检查2x2区域是否全部可通行（即所有4个格子代价都不是inf）
            positions_to_check = [
                (new_x, new_y),
                (new_x + 1, new_y),
                (new_x, new_y + 1),
                (new_x + 1, new_y + 1)
            ]

            valid = True
            total_cost = 0
            for px, py in positions_to_check:
                cost = self.get_terrain_cost(px, py, target_pos, context)
                if cost == float('inf'):
                    valid = False
                    break
                total_cost += cost
            if not valid:
                continue

            # 计算平均成本作为g值（也可以用最大/最小/其他策略）
            base_cost = total_cost / 4

            neighbor = PathNode(new_x, new_y, current_node)
            neighbor.g = current_node.g + base_cost
            neighbor.h = self.manhattan_distance(new_x, new_y,
                                                 target_pos[0], target_pos[1])
            neighbor.calculate_f()
            neighbors.append(neighbor)

        return neighbors

    @staticmethod
    def reconstruct_path(node):
        """重建路径"""
        path = []
        current = node
        while current:
            path.append((current.x, current.y))
            current = current.parent
        return path[::-1]

    def find_path(self, start_pos, target_pos, context=None):
        """A* 寻路主函数"""
        # 创建起始节点
        start_node = PathNode(start_pos[0], start_pos[1])
        start_node.h = self.manhattan_distance(start_pos[0], start_pos[1],
                                               target_pos[0], target_pos[1])
        start_node.calculate_f()

        # 初始化开放和关闭列表
        open_list = []
        open_set = {start_node}
        closed_set = set()

        # 将起点加入开放列表
        heapq.heappush(open_list, start_node)

        while open_list:
            current = heapq.heappop(open_list)
            open_set.remove(current)

            if (current.x, current.y) == target_pos:
                return self.reconstruct_path(current)

            closed_set.add(current)

            for neighbor in self.get_neighbors(current, target_pos, context):
                if neighbor in closed_set:
                    continue

                if neighbor not in open_set:
                    open_set.add(neighbor)
                    heapq.heappush(open_list, neighbor)
                else:
                    for node in open_list:
                        if node == neighbor and neighbor.g < node.g:
                            node.g = neighbor.g
                            node.parent = current
                            node.calculate_f()
                            heapq.heapify(open_list)
                            break

        return None