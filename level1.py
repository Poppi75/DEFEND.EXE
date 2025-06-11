import pygame
import sys
import time
import math
import json
import os
import subprocess

SETTINGS_FILE = "settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {"invert_colors": False}

def invert_color(color):
    if len(color) == 3:
        return tuple(255 - c for c in color)
    elif len(color) == 4:
        return tuple(255 - c for c in color[:3]) + (color[3],)
    else:
        return color

pygame.init()

info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
VIRTUAL_WIDTH, VIRTUAL_HEIGHT = SCREEN_WIDTH, SCREEN_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
virtual_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

font = pygame.font.SysFont("Arial", 32)
small_font = pygame.font.SysFont("Arial", 20)

towers = []
enemies = []
bullets = []
lives = 3
score = 0

PATH = [(100, 400), (400, 400), (400, 700), (1000, 700), (1000, 100)]

settings = load_settings()
invert = settings.get("invert_colors", False)

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
        self.fire_rate = 30

    def draw(self, surf):
        color = TOWER_TYPES[self.type]["color"]
        color = color if not invert else invert_color(color)
        pygame.draw.rect(surf, color, (self.x - 20, self.y - 20, 40, 40))
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

enemy_spawn_timer = 0
enemy_spawn_interval = 120
selected_tower_type = None

# Pause button in bottom right, bigger
pause_button_size = 100
pause_button_rect = pygame.Rect(
    VIRTUAL_WIDTH - pause_button_size - 40,
    VIRTUAL_HEIGHT - pause_button_size - 40,
    pause_button_size,
    pause_button_size
)
paused = False

