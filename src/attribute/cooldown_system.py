import pygame
# from src.config.config import COOLDOWN_CONFIG


class CooldownSystem:
    def __init__(self, tank):
        self.tank = tank
        self.last_shot_time = 0
        self.update_cooldown_time()

    def update_cooldown_time(self):
        """更新冷却时间"""
        # 根据坦克等级设置冷却时间
        self.cooldown_time = {
            1: 1000,  # 1级坦克冷却1秒
            2: 800,  # 2级坦克冷却0.8秒
            3: 600,  # 3级坦克冷却0.6秒
            666: 10  # 666给自己开的挂
        }.get(self.tank.level, 1000)

    def can_shoot(self):
        """检查是否可以射击"""
        current_time = pygame.time.get_ticks()
        return current_time - self.last_shot_time >= self.cooldown_time

    def start_cooldown(self):
        """开始冷却"""
        self.last_shot_time = pygame.time.get_ticks()

    def get_cooldown_progress(self):
        """获取冷却进度（0-1）"""
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.last_shot_time
        return min(1.0, elapsed / self.cooldown_time)

    def draw(self, screen):
        """绘制冷却指示器"""
        progress = self.get_cooldown_progress()

        # 只在冷却中时显示指示器
        if progress < 1.0:
            # 设置指示器位置（坦克上方）
            indicator_width = 30
            indicator_height = 4
            x = self.tank.rect.centerx - indicator_width // 2
            y = self.tank.rect.top - 8

            # 绘制背景条
            pygame.draw.rect(screen, (100, 100, 100),
                             (x, y, indicator_width, indicator_height))

            # 绘制进度条
            progress_width = int(indicator_width * progress)
            if self.tank.is_player:
                color = (0, 255, 0)  # 玩家坦克使用绿色
            else:
                color = (255, 0, 0)  # 敌方坦克使用红色

            pygame.draw.rect(screen, color,
                             (x, y, progress_width, indicator_height))