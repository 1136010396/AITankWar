import pygame
import random
from src.entry.tank import Tank
from src.entry.Path.pathNode import  PathFinder
from src.config import config as C
from src.control.map_manager import TerrainType
from enum import Enum
# from src.utils.constants import RED


class EnemyManager:
    def __init__(self, game):
        """
        初始化敌人管理器

        Args:
            game: Game实例的引用，用于访问游戏资源和状态
        """
        self.game = game
        self.enemies = pygame.sprite.Group()

        # 敌人生成配置
        self.max_enemies = 5  # 最大敌人数量
        self.spawn_cooldown = 2000  # 生成冷却时间（毫秒）
        self.last_spawn_time = 0  # 上次生成时间

        # 创建寻路器实例
        self.pathfinder = PathFinder(self.game,self.game.map_manager.w, self.game.map_manager.h)

        # 修正生成点坐标
        # x坐标：从左到右增长（0到630）
        # y坐标：从上到下增长（0到630）
        self.spawn_points = [
            {'x': 3, 'y': 3},  # 左上角
            {'x': 315, 'y': 3},  # 中上
            {'x': 630 - 51, 'y': 3}  # 右上角（减去坦克宽度48和边距3）
        ]
        # # 定义战术点（x, y 为网格坐标）
        self.tactical_points = {
            C.AttackRoute.LEFT: [
                {"x": 2, "y": 2},  # 左上出生点
                {"x": 2, "y": 8},  # 左侧中上
                {"x": 2, "y": 14},  # 左侧中下
                {"x": 2, "y": 20}  # 左侧底部
            ],
            C.AttackRoute.RIGHT: [
                {"x": 22, "y": 2},  # 右上出生点
                {"x": 22, "y": 8},  # 右侧中上
                {"x": 22, "y": 14},  # 右侧中下
                {"x": 22, "y": 20}  # 右侧底部
            ],
            C.AttackRoute.MIDDLE: [
                {"x": 12, "y": 2},  # 中上出生点
                {"x": 12, "y": 10},  # 中路隐蔽点
                {"x": 12, "y": 18},  # 中路进攻点
                {"x": 12, "y": 23}  # 基地前
            ]
        }

        # 每个角色的行为配置
        self.role_configs = {
            C.TankRole.ATTACKER: {
                "shoot_frequency": 0.1,  # 较高的射击频率
                "move_speed": 3,  # 标准移动速度
                "route_preference": [C.AttackRoute.MIDDLE]  # 偏好中路
            },
            C.TankRole.SUPPORTER: {
                "shoot_frequency": 0.05,  # 中等射击频率
                "move_speed": 4,  # 较快的移动速度
                "route_preference": [C.AttackRoute.LEFT, C.AttackRoute.RIGHT]  # 偏好侧路
            },
            C.TankRole.DEFENDER: {
                "shoot_frequency": 0.03,  # 较低的射击频率
                "move_speed": 2,  # 较慢的移动速度
                "route_preference": [C.AttackRoute.LEFT, C.AttackRoute.RIGHT]  # 偏好侧路
            }
        }



    def create_enemy(self, role, route):
        """创建特定角色和路线的敌方坦克"""
        spawn_point = self.tactical_points[route][0]
        x = spawn_point["x"] * 24 + C.MAP_OFFSET # 转换为像素坐标
        y = spawn_point["y"] * 24 + C.MAP_OFFSET

        enemy = Tank(x, y, self.game.image_manager.images, False)
        enemy.role = role
        enemy.route = route
        enemy.current_point_index = 0
        enemy.config = self.role_configs[role]

        return enemy

    def update_enemy_behavior(self, enemy):
        """更新敌方坦克的行为"""
        # 获取当前路线的战术点
        route_points = self.tactical_points[enemy.route]
        current_point = route_points[enemy.current_point_index]

        # 转换为网格坐标
        target_grid_x = current_point["x"]
        target_grid_y = current_point["y"]

        # 如果没有当前路径或需要重新规划
        if not hasattr(enemy, 'current_path') or not enemy.current_path:
            enemy.current_path = self.find_path(enemy, target_grid_x, target_grid_y)
            enemy.current_path_index = 0

        # 如果有可行路径
        if enemy.current_path and enemy.current_path_index < len(enemy.current_path):
            next_point = enemy.current_path[enemy.current_path_index]
            next_pixel_x, next_pixel_y = self.pathfinder.get_pixel_position(next_point[0], next_point[1])

            # 计算移动方向
            dx = next_pixel_x - enemy.rect.x
            dy = next_pixel_y - enemy.rect.y

            # 确定主要移动方向
            if abs(dx) > abs(dy):
                move_x = 1 if dx > 0 else -1
                move_y = 0
            else:
                move_x = 0
                move_y = 1 if dy > 0 else -1

            # 尝试移动
            sprite_groups = self.get_collision_groups(enemy)
            collision = enemy.move(self.game,move_x, move_y, self.game.screen, sprite_groups)

            # 如果到达当前路径点或遇到障碍
            if (abs(enemy.rect.x - next_pixel_x) < 5 and
                abs(enemy.rect.y - next_pixel_y) < 5):
                enemy.current_path_index += 1
            elif collision:
                # 遇到障碍，重新规划路径
                enemy.current_path = None

            # 处理射击
            self.handle_shooting(enemy)

        else:
            # 到达当前战术点，前进到下一个
            enemy.current_point_index = min(enemy.current_point_index + 1,
                                          len(route_points) - 1)
            enemy.current_path = None

    def handle_shooting(self, enemy):
        """处理坦克的射击行为"""
        # 获取射击概率
        shoot_chance = enemy.config["shoot_frequency"]

        # 根据角色调整射击策略
        if enemy.role == C.TankRole.ATTACKER:
            # 主攻手优先射击基地和障碍物
            if self.is_base_in_line(enemy):
                shoot_chance = 0.8  # 看到基地提高射击概率
            elif self.is_brick_in_line(enemy):
                shoot_chance = 0.3  # 看到砖块适度射击

        elif enemy.role == C.TankRole.SUPPORTER:
            # 支援手优先射击玩家和砖块
            if self.is_player_in_line(enemy):
                shoot_chance = 0.6  # 看到玩家提高射击概率
            elif self.is_brick_in_line(enemy):
                shoot_chance = 0.4  # 积极清理障碍物

        elif enemy.role == C.TankRole.DEFENDER:
            # 防守手主要响应玩家威胁
            if self.is_player_in_line(enemy):
                shoot_chance = 0.5  # 看到玩家立即反击

        # 随机决定是否射击
        if random.random() < shoot_chance:
            bullet = enemy.shoot(self.game.image_manager.images)
            if bullet:
                self.game.bullets.add(bullet)
                self.game.all_sprites.add(bullet)

    def is_base_in_line(self, enemy):
        """检查基地是否在坦克的射击线上"""
        # 获取坦克和基地的中心点
        tank_center = enemy.rect.center
        base_center = self.game.base.rect.center

        # 获取坦克当前朝向
        direction = enemy.direction

        # 根据朝向检查基地是否在射击线上
        if direction == C.UP:
            return (abs(tank_center[0] - base_center[0]) < 24 and  # 水平距离在一个格子内
                    tank_center[1] > base_center[1])               # 基地在坦克上方
        elif direction == C.DOWN:
            return (abs(tank_center[0] - base_center[0]) < 24 and
                    tank_center[1] < base_center[1])
        elif direction == C.LEFT:
            return (abs(tank_center[1] - base_center[1]) < 24 and
                    tank_center[0] > base_center[0])
        elif direction == C.RIGHT:
            return (abs(tank_center[1] - base_center[1]) < 24 and
                    tank_center[0] < base_center[0])
        return False

    def is_brick_in_line(self, enemy):
        """检查是否有砖块在坦克的射击线上"""
        # 获取坦克中心点
        tank_center = enemy.rect.center
        direction = enemy.direction

        # 设置射线检测的范围
        ray_length = 200  # 射线长度
        step = 24        # 检测步长（一个砖块的大小）

        # 根据方向计算射线终点
        if direction == C.UP:
            ray_end = (tank_center[0], tank_center[1] - ray_length)
        elif direction == C.DOWN:
            ray_end = (tank_center[0], tank_center[1] + ray_length)
        elif direction == C.LEFT:
            ray_end = (tank_center[0] - ray_length, tank_center[1])
        else:  # RIGHT
            ray_end = (tank_center[0] + ray_length, tank_center[1])

        # 创建射线矩形用于碰撞检测
        if direction in (C.UP, C.DOWN):
            ray_rect = pygame.Rect(
                tank_center[0] - 12,  # 射线宽度为24像素
                min(tank_center[1], ray_end[1]),
                24,
                abs(ray_end[1] - tank_center[1])
            )
        else:
            ray_rect = pygame.Rect(
                min(tank_center[0], ray_end[0]),
                tank_center[1] - 12,
                abs(ray_end[0] - tank_center[0]),
                24
            )

        # 检查射线是否与砖块相交
        for brick in self.game.map_manager.terrain_groups[TerrainType.BRICK]:
            if ray_rect.colliderect(brick.rect):
                # 确保砖块在射击方向上
                if direction == C.UP and brick.rect.bottom < tank_center[1]:
                    return True
                elif direction == C.DOWN and brick.rect.top > tank_center[1]:
                    return True
                elif direction == C.LEFT and brick.rect.right < tank_center[0]:
                    return True
                elif direction == C.RIGHT and brick.rect.left > tank_center[0]:
                    return True

        return False

    def is_player_in_line(self, enemy):
        """检查玩家是否在坦克的射击线上"""
        # 获取坦克和玩家的中心点
        tank_center = enemy.rect.center
        player_center = self.game.player.rect.center
        direction = enemy.direction

        # 设置判定阈值
        threshold = 24  # 允许的偏差范围

        # 检查是否有障碍物阻挡
        if self.is_path_blocked(tank_center, player_center, direction):
            return False

        # 根据方向检查玩家是否在射击线上
        if direction == C.UP:
            return (abs(tank_center[0] - player_center[0]) < threshold and
                    tank_center[1] > player_center[1])
        elif direction == C.DOWN:
            return (abs(tank_center[0] - player_center[0]) < threshold and
                    tank_center[1] < player_center[1])
        elif direction == C.LEFT:
            return (abs(tank_center[1] - player_center[1]) < threshold and
                    tank_center[0] > player_center[0])
        elif direction == C.RIGHT:
            return (abs(tank_center[1] - player_center[1]) < threshold and
                    tank_center[0] < player_center[0])
        return False

    def is_path_blocked(self, start, end, direction):
        """检查两点之间是否有障碍物"""
        # 创建射线矩形
        if direction in (C.UP, C.DOWN):
            ray_rect = pygame.Rect(
                start[0] - 12,
                min(start[1], end[1]),
                24,
                abs(end[1] - start[1])
            )
        else:
            ray_rect = pygame.Rect(
                min(start[0], end[0]),
                start[1] - 12,
                abs(end[0] - start[0]),
                24
            )

        # 检查是否与不可穿透的地形相交
        for terrain_type in [TerrainType.BRICK, TerrainType.IRON]:
            terrain_group = self.game.map_manager.terrain_groups[terrain_type]
            for terrain in terrain_group:
                if ray_rect.colliderect(terrain.rect):
                    # 确保障碍物在射击路径上
                    if direction == C.UP and terrain.rect.bottom < start[1]:
                        return True
                    elif direction == C.DOWN and terrain.rect.top > start[1]:
                        return True
                    elif direction == C.LEFT and terrain.rect.right < start[0]:
                        return True
                    elif direction == C.RIGHT and terrain.rect.left > start[0]:
                        return True

        return False

    def get_shooting_score(self, enemy):
        """计算当前射击价值"""
        score = 0

        # 检查各种目标并计算分数
        if self.is_base_in_line(enemy):
            score += 100  # 基地最高优先级
        if self.is_player_in_line(enemy):
            score += 80   # 玩家次高优先级
        if self.is_brick_in_line(enemy):
            score += 30   # 砖块最低优先级

        # 根据角色调整分数
        if enemy.role == C.TankRole.ATTACKER:
            if self.is_base_in_line(enemy):
                score *= 1.5  # 主攻手更重视基地
        elif enemy.role == C.TankRole.SUPPORTER:
            if self.is_brick_in_line(enemy):
                score *= 1.3  # 支援手更重视清理障碍
        elif enemy.role == C.TankRole.DEFENDER:
            if self.is_player_in_line(enemy):
                score *= 1.4  # 防守手更重视攻击玩家

        return score


    def spawn_enemy(self):
        """生成新的敌方坦克"""
        if len(self.enemies) >= self.max_enemies:
            return

        # 分配角色和路线
        current_roles = [enemy.role for enemy in self.enemies]

        # 优先补充缺失的角色
        if C.TankRole.ATTACKER not in current_roles:
            role = C.TankRole.ATTACKER
            route = C.AttackRoute.MIDDLE
        elif C.TankRole.SUPPORTER not in current_roles:
            role = C.TankRole.SUPPORTER
            route = random.choice([C.AttackRoute.LEFT, C.AttackRoute.RIGHT])
        elif C.TankRole.DEFENDER not in current_roles:
            role = C.TankRole.DEFENDER
            route = random.choice([C.AttackRoute.LEFT, C.AttackRoute.RIGHT])
        else:
            # 随机选择角色和路线
            role = random.choice(list(C.TankRole))
            route = random.choice(self.role_configs[role]["route_preference"])

        # 创建坦克
        enemy = self.create_enemy(role, route)
        self.enemies.add(enemy)
        self.game.all_sprites.add(enemy)

    def update(self):
        """更新所有敌方坦克"""
        current_time = pygame.time.get_ticks()

        # 生成新坦克
        if current_time - self.last_spawn_time > self.spawn_cooldown:
            self.spawn_enemy()
            self.last_spawn_time = current_time

        # 更新每个坦克的行为
        for enemy in self.enemies:
            self.update_enemy_behavior(enemy)


    # def update(self):
    #     """更新敌人状态"""
    #     # 检查是否需要生成新敌人
    #     current_time = pygame.time.get_ticks()
    #     if (current_time - self.last_spawn_time > self.spawn_cooldown and
    #             len(self.enemies) < self.max_enemies):
    #         self.spawn_enemy()
    #         self.last_spawn_time = current_time
    #
    #     # 更新所有敌人的AI行为
    #     for enemy in self.enemies:
    #         self.update_enemy_ai(enemy)

    def update_enemy_ai(self, enemy):
        """更新单个敌人的AI行为"""
        # 计算到基地的方向
        dx = self.game.base.rect.centerx - enemy.rect.centerx
        dy = self.game.base.rect.centery - enemy.rect.centery

        # 决定移动方向（只能上下左右）
        if abs(dx) > abs(dy):
            # 水平移动
            dx = 1 if dx > 0 else -1
            dy = 0
        else:
            # 垂直移动
            dx = 0
            dy = 1 if dy > 0 else -1

        # 随机改变方向（增加一些随机性）
        if random.random() < 0.02:  # 2% 的概率随机改变方向
            directions = [
                (0, -1),  # 上
                (0, 1),  # 下
                (-1, 0),  # 左
                (1, 0)  # 右
            ]
            dx, dy = random.choice(directions)

        # 尝试移动
        sprite_groups = self.get_collision_groups(enemy)
        enemy.move(self.game,dx, dy, self.game.screen, sprite_groups)


        # 随机发射子弹
        if random.random() < 0.01:  # 1% 的概率发射子弹
            bullet = enemy.shoot(self.game.image_manager.images)
            if bullet:
                self.game.bullets.add(bullet)
                self.game.all_sprites.add(bullet)


    def get_collision_groups(self, enemy):
        """获取碰撞检测组（排除自己）"""
        other_enemies = pygame.sprite.Group([e for e in self.enemies if e != enemy])
        return {
            'enemies': other_enemies,
            'base': pygame.sprite.Group(self.game.base),
            'player': pygame.sprite.Group(self.game.player),
            # 'brick': self.game.map_manager.brick_group,
            # 'iron': self.game.map_manager.iron_group
        }

    def is_position_clear(self, x, y, width=48, height=48):
        """检查指定位置是否没有障碍物"""
        temp_rect = pygame.Rect(x, y, width, height)

        # collision = False
        # 检查与地形的碰撞
        for terrain_type, group in self.game.map_manager.terrain_groups.items():
            for terrain in group:
                if (temp_rect.colliderect(terrain.rect) and
                        not terrain.can_pass_tank()):
                    # collision = True
                    return False

        # # 检查与地形的碰撞
        # for brick in self.game.map_manager.brick_group:
        #     if temp_rect.colliderect(brick.rect):
        #         return False
        #
        # for iron in self.game.map_manager.iron_group:
        #     if temp_rect.colliderect(iron.rect):
        #         return False

        # 检查与其他敌人的碰撞
        for enemy in self.enemies:
            if temp_rect.colliderect(enemy.rect):
                return False

        # 检查与玩家的碰撞
        if temp_rect.colliderect(self.game.player.rect):
            return False

        return True

    def get_valid_spawn_position(self):
        """获取一个有效的敌人生成位置"""
        spawn_points = self.spawn_points.copy()
        random.shuffle(spawn_points)

        for point in spawn_points:
            if self.is_position_clear(point['x'], point['y']):
                return point['x'], point['y']

        return None

    # def spawn_enemy(self):
    #     """生成敌人"""
    #     spawn_pos = self.get_valid_spawn_position()
    #     if spawn_pos:
    #         x, y = spawn_pos
    #         enemy = Tank(x, y, self.game.image_manager.images, False)
    #         self.enemies.add(enemy)
    #         self.game.all_sprites.add(enemy)

    def clear(self):
        """清除所有敌人"""
        self.enemies.empty()

    def find_path(self, enemy, target_x, target_y):
        """使用PathFinder查找路径"""
        start_x, start_y = self.pathfinder.get_grid_position(enemy.rect.x, enemy.rect.y)
        return self.pathfinder.find_path(
            (start_x, start_y),
            (target_x, target_y),
            enemy  # 传入enemy作为上下文
        )






