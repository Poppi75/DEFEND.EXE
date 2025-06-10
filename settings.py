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

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

def invert_color(color):
    return tuple(255 - c for c in color[:3])

pygame.init()
info = pygame.display.Info()
screen_width, screen_height = info.current_w, info.current_h
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("Settings")

font = pygame.font.SysFont(None, 80)
small_font = pygame.font.SysFont(None, 50)

settings = load_settings()
invert = settings.get("invert_colors", False)

def update_texts():
    fg = (255, 255, 255) if not invert else (0, 0, 0)
    return (
        small_font.render("Invert Colors", True, fg),
        small_font.render("Back", True, fg)
    )

invert_text, back_text = update_texts()
invert_rect = invert_text.get_rect(center=(screen_width // 2, screen_height // 2))
back_rect = back_text.get_rect(center=(screen_width // 2, screen_height // 2 + 120))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if invert_rect.collidepoint(event.pos):
                invert = not invert
                settings["invert_colors"] = invert
                save_settings(settings)
                invert_text, back_text = update_texts()
            elif back_rect.collidepoint(event.pos):
                import subprocess
                import sys
                subprocess.Popen([sys.executable, "Start-Menu.py"])
                running = False

    bg_color = (30, 30, 30) if not invert else (225, 225, 225)
    screen.fill(bg_color)
    screen.blit(invert_text, invert_rect)
    screen.blit(back_text, back_rect)
    pygame.display.flip()

pygame.quit()
sys.exit()