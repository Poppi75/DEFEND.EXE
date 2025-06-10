import pygame
import sys
import math

pygame.init()

VIRTUAL_WIDTH, VIRTUAL_HEIGHT = 480, 800
info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Simple Tower Defense")
virtual_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

# Enemy path (straight line)
PATH = [(50, 800), (50, 100), (430, 100), (430, 700)]

class Enemy:
    def __init__(self):
        self.path_index = 0
        self.x, self.y = PATH[0]
        self.speed = 1.2
        self.radius = 15
        self.hp = 3

    def move(self):
        if self.path_index + 1 < len(PATH):
            tx, ty = PATH[self.path_index + 1]
            dx, dy = tx - self.x, ty - self.y
            dist = math.hypot(dx, dy)
            if dist < self.speed:
                self.x, self.y = tx, ty
                self.path_index += 1
            else:
                self.x += self.speed * dx / dist
                self.y += self.speed * dy / dist

    def draw(self, surf):
        pygame.draw.circle(surf, (200, 50, 50), (int(self.x), int(self.y)), self.radius)
        # Draw HP bar
        pygame.draw.rect(surf, (0,255,0), (self.x-15, self.y-25, 30*self.hp/3, 5))

    def reached_end(self):
        return self.path_index == len(PATH) - 1 and math.hypot(self.x - PATH[-1][0], self.y - PATH[-1][1]) < 2

class Tower:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.range = 120
        self.reload = 0

    def draw(self, surf):
        pygame.draw.rect(surf, (100, 100, 255), (self.x-15, self.y-15, 30, 30))
        pygame.draw.circle(surf, (100,100,255,40), (self.x, self.y), self.range, 1)

    def shoot(self, enemies, bullets):
        if self.reload > 0:
            self.reload -= 1
            return
        for e in enemies:
            if math.hypot(e.x - self.x, e.y - self.y) < self.range:
                bullets.append(Bullet(self.x, self.y, e))
                self.reload = 30
                break

class Bullet:
    def __init__(self, x, y, target):
        self.x, self.y = x, y
        self.target = target
        self.speed = 6

    def move(self):
        dx, dy = self.target.x - self.x, self.target.y - self.y
        dist = math.hypot(dx, dy)
        if dist < self.speed or self.target.hp <= 0:
            return True
        self.x += self.speed * dx / dist
        self.y += self.speed * dy / dist
        return False

    def draw(self, surf):
        pygame.draw.circle(surf, (255,255,0), (int(self.x), int(self.y)), 6)

enemies = []
bullets = []
tower = Tower(240, 400)
spawn_timer = 0
lives = 5
score = 0

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Game logic
    spawn_timer += 1
    if spawn_timer > 60 and len(enemies) < 10:
        enemies.append(Enemy())
        spawn_timer = 0

    for e in enemies:
        e.move()
    tower.shoot(enemies, bullets)

    for b in bullets[:]:
        if b.move():
            if b.target.hp > 0:
                b.target.hp -= 1
            bullets.remove(b)

    # Remove dead enemies
    for e in enemies[:]:
        if e.hp <= 0:
            enemies.remove(e)
            score += 1
        elif e.reached_end():
            enemies.remove(e)
            lives -= 1

    # Draw
    virtual_surface.fill((30, 30, 30))
    # Draw path
    pygame.draw.lines(virtual_surface, (100,255,100), False, PATH, 8)
    tower.draw(virtual_surface)
    for e in enemies:
        e.draw(virtual_surface)
    for b in bullets:
        b.draw(virtual_surface)

    # Draw UI
    font = pygame.font.SysFont(None, 32)
    txt = font.render(f"Lives: {lives}  Score: {score}", True, (255,255,255))
    virtual_surface.blit(txt, (10,10))

    if lives <= 0:
        txt = font.render("Game Over!", True, (255,0,0))
        virtual_surface.blit(txt, (160, 380))
        pygame.display.flip()
        pygame.time.wait(2000)
        break
    elif score >= 10:
        txt = font.render("You Win!", True, (0,255,0))
        virtual_surface.blit(txt, (180, 380))
        pygame.display.flip()
        pygame.time.wait(2000)
        break

    # Calculate scale factor and position for aspect ratio preservation
    scale = min(SCREEN_WIDTH / VIRTUAL_WIDTH, SCREEN_HEIGHT / VIRTUAL_HEIGHT)
    new_width = int(VIRTUAL_WIDTH * scale)
    new_height = int(VIRTUAL_HEIGHT * scale)
    scaled_surface = pygame.transform.smoothscale(virtual_surface, (new_width, new_height))
    x_offset = (SCREEN_WIDTH - new_width) // 2
    y_offset = (SCREEN_HEIGHT - new_height) // 2
    screen.fill((0, 0, 0))  # Fill background for letterboxing
    screen.blit(scaled_surface, (x_offset, y_offset))
    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()