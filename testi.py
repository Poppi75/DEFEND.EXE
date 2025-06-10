import pygame
import sys

pygame.init()

# Set your virtual resolution (e.g., 480x800 for portrait mobile)
VIRTUAL_WIDTH, VIRTUAL_HEIGHT = 480, 800

# Get the actual screen size
info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h

# Create a window with the actual screen size
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Simple Pygame Window")

# Create a surface for your virtual resolution
virtual_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw everything on the virtual surface
    virtual_surface.fill((30, 30, 30))

    # Scale the virtual surface to the actual screen size
    scaled_surface = pygame.transform.smoothscale(virtual_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_surface, (0, 0))
    pygame.display.flip()

pygame.quit()
sys.exit()