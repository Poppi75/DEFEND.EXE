import pygame
import sys
import os
import subprocess

pygame.init()

info = pygame.display.Info()
screen_width, screen_height = info.current_w, info.current_h
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("Level Select")

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
    label = font.render(f"Level {i+1}", True, (255, 255, 255))
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
                            # Launch testi.py for level 1
                            subprocess.Popen([sys.executable, "testi.py"])
                            running = False
                        else:
                            print(f"Level {i+1} selected!")  # Placeholder for other levels
            # Check arrow (back) button
            if arrow_rect.collidepoint(mouse_pos):
                # Go back to start menu
                subprocess.Popen([sys.executable, "Start-Menu.py"])
                running = False

    screen.fill((30, 30, 30))

    # Draw level buttons
    for i, (rect, label) in enumerate(level_buttons):
        if i < unlocked_levels:
            color = (0, 200, 0)
        else:
            color = (100, 100, 100)
        pygame.draw.rect(screen, color, rect, border_radius=20)
        screen.blit(label, label.get_rect(center=rect.center))
        if i >= unlocked_levels:
            lock = small_font.render("Locked", True, (255, 0, 0))
            screen.blit(lock, lock.get_rect(center=(rect.centerx, rect.centery + 30)))

    # Draw back arrow
    pygame.draw.polygon(screen, (255, 255, 0), arrow_points)
    pygame.draw.rect(screen, (0, 0, 0), arrow_rect, 2)
    back_label = small_font.render("Back", True, (255, 255, 0))
    screen.blit(back_label, (arrow_rect.right + 10, arrow_rect.centery - 20))

    pygame.display.flip()

pygame.quit()
sys.exit()