def draw_pause_menu(surface):
    overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))

    # Button rects
    resume_rect = pygame.Rect(VIRTUAL_WIDTH//2 - 120, VIRTUAL_HEIGHT//2 - 120, 240, 60)
    settings_rect = pygame.Rect(VIRTUAL_WIDTH//2 - 120, VIRTUAL_HEIGHT//2 - 40, 240, 60)
    restart_rect = pygame.Rect(VIRTUAL_WIDTH//2 - 120, VIRTUAL_HEIGHT//2 + 40, 240, 60)
    mainmenu_rect = pygame.Rect(VIRTUAL_WIDTH//2 - 120, VIRTUAL_HEIGHT//2 + 120, 240, 60)

    # Button colors (invert if needed)
    resume_color = (100, 200, 100) if not invert else invert_color((100, 200, 100))
    settings_color = (100, 100, 255) if not invert else invert_color((100, 100, 255))
    restart_color = (200, 200, 0) if not invert else invert_color((200, 200, 0))
    mainmenu_color = (200, 0, 0) if not invert else invert_color((200, 0, 0))

    # Draw buttons
    pygame.draw.rect(surface, resume_color, resume_rect)
    pygame.draw.rect(surface, settings_color, settings_rect)
    pygame.draw.rect(surface, restart_color, restart_rect)
    pygame.draw.rect(surface, mainmenu_color, mainmenu_rect)

    # Text color (invert if needed)
    text_color = (255, 255, 255) if not invert else (0, 0, 0)

    resume_label = font.render("Resume", True, text_color)
    settings_label = font.render("Settings", True, text_color)
    restart_label = font.render("Restart", True, text_color)
    mainmenu_label = font.render("Main Menu", True, text_color)

    surface.blit(resume_label, resume_label.get_rect(center=resume_rect.center))
    surface.blit(settings_label, settings_label.get_rect(center=settings_rect.center))
    surface.blit(restart_label, restart_label.get_rect(center=restart_rect.center))
    surface.blit(mainmenu_label, mainmenu_label.get_rect(center=mainmenu_rect.center))

    return resume_rect, settings_rect, restart_rect, mainmenu_rect

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

            if not paused and pause_button_rect.collidepoint(vx, vy):
                paused = True

            elif paused:
                resume_rect = pygame.Rect(VIRTUAL_WIDTH//2 - 120, VIRTUAL_HEIGHT//2 - 120, 240, 60)
                settings_rect = pygame.Rect(VIRTUAL_WIDTH//2 - 120, VIRTUAL_HEIGHT//2 - 40, 240, 60)
                restart_rect = pygame.Rect(VIRTUAL_WIDTH//2 - 120, VIRTUAL_HEIGHT//2 + 40, 240, 60)
                mainmenu_rect = pygame.Rect(VIRTUAL_WIDTH//2 - 120, VIRTUAL_HEIGHT//2 + 120, 240, 60)
                if resume_rect.collidepoint(vx, vy):
                    paused = False
                elif settings_rect.collidepoint(vx, vy):
                    subprocess.call([sys.executable, "settings.py"])
                    settings = load_settings()
                    invert = settings.get("invert_colors", False)
                elif restart_rect.collidepoint(vx, vy):
                    subprocess.Popen([sys.executable, "level1.py"])
                    running = False
                elif mainmenu_rect.collidepoint(vx, vy):
                    subprocess.Popen([sys.executable, "Start-Menu.py"])
                    running = False

            if not paused:
                menu_left = VIRTUAL_WIDTH - MENU_WIDTH
                if vx >= menu_left:
                    menu_y = 60
                    for i, ttype in enumerate(TOWER_TYPES):
                        rect = pygame.Rect(menu_left + 10, menu_y + i * 70, 100, 60)
                        if rect.collidepoint(vx, vy):
                            selected_tower_type = i
                elif selected_tower_type is not None:
                    towers.append(Tower(vx, vy, selected_tower_type))
                    selected_tower_type = None

    if not paused:
        enemy_spawn_timer += 1
        if enemy_spawn_timer >= enemy_spawn_interval:
            enemies.append(Enemy(PATH))
            enemy_spawn_timer = 0

        for tower in towers:
            tower.shoot(enemies, bullets)

        for bullet in bullets[:]:
            bullet.update()
            if bullet.target and math.hypot(bullet.x - bullet.target.pos[0], bullet.y - bullet.target.pos[1]) < bullet.radius + 20:
                if bullet.target in enemies:
                    enemies.remove(bullet.target)
                    score += 1
                bullets.remove(bullet)

        for enemy in enemies:
            enemy.update()

    bg_color = (30, 30, 30) if not invert else (225, 225, 225)
    virtual_surface.fill(bg_color)

    path_color = (0, 255, 0) if not invert else invert_color((0, 255, 0))
    pygame.draw.lines(virtual_surface, path_color, False, PATH, 8)

    for tower in towers:
        tower.draw(virtual_surface)
    for enemy in enemies:
        enemy.draw(virtual_surface)
    for bullet in bullets:
        bullet.draw(virtual_surface)

    fg = (255, 255, 255) if not invert else (0, 0, 0)
    text = font.render(f"Lives: {lives}  Score: {score}", True, fg)
    virtual_surface.blit(text, (10, 10))
    small = small_font.render("ESC to quit, click to place towers", True, fg)
    virtual_surface.blit(small, (10, 50))

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

    # Draw pause button (bottom right, bigger, thick bars)
    pygame.draw.rect(
        virtual_surface,
        (180, 180, 180) if not invert else invert_color((180, 180, 180)),
        pause_button_rect,
        border_radius=20
    )
    bar_width = 18
    bar_height = 60
    bar_gap = 24
    bar_color = (60, 60, 60) if not invert else invert_color((60, 60, 60))
    x1 = pause_button_rect.x + pause_button_rect.width // 2 - bar_gap // 2 - bar_width
    x2 = pause_button_rect.x + pause_button_rect.width // 2 + bar_gap // 2
    y = pause_button_rect.y + (pause_button_rect.height - bar_height) // 2
    pygame.draw.rect(virtual_surface, bar_color, (x1, y, bar_width, bar_height), border_radius=8)
    pygame.draw.rect(virtual_surface, bar_color, (x2, y, bar_width, bar_height), border_radius=8)

    if paused:
        draw_pause_menu(virtual_surface)

    scaled = pygame.transform.scale(virtual_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled, (0, 0))
    pygame.display.flip()

pygame.quit()
sys.exit()
