import pygame
import sys
import time
import math

# Initialize pygame and fonts
pygame.init()

# Screen and virtual surface settings
info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
VIRTUAL_WIDTH, VIRTUAL_HEIGHT = SCREEN_WIDTH, SCREEN_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
virtual_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

# Fonts
font = pygame.font.SysFont("Arial", 32)
small_font = pygame.font.SysFont("Arial", 20)

# Game state variables
towers = []
enemies = []
bullets = []
lives = 3
score = 0

# Path for enemies (example path)
PATH = [(100, 400), (400, 400), (400, 700), (1000, 700), (1000, 100)]

# Invert mode and color function
invert = False
def invert_color(color):
    return tuple(255 - c for c in color)

MENU_WIDTH = 120
MENU_BG = (50, 50, 80)
TOWER_TYPES = [
    {"name": "Blue", "color": (0, 0, 200), "range": 120},
    {"name": "Red", "color": (200, 0, 0), "range": 80},
    {"name": "Green", "color": (0, 180, 0), "range": 160},
    {"name": "Yellow", "color": (200, 200, 0), "range": 100},
]

class Tower:
    def __init__(self, x, y, ttype=0):
        self.x, self.y = x, y
        self.type = ttype
        self.range = TOWER_TYPES[ttype]["range"]
        self.cooldown = 0
        self.fire_rate = 30  # frames between shots

    def draw(self, surf):
        color = TOWER_TYPES[self.type]["color"]
        color = color if not invert else invert_color(color)
        pygame.draw.rect(surf, color, (self.x - 20, self.y - 20, 40, 40))
        # Draw range
        pygame.draw.circle(
            surf,
            (100, 100, 255) if not invert else invert_color((100, 100, 255)),
            (self.x, self.y),
            self.range,
            1,
        )

    def shoot(self, enemies, bullets):
        if self.cooldown > 0:
            self.cooldown -= 1
            return
        # Find the first enemy in range
        for enemy in enemies:
            dx = enemy.pos[0] - self.x
            dy = enemy.pos[1] - self.y
            dist = math.hypot(dx, dy)
            if dist <= self.range:
                bullets.append(Bullet(self.x, self.y, enemy))
                self.cooldown = self.fire_rate
                break

class Enemy:
    def __init__(self, path):
        self.path = path
        self.pos = list(path[0])
        self.path_index = 0
        self.speed = 2

    def update(self):
        if self.path_index < len(self.path) - 1:
            target = self.path[self.path_index + 1]
            dx, dy = target[0] - self.pos[0], target[1] - self.pos[1]
            dist = (dx**2 + dy**2) ** 0.5
            if dist < self.speed:
                self.pos = list(target)
                self.path_index += 1
            else:
                self.pos[0] += self.speed * dx / dist
                self.pos[1] += self.speed * dy / dist

    def draw(self, surf):
        color = (255, 0, 0) if not invert else invert_color((255, 0, 0))
        pygame.draw.circle(surf, color, (int(self.pos[0]), int(self.pos[1])), 20)

class Bullet:
    def __init__(self, x, y, target):
        self.x = x
        self.y = y
        self.target = target
        self.speed = 8
        self.radius = 8

    def update(self):
        if not self.target:
            return
        dx = self.target.pos[0] - self.x
        dy = self.target.pos[1] - self.y
        dist = math.hypot(dx, dy)
        if dist < self.speed or dist == 0:
            self.x, self.y = self.target.pos[0], self.target.pos[1]
        else:
            self.x += self.speed * dx / dist
            self.y += self.speed * dy / dist

    def draw(self, surf):
        color = (255, 255, 0) if not invert else invert_color((255, 255, 0))
        pygame.draw.circle(surf, color, (int(self.x), int(self.y)), self.radius)

# Add these variables before the game loop
enemy_spawn_timer = 0
enemy_spawn_interval = 120  # frames (2 seconds at 60 FPS)

selected_tower_type = None

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            vx = int(mx * VIRTUAL_WIDTH / SCREEN_WIDTH)
            vy = int(my * VIRTUAL_HEIGHT / SCREEN_HEIGHT)
            # Check if click is in menu area (right side)
            menu_left = VIRTUAL_WIDTH - MENU_WIDTH
            if vx >= menu_left:
                # Which tower type?
                menu_y = 60
                for i, ttype in enumerate(TOWER_TYPES):
                    rect = pygame.Rect(menu_left + 10, menu_y + i * 70, 100, 60)
                    if rect.collidepoint(vx, vy):
                        selected_tower_type = i
            elif selected_tower_type is not None:
                towers.append(Tower(vx, vy, selected_tower_type))
                selected_tower_type = None

    # Spawn enemies
    enemy_spawn_timer += 1
    if enemy_spawn_timer >= enemy_spawn_interval:
        enemies.append(Enemy(PATH))
        enemy_spawn_timer = 0

    # Towers shoot at enemies
    for tower in towers:
        tower.shoot(enemies, bullets)

    # Update bullets
    for bullet in bullets[:]:
        bullet.update()
        # Remove bullet if it hits the target
        if bullet.target and math.hypot(bullet.x - bullet.target.pos[0], bullet.y - bullet.target.pos[1]) < bullet.radius + 20:
            if bullet.target in enemies:
                enemies.remove(bullet.target)
                score += 1
            bullets.remove(bullet)

    # Update enemies
    for enemy in enemies:
        enemy.update()

    # Drawing
    bg_color = (30, 30, 30) if not invert else (225, 225, 225)
    virtual_surface.fill(bg_color)

    # Draw path
    path_color = (0, 255, 0) if not invert else invert_color((0, 255, 0))
    pygame.draw.lines(virtual_surface, path_color, False, PATH, 8)

    # Draw towers, enemies, bullets
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

    # Draw right-side menu
    menu_left = VIRTUAL_WIDTH - MENU_WIDTH
    pygame.draw.rect(virtual_surface, MENU_BG, (menu_left, 0, MENU_WIDTH, VIRTUAL_HEIGHT))
    menu_y = 60
    for i, ttype in enumerate(TOWER_TYPES):
        rect = pygame.Rect(menu_left + 10, menu_y + i * 70, 100, 60)
        color = ttype["color"] if not invert else invert_color(ttype["color"])
        pygame.draw.rect(virtual_surface, color, rect)
        if selected_tower_type == i:
            pygame.draw.rect(virtual_surface, (255, 255, 255), rect, 3)
        label = small_font.render(ttype["name"], True, fg)
        virtual_surface.blit(label, (menu_left + 20, menu_y + i * 70 + 15))

    # Scale to screen
    scaled = pygame.transform.scale(virtual_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled, (0, 0))
    pygame.display.flip()

pygame.quit()
sys.exit()
