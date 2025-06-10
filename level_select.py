import pygame
import sys
import os
import subprocess
import json

SETTINGS_FILE = "settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {"invert_colors": False}

def invert_color(color):
    return tuple(255 - c for c in color[:3])

pygame.init()

info = pygame.display.Info()
screen_width, screen_height = info.current_w, info.current_h
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("Level Select")

settings = load_settings()
invert = settings.get("invert_colors", False)

font = pygame.font.SysFont(None, 60)
small_font = pygame.font.SysFont(None, 40)

# Level button settings
levels = 10
level_buttons = []
button_width, button_height = 200, 100
gap = 40
start_x = (screen_width - (button_width * 5 + gap * 4)) // 2
start_y = screen_height // 2 - button_height - gap // 2

# Only level 1 is unlocked
unlocked_levels = 1

# Create level button rects and labels
for i in range(levels):
    row = i // 5
    col = i % 5
    x = start_x + col * (button_width + gap)
    y = start_y + row * (button_height + gap)
    rect = pygame.Rect(x, y, button_width, button_height)
    label = font.render(f"Level {i+1}", True, invert_color((255, 255, 255)) if invert else (255, 255, 255))
    level_buttons.append((rect, label))

# Arrow (back) button
arrow_points = [
    (80, 80), (40, 120), (80, 160), (80, 130), (160, 130), (160, 110), (80, 110)
]
arrow_rect = pygame.Rect(40, 80, 120, 80)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            # Check level buttons
            for i, (rect, label) in enumerate(level_buttons):
                if rect.collidepoint(mouse_pos):
                    if i < unlocked_levels:
                        if i == 0:
                            subprocess.Popen([sys.executable, "testi.py"])
                            running = False
                        else:
                            print(f"Level {i+1} selected!")  # Placeholder for other levels
            # Check arrow (back) button
            if arrow_rect.collidepoint(mouse_pos):
                subprocess.Popen([sys.executable, "Start-Menu.py"])
                running = False

    bg_color = (30, 30, 30) if not invert else (225, 225, 225)
    screen.fill(bg_color)

    # Draw level buttons
    for i, (rect, label) in enumerate(level_buttons):
        if i < unlocked_levels:
            color = (0, 200, 0) if not invert else invert_color((0, 200, 0))
        else:
            color = (100, 100, 100) if not invert else invert_color((100, 100, 100))
        pygame.draw.rect(screen, color, rect, border_radius=20)
        screen.blit(label, label.get_rect(center=rect.center))
        if i >= unlocked_levels:
            lock = small_font.render("Locked", True, invert_color((255, 0, 0)) if invert else (255, 0, 0))
            screen.blit(lock, lock.get_rect(center=(rect.centerx, rect.centery + 30)))

    # Draw back arrow
    arrow_color = (255, 255, 0) if not invert else invert_color((255, 255, 0))
    pygame.draw.polygon(screen, arrow_color, arrow_points)
    pygame.draw.rect(screen, invert_color((0, 0, 0)) if invert else (0, 0, 0), arrow_rect, 2)
    back_label = small_font.render("Back", True, arrow_color)
    screen.blit(back_label, (arrow_rect.right + 10, arrow_rect.centery - 20))

    pygame.display.flip()

pygame.quit()
sys.exit()