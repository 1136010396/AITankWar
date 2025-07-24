import math
import random
import pygame
import src.config.config as C
from src.entry.tank import Tank
from src.entry.base import Base
from src.entry.Button import Button
from src.control.image_manager import ImageManager
from src.control.collision_manager import CollisionManager
from src.control.map_manager import MapManager
from src.control.enemy_manager import EnemyManager
from src.data.maps.map_data import CLASSIC_MAP,RIVER_MAP

# 游戏无尽模式
class InfiniteGame:
    def __init__(self):
        self.minStep=3
        self.maxStep=7
        self.width=len(CLASSIC_MAP)*C.LITTLE_BLOCK[0]+C.MAP_OFFSET*2
        self.height=len(CLASSIC_MAP[0])*C.LITTLE_BLOCK[0]+C.MAP_OFFSET*2

        # button
        # self.restart_button = Button(self.width//2, self.height//2, 200, 50, "rePlay", (0, 255, 0), (0, 0, 0))

        self.init()

    def init(self):
        # 初始化Pygame
        pygame.init()
        # 设置游戏窗口
        self.screen = pygame.display.set_mode((self.width,self.height))
        pygame.display.set_caption("坦克大战")

        # manager
        self.image_manager = ImageManager()
        self.map_manager = MapManager(self.image_manager)
        # 先暂时写死测试地图
        self.map_manager.load_map(RIVER_MAP)

        self.collision_manager = CollisionManager()
        # 创建敌人管理器
        self.enemy_manager = EnemyManager(self)

        # 按钮项
        self.restart_button = Button(
            centerx=self.screen.get_rect().centerx,  # 屏幕中心x坐标
            centery=self.screen.get_rect().centery,  # 屏幕中心y坐标
            width=200,  # 按钮宽度
            height=50,  # 按钮高度
            text="RePlay",
            text_size=36,
            bg_color=(50, 50, 50),  # 按钮背景色
            text_color=(255, 255, 255),  # 文字颜色
            hover_color=(70, 70, 70)  # 鼠标悬停时的颜色
        )
        # self.map_manager.load_map(CLASSIC_MAP)

        # 规划位置 先写死判断，后通过检测固定初始位置。
        # self.player = Tank(C.LITTLE_BLOCK[0]*14 , C.LITTLE_BLOCK[0]*22, self.image_manager.images, True)
        self.player = Tank(self.map_manager.player[0]+C.MAP_OFFSET , self.map_manager.player[1]+C.MAP_OFFSET, self.image_manager.images, True)
        self.player.level=666
        self.player.bulletLevel=1
        self.player.cooldown_system.update_cooldown_time()

        # self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        # self.base = Base(C.LITTLE_BLOCK[0]*11, C.LITTLE_BLOCK[1]*22, self.image_manager.images)
        self.base = Base(self.map_manager.base[0]+C.MAP_OFFSET, self.map_manager.base[1]+C.MAP_OFFSET, self.image_manager.images)
        self.all_sprites = pygame.sprite.Group(self.player, self.base)

        self.clock = pygame.time.Clock()
        self.enemy_spawn_timer = 0
        self.score = 0
        self.game_over = False
        self.enemy_move_states = {}



        # 添加暂停状态和暂停菜单
        self.paused = False
        self.quit_to_menu = False

        # 创建暂停菜单按钮
        self.pause_buttons = [
            Button(
                centerx=self.width // 2,
                centery=self.height // 2 - 60,
                width=200,
                height=50,
                text="Continue",
                text_size=36,
                bg_color=(50, 50, 50),
                text_color=(255, 255, 255),
                hover_color=(70, 70, 70)
            ),
            Button(
                centerx=self.width // 2,
                centery=self.height // 2,
                width=200,
                height=50,
                text="BackToMenu",
                text_size=36,
                bg_color=(50, 50, 50),
                text_color=(255, 255, 255),
                hover_color=(70, 70, 70)
            )
        ]

        # 添加子弹等级显示
        self.bullet_level_font = pygame.font.Font(None, 30)
        self.bullet_level_text = self.bullet_level_font.render(f"Bullet Level: {self.player.bulletLevel}", True,
                                                               C.WHITE)
        self.bullet_level_rect = self.bullet_level_text.get_rect(topleft=(10, 50))


    # def spawn_enemy(self):
    #     x = random.randint(0, C.SCREEN_WIDTH - 40)
    #     y = random.randint(0, C.SCREEN_HEIGHT // 2)
    #     enemy = Tank(x, y, self.image_manager.images, False)
    #     enemy.speed = 2
    #     self.enemies.add(enemy)
    #     self.all_sprites.add(enemy)

    def get_collision_groups(self, exclude_sprite=None):
        """
        获取碰撞检测组，可以排除指定的精灵

        Args:
            exclude_sprite: 要排除的精灵对象

        Returns:
            dict: 碰撞组字典
        """
        player = pygame.sprite.Group(self.player)
        enemies = self.enemy_manager.enemies
        if exclude_sprite in self.enemy_manager.enemies:
            # 如果是敌人，返回不包含自己的敌人组
            enemies = pygame.sprite.Group([e for e in self.enemy_manager.enemies if e != exclude_sprite])
        elif exclude_sprite == self.player:
            # 如果是玩家，只返回敌人和基地组
            player=None

        # 默认返回所有组
        return {
            'enemies': enemies,
            'base': pygame.sprite.Group(self.base),
            'player': player,
        }

    def upgrade_bullet(self):
        if self.player.bulletLevel < 3:  # 假设最高等级为3
            self.player.bulletLevel += 1
            self.update_bullet_level_text()

    def update_bullet_level_text(self):
        self.bullet_level_text = self.bullet_level_font.render(f"Bullet Level: {self.player.bulletLevel}", True,
                                                               C.WHITE)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # ESC键切换暂停状态
                    self.paused = not self.paused

            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.game_over and self.restart_button.is_clicked(event.pos):
                    self.init()
                    return True

            if self.paused:
                # 处理暂停菜单的鼠标点击
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    for i, button in enumerate(self.pause_buttons):
                        if button.is_clicked(mouse_pos):
                            if i == 0:  # 继续游戏
                                self.paused = False
                            elif i == 1:  # 返回主菜单
                                self.quit_to_menu = True
                                return False
            elif event.type == pygame.KEYDOWN and not self.game_over:
                print(f"Key pressed: {pygame.key.name(event.key)}")  # 调试信息qq
                if event.key == pygame.K_SPACE:
                    bullet = self.player.shoot(self.image_manager.images)
                    if bullet is not None:
                        self.bullets.add(bullet)
                        self.all_sprites.add(bullet)

                if event.key == pygame.K_q:
                    print("Q key pressed, upgrading bullet")  # 调试信息
                    self.upgrade_bullet()

        if not self.game_over and not self.paused:
            keys = pygame.key.get_pressed()
            collision_groups = self.get_collision_groups(self.player)

            if keys[pygame.K_LEFT]:
                self.player.move(self,-1, 0, self.screen, collision_groups)
                self.player.rotate(C.LEFT)
            if keys[pygame.K_RIGHT]:
                self.player.move(self,1, 0, self.screen, collision_groups)
                self.player.rotate(C.RIGHT)
            if keys[pygame.K_UP]:
                self.player.move(self,0, -1, self.screen, collision_groups)
                self.player.rotate(C.UP)
            if keys[pygame.K_DOWN]:
                self.player.move(self,0, 1, self.screen, collision_groups)
                self.player.rotate(C.DOWN)

        return True

    def enemy_move(self):
        # 敌人AI行为 大致朝基地移动
        for enemy in self.enemy_manager.enemies:
            # 初始化敌人移动状态
            if enemy not in self.enemy_move_states:
                self.enemy_move_states[enemy] = {
                    'direction': C.DOWN,  # 初始向上移动
                    'steps_remaining': random.randint(self.minStep, self.maxStep)  # 移动1-3步后重新选择方向
                }

            if random.random() < 0.01:
                bullet = enemy.shoot(self.image_manager.images)
                self.bullets.add(bullet)
                self.all_sprites.add(bullet)

            # 获取当前移动状态
            move_state = self.enemy_move_states[enemy]

            # 检查是否需要更新移动方向
            if move_state['steps_remaining'] <= 0:
                dx = self.base.rect.centerx - enemy.rect.centerx
                dy = self.base.rect.centery - enemy.rect.centery
                dist = math.hypot(dx, dy)
                if dist != 0:
                    dx, dy = dx / dist, dy / dist
                # 确保移动方向是整数且只有一个方向
                if abs(dx) > abs(dy):
                    dy = 0
                    dx = 1 if dx > 0 else -1 if dx < 0 else 0
                else:
                    dx = 0
                    dy = 1 if dy > 0 else -1 if dy < 0 else 0
                # 更新移动状态
                move_state['direction'] = C.vector_to_direction(dx, dy)
                move_state['steps_remaining'] = random.randint(self.minStep, self.maxStep)
            else:
                move_state['steps_remaining'] -= 1

            collision_groups = self.get_collision_groups(enemy)

            dx, dy = C.direction_to_vector(move_state['direction'])
            enemy.move(self,dx, dy, self.screen,collision_groups)
            enemy.rotate(C.vector_to_direction(dx, dy))

    def handle_bullet_collisions(self):
        # 子弹碰撞检测
        """处理子弹碰撞"""
        for bullet in self.bullets:
            # 检查与地形的碰撞
            for terrain_type, group in self.map_manager.terrain_groups.items():
                for terrain in group:
                    if bullet.rect.colliderect(terrain.rect):
                        if not terrain.can_pass_bullet():
                            if terrain.can_be_destroyed_by(bullet):
                                terrain.kill()
                            bullet.kill()
                            break
            if bullet.is_player_bullet:
                # 玩家子弹检测
                # 1. 与敌人的碰撞
                for enemy in self.enemy_manager.enemies:
                    if self.collision_manager.check_collision(bullet, enemy):
                        enemy.kill()
                        if not bullet.strong:  # 非强力子弹碰撞后消失
                            bullet.kill()
                        self.score += 1
                        break

                # 2. 与敌人子弹的碰撞
                for enemy_bullet in [b for b in self.bullets if not b.is_player_bullet]:
                    if self.collision_manager.check_collision(bullet, enemy_bullet):
                        enemy_bullet.kill()
                        if not bullet.strong:
                            bullet.kill()
                        break
            else:
                # 敌人子弹检测
                # 1. 与玩家的碰撞
                if self.collision_manager.check_collision(bullet, self.player):
                    self.player.life -= 1
                    bullet.kill()
                    if self.player.life <= 0:
                        self.game_over = True

                # 2. 与基地的碰撞
                elif self.collision_manager.check_collision(bullet, self.base):
                    self.game_over = True
                    bullet.kill()

                # 3. 与玩家子弹的碰撞
                for player_bullet in [b for b in self.bullets if b.is_player_bullet]:
                    if self.collision_manager.check_collision(bullet, player_bullet):
                        bullet.kill()
                        if not player_bullet.strong:
                            player_bullet.kill()
                        break


    def collision(self):
        self.handle_bullet_collisions()
        # for bullet in self.bullets:
        #     # 检查与地形的碰撞
        #     for brick in self.map_manager.brick_group:
        #         if self.collision_manager.check_collision(bullet, brick):
        #             if brick.hit(bullet):  # 如果地形可以被摧毁
        #                 brick.kill()
        #             if not bullet.strong:  # 如果不是强力子弹
        #                 bullet.kill()
        #             break
        #
        #     for iron in self.map_manager.iron_group:
        #         if self.collision_manager.check_collision(bullet, iron):
        #             if iron.hit(bullet):  # 只有强力子弹才能摧毁铁块
        #                 iron.kill()
        #             bullet.kill()  # 无论是否摧毁铁块，子弹都会消失
        #             break
        #     if bullet.is_player_bullet:
        #         # 玩家子弹检测
        #         # 1. 与敌人的碰撞
        #         for enemy in self.enemy_manager.enemies:
        #             if self.collision_manager.check_collision(bullet, enemy):
        #                 enemy.kill()
        #                 if not bullet.strong:  # 非强力子弹碰撞后消失
        #                     bullet.kill()
        #                 self.score += 1
        #                 break
        #
        #         # 2. 与敌人子弹的碰撞
        #         for enemy_bullet in [b for b in self.bullets if not b.is_player_bullet]:
        #             if self.collision_manager.check_collision(bullet, enemy_bullet):
        #                 enemy_bullet.kill()
        #                 if not bullet.strong:
        #                     bullet.kill()
        #                 break
        #     else:
        #         # 敌人子弹检测
        #         # 1. 与玩家的碰撞
        #         if self.collision_manager.check_collision(bullet, self.player):
        #             self.player.life -= 1
        #             bullet.kill()
        #             if self.player.life <= 0:
        #                 self.game_over = True
        #
        #         # 2. 与基地的碰撞
        #         elif self.collision_manager.check_collision(bullet, self.base):
        #             self.game_over = True
        #             bullet.kill()
        #
        #         # 3. 与玩家子弹的碰撞
        #         for player_bullet in [b for b in self.bullets if b.is_player_bullet]:
        #             if self.collision_manager.check_collision(bullet, player_bullet):
        #                 bullet.kill()
        #                 if not player_bullet.strong:
        #                     player_bullet.kill()
        #                 break

        # # 坦克之间的碰撞检测
        # # 1. 敌人坦克之间
        # for enemy1 in self.enemies:
        #     # 与其他敌人
        #     for enemy2 in self.enemies:
        #         if enemy1 != enemy2 and self.collision_manager.check_collision(enemy1, enemy2):
        #             # 发生碰撞时，让坦克稍微分开
        #             self.resolve_tank_collision(enemy1, enemy2)
        #
        #     # 与玩家
        #     if self.collision_manager.check_collision(enemy1, self.player):
        #         self.resolve_tank_collision(enemy1, self.player)
        #
        #     # 与基地
        #     if self.collision_manager.check_collision(enemy1, self.base):
        #         self.resolve_tank_collision(enemy1, self.base)
        #
        # # 2. 玩家与基地的碰撞
        # if self.collision_manager.check_collision(self.player, self.base):
        #     self.resolve_tank_collision(self.player, self.base)

    # def resolve_tank_collision(self, sprite1, sprite2):
    #     """处理两个精灵之间的碰撞"""
    #     # 由于上述检查只有在sprite2才有可能是基地
    #     if isinstance(sprite2, Base):
    #         # 计算从基地到坦克的方向
    #         dx = sprite1.rect.centerx - sprite2.rect.centerx
    #         dy = sprite1.rect.centery - sprite2.rect.centery
    #
    #         # 标准化向量
    #         distance = max(1, (dx * dx + dy * dy) ** 0.5)
    #         dx = dx / distance
    #         dy = dy / distance
    #
    #         # 只将坦克推开
    #         push_distance = 2
    #         sprite1.rect.x += dx * push_distance
    #         sprite1.rect.y += dy * push_distance
    #         return
    #
    #     # 两个坦克之间的碰撞
    #     dx = sprite1.rect.centerx - sprite2.rect.centerx
    #     dy = sprite1.rect.centery - sprite2.rect.centery
    #
    #     # 标准化向量
    #     distance = max(1, (dx * dx + dy * dy) ** 0.5)
    #     dx = dx / distance
    #     dy = dy / distance
    #
    #     # 将两个坦克稍微推开
    #     push_distance = 1
    #     sprite1.rect.x += dx * push_distance
    #     sprite1.rect.y += dy * push_distance
    #     sprite2.rect.x -= dx * push_distance
    #     sprite2.rect.y -= dy * push_distance


    def update(self):
        self.all_sprites.update()

        # 敌方ai移动
        # self.enemy_move()
        self.enemy_manager.update()

        # 子弹碰撞检测
        # 这里可以优化为并行计算来辅助判断。
        self.collision()

        # if self.check_game_over_condition():
        #     self.is_game_over = True

        # # 放到enemy功能里面了
        # self.enemy_spawn_timer += 1
        # if self.enemy_spawn_timer >= 120:  # 每2秒生成一个敌人
        #     self.spawn_enemy()
        #     self.enemy_spawn_timer = 0

    def draw(self):
        self.screen.fill(C.BLACK)
        self.map_manager.draw(self.screen)
        self.all_sprites.draw(self.screen)

        # 显示分数
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, C.RED)
        self.screen.blit(score_text, (10, 10))

        # 显示子弹等级
        self.screen.blit(self.bullet_level_text, self.bullet_level_rect)

        pygame.display.flip()

    def cleanup(self):
        # """清理游戏资源"""
        # # 停止所有音效
        # pygame.mixer.stop()

        # 清理精灵组
        self.all_sprites.empty()
        self.bullets.empty()
        if hasattr(self, 'enemy_manager'):
            self.enemy_manager.enemies.empty()

        # 重置游戏状态
        self.game_over = False
        self.paused = False

    def draw_pause_menu(self):
        """绘制暂停菜单"""
        # 创建半透明遮罩
        overlay = pygame.Surface((self.width, self.height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))

        # 绘制暂停菜单标题
        title_font = pygame.font.Font(None, 74)
        title_text = title_font.render("Pause", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.width // 2, self.height // 2 - 120))
        self.screen.blit(title_text, title_rect)

        # 绘制按钮
        for button in self.pause_buttons:
            button.draw(self.screen)

    def draw_game_over(self):
        self.screen.fill((0, 0, 0))  # 填充黑色背景
        game_over_image = self.image_manager.get_image('gameOver')
        if game_over_image:
            # 获取屏幕中心位置
            screen_center_x = self.width // 2
            screen_center_y = self.height // 3
            image_rect = game_over_image.get_rect()
            image_rect.center = (screen_center_x, screen_center_y)
            self.screen.blit(game_over_image, image_rect)

        self.restart_button.draw(self.screen)
        pygame.display.flip()

    # def run(self):
    #     running = True
    #     while running:
    #         running = self.handle_events()
    #         if running:
    #             if not self.game_over:
    #                 self.update()
    #                 self.draw()
    #             else:
    #                 self.draw_game_over()
    #             self.clock.tick(60)
    #     pygame.quit()

    def run(self):
        """运行游戏"""
        running = True
        while running:
            running = self.handle_events()

            if not self.game_over:
                if not self.paused:
                    self.update()
                    self.draw()
                else:
                    # 在游戏画面上绘制暂停菜单
                    self.draw_pause_menu()
            else:
                self.draw_game_over()

            pygame.display.flip()
            self.clock.tick(60)

        # 在退出前清理资源
        self.cleanup()
        return self.quit_to_menu



# 运行游戏
if __name__ == "__main__":
    game = InfiniteGame()
    # 如果要切换到其他地图
    # game.map_manager.load_map(ANOTHER_MAP)
    game.run()