import pygame
import sys
import subprocess

pygame.init()

info = pygame.display.Info()
screen_width, screen_height = info.current_w, info.current_h
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("Full Screen Pygame Window")

# Load and scale the background image
background = pygame.image.load("background.png")  # Change to your image filename
background = pygame.transform.scale(background, (screen_width, screen_height))  # Scale to fit the screen

font = pygame.font.SysFont(None, 80)
button_text = font.render("Start", True, (255, 255, 255))
button_text_rect = button_text.get_rect(center=(screen_width // 2, screen_height // 2 - 20))

quit_text = font.render("Quit", True, (255, 255, 255))
quit_text_rect = quit_text.get_rect(center=(screen_width // 2, screen_height // 2 + 120))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button_text_rect.collidepoint(event.pos):
                # Launch level_select.py instead of testi.py
                subprocess.Popen([sys.executable, "level_select.py"])
                running = False
            elif quit_text_rect.collidepoint(event.pos):
                running = False

    screen.blit(background, (0, 0))  # Draw the scaled background image
    screen.blit(button_text, button_text_rect)
    screen.blit(quit_text, quit_text_rect)
    pygame.display.flip()

pygame.quit()
sys.exit()