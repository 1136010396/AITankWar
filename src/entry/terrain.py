import pygame
from src.attribute.collision import CollisionBox, CollisionType
import src.config.config as C
from src.data.maps.map_data import CLASSIC_MAP

from enum import Enum

class TerrainType(Enum):
    BRICK = "brick"      # 砖块
    IRON = "iron"       # 铁块
    RIVER = "river"     # 河流
    GRASS = "grass"     # 草丛


class Terrain(pygame.sprite.Sprite):
    def __init__(self, x, y, terrain_type, images):
        super().__init__()
        self.terrain_type = terrain_type

        # 加载地形图片
        self.image = images[terrain_type.value]

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # 设置地形属性
        self.properties = {
            TerrainType.BRICK: {
                "destructible": True,  # 可破坏
                "bullet_pass": False,  # 子弹不可穿过
                "tank_pass": False,  # 坦克不可穿过
                "min_bullet_level": 1  # 最小可破坏子弹等级
            },
            TerrainType.IRON: {
                "destructible": True,
                "bullet_pass": False,
                "tank_pass": False,
                "min_bullet_level": 3  # 需要高等级子弹
            },
            TerrainType.RIVER: {
                "destructible": False,
                "bullet_pass": True,  # 子弹可穿过
                "tank_pass": False,  # 坦克不可穿过
                "min_bullet_level": 999  # 不可破坏
            },
            TerrainType.GRASS: {
                "destructible": False,
                "bullet_pass": True,  # 子弹可穿过
                "tank_pass": True,  # 坦克可穿过
                "min_bullet_level": 999  # 不可破坏
            }
        }[terrain_type]

        # 设置碰撞体积
        self.collision_box = CollisionBox(
            width=C.LITTLE_BLOCK[0],  # 砖块大小
            height=C.LITTLE_BLOCK[1],
            collision_type=CollisionType.RECTANGLE
        )

    def hit(self, bullet):
        """处理被子弹击中的效果"""
        if self.terrain_type == 'brick':
            # 普通砖块可以被任何子弹摧毁
            return True
        elif self.terrain_type == 'iron':
            # 铁块只能被强力子弹摧毁
            return bullet.strong
        return False

    def can_be_destroyed_by(self, bullet):
        """检查是否可以被指定子弹摧毁"""
        return (self.properties["destructible"] and
                bullet.level >= self.properties["min_bullet_level"])

    def can_pass_bullet(self):
        """检查是否允许子弹通过"""
        return self.properties["bullet_pass"]

    def can_pass_tank(self):
        """检查是否允许坦克通过"""
        return self.properties["tank_pass"]