import pygame
import src.config.config as C
from src.attribute.collision import CollisionBox, CollisionType
# 子弹类
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, is_player_bullet, image_manager,level=2):
        super().__init__()
        # self.image = pygame.Surface((10, 10))
        # self.image.fill(GREEN if is_player_bullet else RED)  # 玩家子弹为绿色，敌人子弹为红色
        # 强力子弹可以穿透
        self.strong = False
        self.level=level

        self.speed = 5
        self.dx = dx
        self.dy = dy
        self.is_player_bullet = is_player_bullet  # 新增属性，标识是否为玩家的子弹

        if dy < 0:
            self.image = image_manager['bullet_up']
        elif dy > 0:
            self.image = image_manager['bullet_down']
        elif dx < 0:
            self.image = image_manager['bullet_left']
        else:
            self.image = image_manager['bullet_right']

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # self.collision_box = CollisionBox(
        #     radius=4,  # 子弹碰撞半径（比视觉大小小一些）
        #     collision_type=CollisionType.CIRCLE
        # )

    def update(self):
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed

        # 如果子弹移出屏幕，则删除它
        if self.rect.bottom < 0 or self.rect.top > C.SCREEN_HEIGHT or \
           self.rect.right < 0 or self.rect.left > C.SCREEN_WIDTH:
            self.kill()