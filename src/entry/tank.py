import pygame
from src.entry.bullet import Bullet
from src.attribute.collision import CollisionBox, CollisionType
from src.attribute.cooldown_system import CooldownSystem
import src.config.config as C

tank_T1_0 = r"..\image\tank\tank_T1_0.png"

# 坦克类
class Tank(pygame.sprite.Sprite):
    def __init__(self, x, y,images, is_player=False):
        super().__init__()

        self.is_player = is_player
        self.life = 3 if is_player else 1
        # self.speed = 3
        self.speed = 4
        self.direction = C.UP
        self.level=3
        self.bulletLevel=3

        self.collision_box = CollisionBox(
            width=C.TANK_SIZE[0],  # 坦克主体碰撞箱宽度
            height=C.TANK_SIZE[1],  # 坦克主体碰撞箱高度
            collision_type=CollisionType.RECTANGLE
        )

        # 创建用于碰撞检测的矩形，比视觉大小小一些
        # self.collision_rect = pygame.Rect(0, 0, C.TANK_SIZE[0]-2, C.TANK_SIZE[1]-2)  # 比48x48稍小

        if is_player:
            self.tank_L0 = images['tank_T1_0']
            self.tank_L1 = images['tank_T1_1']
            self.tank_L2 = images['tank_T1_2']
        else:
            self.tank_L0 = images['enemy_1_0']
            self.tank_L1 = self.tank_L0  # 敌人坦克没有等级区分
            self.tank_L2 = self.tank_L0

        # 当前使用的坦克图片
        self.tank = self.tank_L0

        self.tank_R0 = self.tank.subsurface((0, 0), (48, 48))
        self.tank_R1 = self.tank.subsurface((48, 0), (48, 48))
        self.image = self.tank_R0
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

          # 0: 上, 1: 右, 2: 下, 3: 左
        # 移动相关
        self.dir_x, self.dir_y = 0, -1
        self.moving = False
        self.frame = 0  # 用于动画切换

        # # 射击相关
        # self.bullet_cooling = False
        self.cooldown_system = CooldownSystem(self)

    def update_collision_rect(self):
        """更新碰撞矩形的位置"""
        # 保持碰撞矩形在视觉矩形的中心
        self.collision_rect.centerx = self.rect.centerx
        self.collision_rect.centery = self.rect.centery

    def move(self,gameEntity, dx, dy, screen, sprite_groups=None):
        if sprite_groups is None:
            sprite_groups = {}

        old_x, old_y = self.rect.x, self.rect.y
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        _,_,w,h=screen.get_rect()
        if self.rect.x > h - 3 or self.rect.x < 3:
            self.rect.x, self.rect.y = old_x, old_y
        elif self.rect.y > w - 3 or self.rect.y < 3:
            self.rect.x, self.rect.y = old_x, old_y
        # self.rect.clamp_ip(screen.get_rect())

        # 确定朝向
        if dx == 0 and dy < 0:  # 上
            self.direction = C.UP
            self.tank_R0 = self.tank.subsurface((0, 0), (48, 48))
            self.tank_R1 = self.tank.subsurface((48, 0), (48, 48))
        elif dx > 0 and dy == 0:  # 右
            self.direction = C.RIGHT
            self.tank_R0 = self.tank.subsurface((0, 144), (48, 48))
            self.tank_R1 = self.tank.subsurface((48, 144), (48, 48))
        elif dx == 0 and dy > 0:  # 下
            self.direction = C.DOWN
            self.tank_R0 = self.tank.subsurface((0, 48), (48, 48))
            self.tank_R1 = self.tank.subsurface((48, 48), (48, 48))
        elif dx < 0 and dy == 0:  # 左
            self.direction = C.LEFT
            self.tank_R0 = self.tank.subsurface((0, 96), (48, 48))
            self.tank_R1 = self.tank.subsurface((48, 96), (48, 48))

        # 更新动画
        self.frame = self.frame ^ 1
        self.image = self.tank_R0 if self.frame else self.tank_R1

        collision=False
        # 检查与地形的碰撞
        for terrain_type, group in gameEntity.map_manager.terrain_groups.items():
            for terrain in group:
                if (self.rect.colliderect(terrain.rect) and
                        not terrain.can_pass_tank()):
                    collision = True
                    break
            if collision:
                break

        # 分别检查不同类型的碰撞
        if not collision:
            for group in sprite_groups.values():
                if group is None:
                    continue
                if pygame.sprite.spritecollide(self, group, False, None):
                    collision = True
                    break


        # 如果发生碰撞，恢复位置
        if collision:
            self.rect.x = old_x
            self.rect.y = old_y

        return collision


        # self.moving = (dx != 0 or dy != 0)
        # if self.moving:
        #     self.frame = self.frame ^ 1
        #     self.image = self.tank_R0 if self.frame else self.tank_R1

    def rotate(self, direction):
        self.direction = direction

    def shoot(self, bullet_images):
        # 检查冷却是否完成
        if not self.cooldown_system.can_shoot():
            return None

        # # 计算坦克中心点
        tank_center_x = self.rect.centerx
        tank_center_y = self.rect.centery
        # dx, dy = 0, 0
        bullet_offset=12//2

        # 根据方向计算子弹初始位置
        if self.direction == C.UP:
            bullet_x = tank_center_x - bullet_offset
            bullet_y = self.rect.top
            dx,dy = 0, -1
        elif self.direction == C.DOWN:
            bullet_x = tank_center_x - bullet_offset
            bullet_y = self.rect.bottom
            dx,dy = 0, 1
        elif self.direction == C.LEFT:
            bullet_x = self.rect.left
            bullet_y = tank_center_y - bullet_offset
            dx,dy = -1, 0
        else:  # RIGHT
            bullet_x = self.rect.right
            bullet_y = tank_center_y - bullet_offset
            dx,dy = 1, 0

        bullet = Bullet(bullet_x, bullet_y, dx,dy,
                        self.is_player, bullet_images,level=self.bulletLevel)
        self.cooldown_system.start_cooldown()
        # self.last_shot_time = current_time

        return bullet

        # if self.direction == C.UP:  # 上
        #     return Bullet(self.rect.centerx, self.rect.top, 0, -1, self.is_player, bullet_images)
        # elif self.direction == C.RIGHT:  # 右
        #     return Bullet(self.rect.right, self.rect.centery, 1, 0, self.is_player, bullet_images)
        # elif self.direction == C.DOWN:  # 下
        #     return Bullet(self.rect.centerx, self.rect.bottom, 0, 1, self.is_player, bullet_images)
        # else:  # 左
        #     return Bullet(self.rect.left, self.rect.centery, -1, 0, self.is_player, bullet_images)
