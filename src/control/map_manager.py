import pygame
import src.config.config as C
from src.entry.terrain import Terrain, TerrainType
from src.data.maps.map_data import CLASSIC_MAP


class MapManager:
    def __init__(self, image_manager):
        self.image_manager = image_manager
        # self.brick_group = pygame.sprite.Group()
        # self.iron_group = pygame.sprite.Group()
        self.terrain_groups = {
            TerrainType.BRICK: pygame.sprite.Group(),
            TerrainType.IRON: pygame.sprite.Group(),
            TerrainType.RIVER: pygame.sprite.Group(),
            TerrainType.GRASS: pygame.sprite.Group()
        }
        # 默认地图
        self.load_map(CLASSIC_MAP)


    def load_map(self, map_data):
        """
        加载地图数据
        map_data: 二维列表，表示地图布局
        0: 空地
        1: 砖块
        2: 铁块
        """
        self.clear_map()

        for row_idx, row in enumerate(map_data):
            for col_idx, cell in enumerate(row):
                x = col_idx * C.LITTLE_BLOCK[0]# 24是地形块的大小
                y = row_idx * C.LITTLE_BLOCK[1]

                if cell == C.BRICK:
                    self.create_terrain(x, y, TerrainType.BRICK)
                elif cell == C.IRON:
                    self.create_terrain(x, y, TerrainType.IRON)
                elif cell == C.RIVER:
                    self.create_terrain(x, y, TerrainType.RIVER)
                elif cell == C.GRASS:
                    self.create_terrain(x, y, TerrainType.GRASS)
                elif cell==C.BASE:
                    self.base=(x,y)
                elif cell==C.PLAYER:
                    self.player=(x,y)
        self.base = [i - 24 for i in self.base]
        self.player = [i - 24 for i in self.player]
        self.h=len(map_data)
        self.w=len(map_data[0])

    def create_terrain(self, x, y, terrain_type):
        """创建地形"""
        terrain = Terrain(x+C.MAP_OFFSET, y+C.MAP_OFFSET, terrain_type, self.image_manager.images)
        # terrain = Terrain(x, y, terrain_type, self.image_manager.images)
        self.terrain_groups[terrain_type].add(terrain)
        return terrain

    def clear_map(self):
        """清除当前地图"""
        # self.brick_group.empty()
        # self.iron_group.empty()
        for group in self.terrain_groups.values():
            group.empty()

    def draw(self, screen):
        # """绘制地图"""
        # self.brick_group.draw(screen)
        # self.iron_group.draw(screen)

        """绘制地图（注意绘制顺序）"""
        # 先绘制不透明地形
        for terrain_type in [TerrainType.BRICK, TerrainType.IRON, TerrainType.RIVER]:
            self.terrain_groups[terrain_type].draw(screen)

        # 最后绘制草丛（半透明）
        for grass in self.terrain_groups[TerrainType.GRASS]:
            screen.blit(grass.image, grass.rect)