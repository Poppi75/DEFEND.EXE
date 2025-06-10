import pygame
import sys

# Initialize pygame
pygame.init()

# Set window size
size = (400, 300)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Simple Pygame Window")

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((30, 30, 30))  # Fill the screen with a dark color
    pygame.display.flip()

pygame.quit()
sys.exit()