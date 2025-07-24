from enum import Enum
import pygame


class CollisionType(Enum):
    RECTANGLE = 0  # 矩形碰撞
    CIRCLE = 1  # 圆形碰撞
    COMPOSITE = 2  # 组合碰撞（多个碰撞体）


class CollisionBox:
    def __init__(self, offset_x=0, offset_y=0, width=0, height=0, collision_type=CollisionType.RECTANGLE, radius=0):
        """
        初始化碰撞体积

        Args:
            offset_x: 相对于精灵中心的X偏移
            offset_y: 相对于精灵中心的Y偏移
            width: 矩形宽度
            height: 矩形高度
            collision_type: 碰撞类型
            radius: 圆形碰撞体半径
        """
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.width = width
        self.height = height
        self.collision_type = collision_type
        self.radius = radius

    def get_rect(self, sprite_rect):
        """获取实际的碰撞矩形"""
        if self.collision_type == CollisionType.RECTANGLE:
            return pygame.Rect(
                sprite_rect.centerx + self.offset_x - self.width // 2,
                sprite_rect.centery + self.offset_y - self.height // 2,
                self.width,
                self.height
            )
        elif self.collision_type == CollisionType.CIRCLE:
            return pygame.Rect(
                sprite_rect.centerx + self.offset_x - self.radius,
                sprite_rect.centery + self.offset_y - self.radius,
                self.radius * 2,
                self.radius * 2
            )
        return sprite_rect
