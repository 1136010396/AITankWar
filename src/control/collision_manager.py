import pygame
from src.attribute.collision import CollisionBox, CollisionType

class CollisionManager:
    @staticmethod
    def check_collision(sprite1, sprite2):
        """
        检查两个精灵之间的碰撞

        Args:
            sprite1: 第一个精灵
            sprite2: 第二个精灵

        Returns:
            bool: 是否发生碰撞
        """
        # 获取碰撞体积
        collision_box1 = getattr(sprite1, 'collision_box', None)
        collision_box2 = getattr(sprite2, 'collision_box', None)

        # 如果没有定义碰撞体积，使用默认的rect
        if collision_box1 is None or collision_box2 is None:
            return pygame.sprite.collide_rect(sprite1, sprite2)

        rect1 = collision_box1.get_rect(sprite1.rect)
        rect2 = collision_box2.get_rect(sprite2.rect)

        # 根据碰撞类型进行检测
        if (collision_box1.collision_type == CollisionType.CIRCLE and
                collision_box2.collision_type == CollisionType.CIRCLE):
            # 圆形与圆形的碰撞
            center1 = rect1.center
            center2 = rect2.center
            distance = ((center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2) ** 0.5
            return distance < (collision_box1.radius + collision_box2.radius)

        elif (collision_box1.collision_type == CollisionType.RECTANGLE and
              collision_box2.collision_type == CollisionType.RECTANGLE):
            # 矩形与矩形的碰撞
            return rect1.colliderect(rect2)

        else:
            # 圆形与矩形的碰撞
            if collision_box1.collision_type == CollisionType.CIRCLE:
                circle_rect = rect1
                circle_radius = collision_box1.radius
                rect = rect2
            else:
                circle_rect = rect2
                circle_radius = collision_box2.radius
                rect = rect1

            # 计算圆心到矩形的最短距离
            circle_center = circle_rect.center
            closest_x = max(rect.left, min(circle_center[0], rect.right))
            closest_y = max(rect.top, min(circle_center[1], rect.bottom))

            distance = ((circle_center[0] - closest_x) ** 2 +
                        (circle_center[1] - closest_y) ** 2) ** 0.5

            return distance < circle_radius