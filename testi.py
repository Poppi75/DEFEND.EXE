import pygame
import sys
import json
import os

SETTINGS_FILE = "settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {"invert_colors": False}

def invert_color(color):
    return tuple(255 - c for c in color[:3])

pygame.init()

VIRTUAL_WIDTH, VIRTUAL_HEIGHT = 800, 480  # Swapped for landscape
info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Simple Tower Defense (Landscape)")
virtual_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

settings = load_settings()
invert = settings.get("invert_colors", False)

# Enemy path (adjusted for landscape)
PATH = [(0, 240), (200, 240), (200, 50), (600, 50), (600, 430), (800, 430)]

class Enemy:
    def __init__(self):
        self.pos = list(PATH[0])
        self.path_index = 0
        self.speed = 2
        self.radius = 15

    def move(self):
        if self.path_index < len(PATH) - 1:
            target = PATH[self.path_index + 1]
            dx, dy = target[0] - self.pos[0], target[1] - self.pos[1]
            dist = (dx ** 2 + dy ** 2) ** 0.5
            if dist < self.speed:
                self.pos = list(target)
                self.path_index += 1
            else:
                self.pos[0] += self.speed * dx / dist
                self.pos[1] += self.speed * dy / dist

    def draw(self, surf):
        color = (200, 0, 0) if not invert else invert_color((200, 0, 0))
        pygame.draw.circle(surf, color, (int(self.pos[0]), int(self.pos[1])), self.radius)

    def reached_end(self):
        return self.path_index == len(PATH) - 1

class Tower:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.range = 120
        self.cooldown = 0

    def draw(self, surf):
        color = (0, 0, 200) if not invert else invert_color((0, 0, 200))
        pygame.draw.rect(surf, color, (self.x - 20, self.y - 20, 40, 40))
        # Draw range
        pygame.draw.circle(surf, (100, 100, 255) if not invert else invert_color((100, 100, 255)), (self.x, self.y), self.range, 1)

    def can_shoot(self):
        return self.cooldown == 0

    def shoot(self, enemy):
        self.cooldown = 30
        return Bullet(self.x, self.y, enemy)

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1

class Bullet:
    def __init__(self, x, y, enemy):
        self.x, self.y = x, y
        self.target = enemy
        self.speed = 8
        self.radius = 6

    def move(self):
        dx, dy = self.target.pos[0] - self.x, self.target.pos[1] - self.y
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist < self.speed or dist == 0:
            self.x, self.y = self.target.pos[0], self.target.pos[1]
        else:
            self.x += self.speed * dx / dist
            self.y += self.speed * dy / dist

    def draw(self, surf):
        color = (255, 255, 0) if not invert else invert_color((255, 255, 0))
        pygame.draw.circle(surf, color, (int(self.x), int(self.y)), self.radius)

    def hit(self):
        dx, dy = self.target.pos[0] - self.x, self.target.pos[1] - self.y
        return (dx ** 2 + dy ** 2) ** 0.5 < self.radius + self.target.radius

enemies = []
bullets = []
towers = []
spawn_timer = 0
lives = 5
score = 0

font = pygame.font.SysFont(None, 40)
small_font = pygame.font.SysFont(None, 30)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            # Convert to virtual coordinates
            vx = int(mx * VIRTUAL_WIDTH / SCREEN_WIDTH)
            vy = int(my * VIRTUAL_HEIGHT / SCREEN_HEIGHT)
            towers.append(Tower(vx, vy))

    # Game logic
    spawn_timer += 1
    if spawn_timer > 60:
        enemies.append(Enemy())
        spawn_timer = 0

    for enemy in enemies[:]:
        enemy.move()
        if enemy.reached_end():
            enemies.remove(enemy)
            lives -= 1
            if lives <= 0:
                running = False

    for tower in towers:
        tower.update()
        for enemy in enemies:
            dx, dy = enemy.pos[0] - tower.x, enemy.pos[1] - tower.y
            if dx ** 2 + dy ** 2 < tower.range ** 2 and tower.can_shoot():
                bullets.append(tower.shoot(enemy))
                break

    for bullet in bullets[:]:
        bullet.move()
        if bullet.hit():
            if bullet.target in enemies:
                enemies.remove(bullet.target)
                score += 1
            bullets.remove(bullet)

    # Drawing
    bg_color = (30, 30, 30) if not invert else (225, 225, 225)
    virtual_surface.fill(bg_color)

    # Draw path
    path_color = (0, 255, 0) if not invert else invert_color((0, 255, 0))
    pygame.draw.lines(virtual_surface, path_color, False, PATH, 8)

    for tower in towers:
        tower.draw(virtual_surface)
    for enemy in enemies:
        enemy.draw(virtual_surface)
    for bullet in bullets:
        bullet.draw(virtual_surface)

    # HUD
    fg = (255, 255, 255) if not invert else (0, 0, 0)
    text = font.render(f"Lives: {lives}  Score: {score}", True, fg)
    virtual_surface.blit(text, (10, 10))
    small = small_font.render("ESC to quit, click to place towers", True, fg)
    virtual_surface.blit(small, (10, 50))

    # Scale to screen
    scaled = pygame.transform.scale(virtual_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled, (0, 0))
    pygame.display.flip()

pygame.quit()
sys.exit()
