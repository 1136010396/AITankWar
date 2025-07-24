import pygame
import random
import math

# 初始化Pygame
pygame.init()

# 设置游戏窗口
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("坦克大战")

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


# 坦克类
class Tank(pygame.sprite.Sprite):
    def __init__(self, x, y, color, is_player=False):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 3
        self.is_player = is_player
        self.direction = 0  # 0: 上, 1: 右, 2: 下, 3: 左

    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        self.rect.clamp_ip(screen.get_rect())

    def rotate(self, direction):
        self.direction = direction

    def shoot(self):
        if self.direction == 0:
            return Bullet(self.rect.centerx, self.rect.top, 0, -1,self.is_player)
        elif self.direction == 1:
            return Bullet(self.rect.right, self.rect.centery, 1, 0,self.is_player)
        elif self.direction == 2:
            return Bullet(self.rect.centerx, self.rect.bottom, 0, 1,self.is_player)
        else:
            return Bullet(self.rect.left, self.rect.centery, -1, 0,self.is_player)


# 子弹类
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, is_player_bullet):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = 5
        self.dx = dx
        self.dy = dy
        self.is_player_bullet = is_player_bullet

    def update(self):
        self.rect.x += self.dx * self.speed
        self.rect.y += self.dy * self.speed
        if not screen.get_rect().contains(self.rect):
            self.kill()


# 大本营类
class Base(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((60, 60))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# 游戏类
class Game:
    def __init__(self):
        self.player = Tank(WIDTH // 2, HEIGHT - 50, GREEN, True)
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.base = Base(WIDTH // 2 - 30, HEIGHT - 70)
        self.all_sprites = pygame.sprite.Group(self.player, self.base)
        self.clock = pygame.time.Clock()
        self.enemy_spawn_timer = 0
        self.score = 0
        self.game_over = False

    def spawn_enemy(self):
        x = random.randint(0, WIDTH - 40)
        y = random.randint(0, HEIGHT // 2)
        enemy = Tank(x, y, RED)
        self.enemies.add(enemy)
        self.all_sprites.add(enemy)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and not self.game_over:
                if event.key == pygame.K_SPACE:
                    bullet = self.player.shoot()
                    self.bullets.add(bullet)
                    self.all_sprites.add(bullet)

        if not self.game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.player.move(-1, 0)
                self.player.rotate(3)
            if keys[pygame.K_RIGHT]:
                self.player.move(1, 0)
                self.player.rotate(1)
            if keys[pygame.K_UP]:
                self.player.move(0, -1)
                self.player.rotate(0)
            if keys[pygame.K_DOWN]:
                self.player.move(0, 1)
                self.player.rotate(2)

        return True

    def update(self):
        self.all_sprites.update()

        # 敌人AI行为
        for enemy in self.enemies:
            if random.random() < 0.01:
                bullet = enemy.shoot()
                self.bullets.add(bullet)
                self.all_sprites.add(bullet)

            dx = self.base.rect.centerx - enemy.rect.centerx
            dy = self.base.rect.centery - enemy.rect.centery
            dist = math.hypot(dx, dy)
            if dist != 0:
                dx, dy = dx / dist, dy / dist
            enemy.move(dx, dy)

        # 碰撞检测
        for bullet in self.bullets:
            if bullet.is_player_bullet:
                # 玩家子弹只能伤害敌人
                hit_enemies = pygame.sprite.spritecollide(bullet, self.enemies, True)
                if hit_enemies:
                    bullet.kill()
                    self.score += len(hit_enemies)
            else:
                # 敌人子弹可以伤害玩家和大本营
                if pygame.sprite.collide_rect(bullet, self.player):
                    self.game_over = True
                    bullet.kill()
                elif pygame.sprite.collide_rect(bullet, self.base):
                    self.game_over = True
                    bullet.kill()

        # 生成新的敌人
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer >= 120:  # 每2秒生成一个敌人
            self.spawn_enemy()
            self.enemy_spawn_timer = 0

    def draw(self):
        screen.fill(WHITE)
        self.all_sprites.draw(screen)

        # 显示分数
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        if self.game_over:
            font = pygame.font.Font(None, 72)
            game_over_text = font.render("Game Over", True, RED)
            screen.blit(game_over_text, (WIDTH // 2 - 100, HEIGHT // 2 - 36))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            if not self.game_over:
                self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()


# 运行游戏
if __name__ == "__main__":
    game = Game()
    game.run()