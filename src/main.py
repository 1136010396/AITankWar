import pygame
import os
import pygame.freetype
from src.config import config as C
from src.mode.infinite import InfiniteGame
from src.mode.singleFight import SingleFightGame
from src.entry.Button import Button

MAIN_WIDTH=606

class GameMenu:
    def __init__(self):
        self.reset_to_menu()

    def clear(self):
        pygame.init()
        # self.screen = pygame.display.set_mode((800, 600))
        self.screen = pygame.display.set_mode((MAIN_WIDTH, 630))
        pygame.display.set_caption("坦克大战 - 主菜单")
        self.clock = pygame.time.Clock()
        self.current_mode = None

    def reset_to_menu(self):
        pygame.init()
        # self.screen = pygame.display.set_mode((800, 600))
        self.screen = pygame.display.set_mode((MAIN_WIDTH, 630))
        pygame.display.set_caption("坦克大战 - 主菜单")
        self.clock = pygame.time.Clock()
        self.current_mode = None

        # 菜单状态
        self.current_state = "main"  # "main", "level_select"

        # # 加载字体
        # self.title_font = pygame.font.Font(None, 74)
        # self.normal_font = pygame.font.Font(None, 36)
        # 加载中文字体
        self.load_fonts()

        # 关卡配置
        self.max_levels = 2
        self.unlocked_levels = self.load_unlocked_levels()

        # 创建按钮
        self.create_buttons()

        # 加载背景图片
        self.background = pygame.image.load("data/image/menu/background.png")
        # self.background = pygame.transform.scale(self.background, (800, 600))
        self.background = pygame.transform.scale(self.background, (MAIN_WIDTH, 630))

    def load_fonts(self):
        """加载字体"""
        try:
            # 尝试加载系统中文字体
            font_paths = [
                "C:/Windows/Fonts/msyh.ttc",  # Windows 微软雅黑
                "C:/Windows/Fonts/simhei.ttf",  # Windows 黑体
                "/System/Library/Fonts/PingFang.ttc",  # macOS
                "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf"  # Linux
            ]

            font_path = None
            for path in font_paths:
                if os.path.exists(path):
                    font_path = path
                    break

            if font_path:
                self.title_font = pygame.font.Font(font_path, 74)
                self.normal_font = pygame.font.Font(font_path, 36)
            else:
                # 如果找不到系统字体，使用项目自带的字体
                font_path = "src/assets/fonts/msyh.ttc"  # 确保这个路径下有字体文件
                self.title_font = pygame.font.Font(font_path, 74)
                self.normal_font = pygame.font.Font(font_path, 36)

        except Exception as e:
            print(f"加载字体失败: {e}")
            # 使用默认字体作为后备
            self.title_font = pygame.font.Font(None, 74)
            self.normal_font = pygame.font.Font(None, 36)

    def create_buttons(self):
        """创建所有按钮"""
        button_style = {
            "text_size": 36,
            "bg_color": (50, 50, 50),
            "text_color": (255, 255, 255),
            "hover_color": (70, 70, 70),
            "font_path": self.normal_font  # 传入中文字体
        }

        # 主菜单按钮
        self.main_menu_buttons = [
            Button(
                centerx=MAIN_WIDTH//2,
                centery=250,
                width=200,
                height=50,
                text="无尽模式",
                **button_style
            ),
            Button(
                centerx=MAIN_WIDTH//2,
                centery=320,
                width=200,
                height=50,
                text="单关模式",
                **button_style
            ),
            Button(
                centerx=MAIN_WIDTH//2,
                centery=390,
                width=200,
                height=50,
                text="退出游戏",
                **button_style
            )
        ]

        button_style["text_size"] = 30
        # 返回按钮
        self.back_button = Button(
            centerx=100,
            centery=50,
            width=120,
            height=40,
            text="返回",
            **button_style
        )

        # 创建关卡选择按钮
        self.level_buttons = []
        buttons_per_row = 5
        button_width = 100
        button_height = 50
        margin = 20
        start_x = (800 - (button_width * buttons_per_row + margin * (buttons_per_row - 1))) // 2
        start_y = 150

        for level in range(1, self.max_levels + 1):
            row = (level - 1) // buttons_per_row
            col = (level - 1) % buttons_per_row
            x = start_x + col * (button_width + margin)
            y = start_y + row * (button_height + margin)

            self.level_buttons.append(
                Button(
                    centerx=x + button_width // 2,
                    centery=y + button_height // 2,
                    width=button_width,
                    height=button_height,
                    text=f"关卡 {level}",
                    **button_style
                )
            )

    def load_unlocked_levels(self):
        """加载已解锁的关卡"""
        # 这里可以从存档文件加载，现在先默认解锁前3关
        return set(range(1, 4))

    def show_menu(self):
        # """显示菜单界面"""
        # running = True
        # while running:
        self.handle_menu_events()
        self.draw_menu()
        self.clock.tick(60)

    def handle_menu_events(self):
        """处理菜单事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos

                if self.current_state == "main":
                    # 主菜单按钮检测
                    for i, button in enumerate(self.main_menu_buttons):
                        if button.is_clicked(mouse_pos):
                            if i == 0:  # 无尽模式
                                self.current_mode = InfiniteGame()
                                return
                            elif i == 1:  # 单关模式
                                self.current_state = "level_select"
                                self.clear()
                            elif i == 2:  # 退出游戏
                                pygame.quit()
                                exit()

                elif self.current_state == "level_select":
                    # 返回按钮检测
                    if self.back_button.is_clicked(mouse_pos):
                        self.current_state = "main"
                        self.clear()
                        return

                    # 关卡按钮检测
                    for i, button in enumerate(self.level_buttons):
                        if button.is_clicked(mouse_pos):
                            level = i + 1
                            if level in self.unlocked_levels:
                                self.current_mode = SingleFightGame(C.LEVEL_DIR[level])
                                return

    def draw_menu(self):

        """绘制菜单界面"""
        # 绘制背景
        self.screen.blit(self.background, (0, 0))

        # 绘制标题
        title_text = "坦克大战"
        title_surface = self.title_font.render(title_text, True, (0, 0, 255))
        title_rect = title_surface.get_rect(center=(MAIN_WIDTH//2, 100))
        self.screen.blit(title_surface, title_rect)

        if self.current_state == "main":
            # 绘制主菜单按钮
            for button in self.main_menu_buttons:
                button.draw(self.screen)

        elif self.current_state == "level_select":
            # 绘制返回按钮
            self.back_button.draw(self.screen)

            # 绘制关卡选择标题
            select_text = "选择关卡"
            select_surface = self.normal_font.render(select_text, True, (255, 255, 255))
            select_rect = select_surface.get_rect(center=(400, 50))
            self.screen.blit(select_surface, select_rect)

            # 绘制关卡按钮
            for i, button in enumerate(self.level_buttons):
                level = i + 1
                # 根据解锁状态设置按钮颜色
                if level in self.unlocked_levels:
                    button.bg_color = (50, 50, 50)
                    button.text_color = (255, 255, 255)
                else:
                    button.bg_color = (30, 30, 30)
                    button.text_color = (100, 100, 100)
                button.draw(self.screen)

        pygame.display.flip()

    def run(self):
        """运行游戏菜单"""
        running=True
        while running:
            if self.current_mode is None:
                self.show_menu()
            else:
                # 运行选择的游戏模式，并获取返回值
                quit_to_menu = self.current_mode.run()
                # 如果是正常返回主菜单，重置当前模式和界面
                if quit_to_menu:
                    self.current_mode = None
                    self.clear()
                else:
                    # 如果是退出游戏
                    running = False


if __name__ == "__main__":
    menu = GameMenu()
    menu.run()
# import pygame
# import sys
#
# # 初始化Pygame
# pygame.init()
#
# # 设置屏幕
# SCREEN_WIDTH = 800
# SCREEN_HEIGHT = 600
# screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# pygame.display.set_caption("坦克大战")
#
# # 颜色定义
# BLACK = (0, 0, 0)
# WHITE = (255, 255, 255)
# RED = (255, 0, 0)
#
# # 字体
# font = pygame.font.Font(None, 36)
#
# class Scene:
#     def __init__(self):
#         self.next_scene = self
#
#     def handle_events(self, events):
#         pass
#
#     def update(self):
#         pass
#
#     def render(self, screen):
#         pass
#
# class MainMenuScene(Scene):
#     def __init__(self):
#         super().__init__()
#         self.title = font.render("坦克大战", True, WHITE)
#         self.start_text = font.render("按空格键开始游戏", True, WHITE)
#
#     def handle_events(self, events):
#         for event in events:
#             if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
#                 self.next_scene = LevelSelectScene()
#
#     def render(self, screen):
#         screen.fill(BLACK)
#         screen.blit(self.title, (SCREEN_WIDTH // 2 - self.title.get_width() // 2, 200))
#         screen.blit(self.start_text, (SCREEN_WIDTH // 2 - self.start_text.get_width() // 2, 300))
#
# class LevelSelectScene(Scene):
#     def __init__(self):
#         super().__init__()
#         self.title = font.render("选择关卡", True, WHITE)
#         self.levels = ["无尽模式", "单关模式", "退出游戏"]
#         self.selected = 0
#
#     def handle_events(self, events):
#         for event in events:
#             if event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_UP:
#                     self.selected = (self.selected - 1) % len(self.levels)
#                 elif event.key == pygame.K_DOWN:
#                     self.selected = (self.selected + 1) % len(self.levels)
#                 elif event.key == pygame.K_RETURN:
#                     if self.selected == 2:  # 退出游戏
#                         pygame.quit()
#                         sys.exit()
#                     # 这里可以添加其他模式的跳转逻辑
#                 elif event.key == pygame.K_ESCAPE:
#                     self.next_scene = MainMenuScene()
#
#     def render(self, screen):
#         screen.fill(BLACK)
#         screen.blit(self.title, (SCREEN_WIDTH // 2 - self.title.get_width() // 2, 100))
#         for i, level in enumerate(self.levels):
#             color = RED if i == self.selected else WHITE
#             text = font.render(level, True, color)
#             screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 200 + i * 50))
#
# def main():
#     clock = pygame.time.Clock()
#     current_scene = MainMenuScene()
#
#     while True:
#         events = pygame.event.get()
#         for event in events:
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 sys.exit()
#
#         current_scene.handle_events(events)
#         current_scene.update()
#         current_scene.render(screen)
#
#         if current_scene != current_scene.next_scene:
#             current_scene = current_scene.next_scene
#
#         pygame.display.flip()
#         clock.tick(60)
#
# if __name__ == "__main__":
#     main()