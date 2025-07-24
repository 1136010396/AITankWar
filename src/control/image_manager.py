import pygame
from pygame.examples.aliens import load_image


class ImageManager:
    def __init__(self):
        self.images = {}
        self._initialized = False
        self.init()

    def load_image(self, name, path,scale_size=None):
        if name not in self.images:
            try:
                image = pygame.image.load(path).convert_alpha()

                # 如果指定了缩放尺寸
                if scale_size:
                    self.images[name]  = pygame.transform.smoothscale(image, scale_size)
                else :
                    self.images[name] = image
            except pygame.error as e:
                print(f"无法加载图片 {name}: {e}")
                # 加载失败时使用一个默认的占位图片
                self.images[name] = self.create_placeholder_image()
        return self.images[name]

    def get_image(self, name):
        return self.images.get(name)

    def create_placeholder_image(self):
        # 创建一个简单的占位图片
        surface = pygame.Surface((32, 32))
        surface.fill((255, 0, 255))  # 使用醒目的粉色
        return surface

    def init(self):
        if self._initialized:
            return
        base_path = "data/image"
        # 子弹图片
        self.load_image('bullet_up', f"{base_path}/bullet/bullet_up.png")
        self.load_image('bullet_down', f"{base_path}/bullet/bullet_down.png")
        self.load_image('bullet_left', f"{base_path}/bullet/bullet_left.png")
        self.load_image('bullet_right', f"{base_path}/bullet/bullet_right.png")

        # 地形图片
        self.load_image('brick', f"{base_path}/terrain/brick.png")
        self.load_image('iron', f"{base_path}/terrain/iron.png")
        self.load_image('river', f"{base_path}/terrain/river1.png",scale_size=(24,24))
        self.load_image('grass', f"{base_path}/terrain/tree.png",scale_size=(24,24))  # 草丛需要透明
        # 为草丛添加半透明效果
        self.images['grass'].set_alpha(128)


        # 坦克图片
        self.load_image('tank_T1_0', f"{base_path}/tank/tank_T1_0.png")
        self.load_image('tank_T1_1', f"{base_path}/tank/tank_T1_1.png")
        self.load_image('tank_T1_2', f"{base_path}/tank/tank_T1_2.png")
        self.load_image('enemy_1_0', f"{base_path}/tank/enemy_1_0.png")

        # 基地图片
        self.load_image('base', f"{base_path}/base/home.png")

        # 状态图片
        self.load_image('gameOver', f"{base_path}/status/gameover.png")

        self._initialized = True

