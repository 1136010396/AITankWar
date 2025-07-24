import pygame
import src.config.config as C

# class Button:
#     def __init__(self, x, y, width, height, text, color, text_color):
#         self.rect = pygame.Rect(x, y, width, height)
#         self.text = text
#         self.color = color
#         self.text_color = text_color
#
#     def draw(self, surface):
#         pygame.draw.rect(surface, self.color, self.rect)
#         font = pygame.font.Font(None, 36)
#         text = font.render(self.text, True, self.text_color)
#         text_rect = text.get_rect(center=self.rect.center)
#         surface.blit(text, text_rect)
#
#     def is_clicked(self, pos):
#         return self.rect.collidepoint(pos)
class Button:
    def __init__(self, centerx, centery, width, height, text, text_size=36,
                 bg_color=(50, 50, 50), text_color=(255, 255, 255), hover_color=(70, 70, 70),
                 font_path=None):
        """
        初始化按钮

        Args:
            centerx: 按钮中心x坐标
            centery: 按钮中心y坐标
            width: 按钮宽度
            height: 按钮高度
            text: 按钮文本
            text_size: 文字大小
            bg_color: 按钮背景色
            text_color: 文字颜色
            hover_color: 鼠标悬停时的颜色
        """
        self.width = width
        self.height = height
        self.bg_color = bg_color
        self.text_color = text_color
        self.hover_color = hover_color

        # 创建按钮矩形
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.centerx = centerx
        self.rect.centery = centery

        # 创建文本
        self.font = pygame.font.Font(None, text_size)
        self.text = text
        self.text_surface = self.font.render(text, True, text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

        # 状态
        self.is_hovered = False

        # 使用传入的字体或创建新字体
        if isinstance(font_path, pygame.font.Font):
            self.font = font_path
        else:
            try:
                self.font = pygame.font.Font(font_path, text_size) if font_path else pygame.font.Font(None, text_size)
            except:
                self.font = pygame.font.Font(None, text_size)

    def handle_event(self, event):
        """处理事件"""
        if event.type == pygame.MOUSEMOTION:
            # 检查鼠标是否在按钮上
            self.is_hovered = self.rect.collidepoint(event.pos)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                return True
        return False

    def draw(self, screen):
        """绘制按钮"""
        # 绘制按钮背景
        color = self.hover_color if self.is_hovered else self.bg_color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)

        # 绘制边框
        border_color = (255, 255, 255) if self.is_hovered else (200, 200, 200)
        pygame.draw.rect(screen, border_color, self.rect, width=2, border_radius=10)

        # # 绘制文本
        # screen.blit(self.text_surface, self.text_rect)
        # 渲染文本
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)