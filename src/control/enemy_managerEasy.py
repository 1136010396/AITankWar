import pygame
import random
from src.entry.tank import Tank
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

        # 修正生成点坐标
        # x坐标：从左到右增长（0到630）
        # y坐标：从上到下增长（0到630）
        self.spawn_points = [
            {'x': 3, 'y': 3},  # 左上角
            {'x': 315, 'y': 3},  # 中上
            {'x': 630 - 51, 'y': 3}  # 右上角（减去坦克宽度48和边距3）
        ]


    def update(self):
        """更新敌人状态"""
        # 检查是否需要生成新敌人
        current_time = pygame.time.get_ticks()
        if (current_time - self.last_spawn_time > self.spawn_cooldown and
                len(self.enemies) < self.max_enemies):
            self.spawn_enemy()
            self.last_spawn_time = current_time

        # 更新所有敌人的AI行为
        for enemy in self.enemies:
            self.update_enemy_ai(enemy)

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

    def spawn_enemy(self):
        """生成敌人"""
        spawn_pos = self.get_valid_spawn_position()
        if spawn_pos:
            x, y = spawn_pos
            enemy = Tank(x, y, self.game.image_manager.images, False)
            self.enemies.add(enemy)
            self.game.all_sprites.add(enemy)

    def clear(self):
        """清除所有敌人"""
        self.enemies.empty()