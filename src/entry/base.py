import pygame
from src.attribute.collision import CollisionBox, CollisionType
import src.config.config as C

# 大本营类
class Base(pygame.sprite.Sprite):
    def __init__(self, x, y, images):
        super().__init__()
        self.image = images['base']
        # self.image.fill(C.BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # 设置基地的碰撞体积（使用较精确的矩形碰撞）
        self.collision_box = CollisionBox(
            width=C.BASE_SIZE[0],  # 基地碰撞箱宽度
            height=C.BASE_SIZE[1],  # 基地碰撞箱高度
            collision_type=CollisionType.RECTANGLE
        )
