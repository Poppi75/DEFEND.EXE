import pygame
import sys
import subprocess
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

def invert_surface(surface):
    arr = pygame.surfarray.array3d(surface)
    arr = 255 - arr
    return pygame.surfarray.make_surface(arr)

pygame.init()

info = pygame.display.Info()
screen_width, screen_height = info.current_w, info.current_h
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("Full Screen Pygame Window")

settings = load_settings()
invert = settings.get("invert_colors", False)

# Load and scale the background image
background = pygame.image.load("background.png")
background = pygame.transform.scale(background, (screen_width, screen_height))
if invert:
    background = invert_surface(background)

font = pygame.font.SysFont(None, 80)
fg = (255, 255, 255) if not invert else (0, 0, 0)
button_text = font.render("Start", True, fg)
button_text_rect = button_text.get_rect(center=(screen_width // 2, screen_height // 2 - 80 + 100))

settings_text = font.render("Settings", True, fg)
settings_text_rect = settings_text.get_rect(center=(screen_width // 2, screen_height // 2 + 0 + 100))

quit_text = font.render("Quit", True, fg)
quit_text_rect = quit_text.get_rect(center=(screen_width // 2, screen_height // 2 + 80 + 100))

delete_font = pygame.font.SysFont(None, 40)
delete_text = delete_font.render("Delete Progress", True, fg)
delete_text_rect = delete_text.get_rect(bottomright=(screen_width - 40, screen_height - 30))

progress_deleted = False  # Add this flag

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            settings["invert_colors"] = False
            save_settings(settings)
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button_text_rect.collidepoint(event.pos):
                subprocess.Popen([sys.executable, "level_select.py"])
                running = False
            elif quit_text_rect.collidepoint(event.pos):
                settings["invert_colors"] = False
                save_settings(settings)
                running = False
            elif settings_text_rect.collidepoint(event.pos):
                subprocess.call([sys.executable, "settings.py"])
                # Reload settings and update invert variable
                settings = load_settings()
                invert = settings.get("invert_colors", False)
                # Update colors and background
                fg = (255, 255, 255) if not invert else (0, 0, 0)
                background = pygame.image.load("background.png")
                background = pygame.transform.scale(background, (screen_width, screen_height))
                if invert:
                    background = invert_surface(background)
                button_text = font.render("Start", True, fg)
                button_text_rect = button_text.get_rect(center=(screen_width // 2, screen_height // 2 - 80 + 100))
                settings_text = font.render("Settings", True, fg)
                settings_text_rect = settings_text.get_rect(center=(screen_width // 2, screen_height // 2 + 0 + 100))
                quit_text = font.render("Quit", True, fg)
                quit_text_rect = quit_text.get_rect(center=(screen_width // 2, screen_height // 2 + 80 + 100))
                delete_text = delete_font.render("Delete Progress", True, fg)
                delete_text_rect = delete_text.get_rect(bottomright=(screen_width - 40, screen_height - 30))
            elif delete_text_rect.collidepoint(event.pos):
                # Reset unlocked_levels to 1
                settings["unlocked_levels"] = 1
                save_settings(settings)
                progress_deleted = True  # Set flag

    screen.blit(background, (0, 0))
    screen.blit(button_text, button_text_rect)
    screen.blit(settings_text, settings_text_rect)
    screen.blit(quit_text, quit_text_rect)
    screen.blit(delete_text, delete_text_rect)

    if progress_deleted:
        confirm_text = delete_font.render("Progress deleted!", True, (255, 80, 80))
        confirm_rect = confirm_text.get_rect(bottomright=(screen_width - 40, screen_height - 70))
        screen.blit(confirm_text, confirm_rect)

    pygame.display.flip()

pygame.quit()
sys.exit()