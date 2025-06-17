import pygame
import sys
import time
import math
import json
import os
import subprocess
import random

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
    if len(color) == 3:
        return tuple(255 - c for c in color)
    elif len(color) == 4:
        return tuple(255 - c for c in color[:3]) + (color[3],)
    else:
        return color

def unlock_level(level):
    settings = load_settings()
    if "unlocked_levels" not in settings or settings["unlocked_levels"] < level:
        settings["unlocked_levels"] = level
        save_settings(settings)

# --- PUZZLES ---
PUZZLES = [
    # LOGIC TASKS (8 puzzles)
    {
        "question": "Which number is missing?\n2, 4, 8, 16, ?",
        "options": [
            "18",
            "24",
            "32",
            "30"
        ],
        "answer": 2  # 32
    },
    {
        "question": "What is the output?\n\nif True or False and False:\n    print(\"Yes\")\nelse:\n    print(\"No\")",
        "options": [
            "Yes",
            "No",
            "Error",
            "None"
        ],
        "answer": 0  # Yes
    },
    {
        "question": "Which one does NOT belong?",
        "options": [
            "Firewall",
            "Antivirus",
            "Trojan",
            "Scanner"
        ],
        "answer": 2  # Trojan
    },
    {
        "question": "How many times will this run?\n\nfor i in range(0, 5):\n    print(i)",
        "options": [
            "4",
            "5",
            "6",
            "Infinite"
        ],
        "answer": 1  # 5
    },
    {
        "question": "Which one is NOT a valid boolean value?",
        "options": [
            "True",
            "False",
            "None",
            "Both"
        ],
        "answer": 2  # None
    },
    {
        "question": "You have a key, a firewall, and a lock. What opens access?",
        "options": [
            "Key",
            "Firewall",
            "Lock",
            "Virus"
        ],
        "answer": 0  # Key
    },
    {
        "question": "Which result is TRUE?\n\nnot (False and True)",
        "options": [
            "True",
            "False",
            "Error",
            "None"
        ],
        "answer": 0  # True
    },
    {
        "question": "If a scanner removes 3 viruses and 2 reappear, how many were removed in total?",
        "options": [
            "1",
            "5",
            "2",
            "3"
        ],
        "answer": 1  # 5
    },
    # CODE FIXES (Python only, 8 puzzles)
    {
        "question": "What’s wrong with this code?\n\nvalues = [1, 2, 3, 4]\nfor i in range(len(values)):\n    print(values[i + 1])",
        "options": [
            "values is not iterable",
            "i + 1 causes IndexError",
            "Syntax error",
            "It prints wrong values"
        ],
        "answer": 1  # i + 1 causes IndexError
    },
    {
        "question": "Why does this crash with AttributeError?\n\nnumber = 10\nprint(number.append(5))",
        "options": [
            "append used on int",
            "print() is broken",
            "append() needs two values",
            "number not declared"
        ],
        "answer": 0  # append used on int
    },
    {
        "question": "What’s the issue with this function?\n\ndef is_even(n):\n    if n % 2 = 0:\n        return True\n    else:\n        return False",
        "options": [
            "= used instead of ==",
            "% doesn’t work on n",
            "Should return a string",
            "Missing parameter"
        ],
        "answer": 0  # = used instead of ==
    },
    {
        "question": "What’s the fix for this crash?\n\nuser_input = input(\"Age: \")\nage = user_input + 5\nprint(age)",
        "options": [
            "Can’t add to string",
            "input() is invalid",
            "Must use f-strings",
            "age is undefined"
        ],
        "answer": 0  # Can’t add to string
    },
    {
        "question": "Why will this always return the same result?\n\ndef scan():\n    threats = []\n    threats.append(\"trojan\")\n    return threats\n\nthreats = scan()\nprint(threats)\nthreats = scan()\nprint(threats)",
        "options": [
            "List gets overwritten",
            "Same list object is reused",
            "append() doesn’t work",
            "Needs global variable"
        ],
        "answer": 1  # Same list object is reused
    },
    {
        "question": "Why is this if check unreliable?\n\nis_ready = \"False\"\nif not is_ready:\n    print(\"Not ready\")\nelse:\n    print(\"Ready\")",
        "options": [
            "String \"False\" is truthy",
            "not cannot be used",
            "Needs is_ready == False",
            "Crash at runtime"
        ],
        "answer": 0  # String "False" is truthy
    },
    {
        "question": "What causes this logic bug?\n\nfiles = [\"log.txt\", \"data.csv\", \"virus.exe\"]\nfor f in files:\n    if \"virus\" in f:\n        continue\n        print(\"Skipping virus\")",
        "options": [
            "continue should be break",
            "print after continue never runs",
            "\"virus\" isn’t in list",
            "Syntax error"
        ],
        "answer": 1  # print after continue never runs
    },
    {
        "question": "Why does this condition never trigger?\n\nconnections = None\nif len(connections) == 0:\n    print(\"No connections\")",
        "options": [
            "len() can’t be used on None",
            "connections is a string",
            "0 is not a valid length",
            "Should use connections.empty()"
        ],
        "answer": 0  # len() can’t be used on None
    },
    # SYSTEM ERRORS (8 puzzles)
    {
        "question": "What is a likely reason a firewall blocks traffic?",
        "options": [
            "CPU load",
            "Port not allowed",
            "Wi-Fi disabled",
            "Antivirus crash"
        ],
        "answer": 1  # Port not allowed
    },
    {
        "question": "Your scanner won’t start. What’s first to check?",
        "options": [
            "Internet",
            "Power",
            "Permissions",
            "BIOS"
        ],
        "answer": 2  # Permissions
    },
    {
        "question": "Program crashes only on one OS. What’s likely?",
        "options": [
            "Syntax error",
            "OS-specific paths",
            "RAM issue",
            "Resolution mismatch"
        ],
        "answer": 1  # OS-specific paths
    },
    {
        "question": "You see “FileNotFoundError”. What does that mean?",
        "options": [
            "Missing import",
            "Syntax error",
            "File doesn't exist",
            "Permission denied"
        ],
        "answer": 2  # File doesn't exist
    },
    {
        "question": "Your antivirus says “update failed.” Most likely cause?",
        "options": [
            "CPU overheat",
            "Disk full",
            "No internet",
            "Wrong version"
        ],
        "answer": 2  # No internet
    },
    {
        "question": "You launch a scanner, but nothing happens. What’s missing?",
        "options": [
            "Admin rights",
            "DNS",
            "Display driver",
            "API"
        ],
        "answer": 0  # Admin rights
    },
    {
        "question": "You get \"Access denied\" when writing a file. Why?",
        "options": [
            "Wrong filename",
            "Permission issue",
            "File too large",
            "OS crash"
        ],
        "answer": 1  # Permission issue
    },
    {
        "question": "App fails to open and throws a “missing DLL” error. This means:",
        "options": [
            "Disk failure",
            "Library file not found",
            "Invalid port",
            "Path too long"
        ],
        "answer": 1  # Library file not found
    }
]

pygame.init()

info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
VIRTUAL_WIDTH, VIRTUAL_HEIGHT = SCREEN_WIDTH, SCREEN_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
virtual_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))

font = pygame.font.SysFont("Arial", 32)
small_font = pygame.font.SysFont("Arial", 20)
big_font = pygame.font.SysFont("Arial", 80)

towers = []
enemies = []
bullets = []
lives = 3
score = 0

PATH = [(0, 400), (400, 400), (400, 700), (1000, 700), (1000, 100), 
        (1600, 100), (1600, 250), (1350, 250), (1350, 650), 
        (1600, 650), (1600, 900), (800, 900), (800, 1100)]

settings = load_settings()
invert = settings.get("invert_colors", False)

MENU_WIDTH = 120
MENU_BG = (50, 50, 80)
TOWER_TYPES = [
    {
        "name": "Blue",
        "color": (0, 0, 200),
        "range": 140,
        "cooldown": 60,
        "fire_rate": 60,
        "acquire_delay": int(1.5 * 60),
    },
    {
        "name": "Red",
        "color": (200, 0, 0),
        "range": 70,
        "cooldown": 30,
        "fire_rate": 30,
        "acquire_delay": int(1.0 * 60),
    },
    {
        "name": "Green",
        "color": (0, 180, 0),
        "range": 180,
        "cooldown": 90,
        "fire_rate": 90,
        "acquire_delay": int(2.0 * 60),
    },
    {
        "name": "Yellow",
        "color": (200, 200, 0),
        "range": 100,
        "cooldown": 45,
        "fire_rate": 45,
        "acquire_delay": int(1.2 * 60),
    },
]

# --- Puzzle state ---
puzzle_active = False
current_puzzle = None
puzzle_result = None  # None, True, or False
puzzle_option_rects = []
last_puzzle_index = None  # For random puzzle selection
tower_place_cooldowns = [0 for _ in TOWER_TYPES]  # Per-tower-type cooldown

class Tower:
    def __init__(self, x, y, ttype=0):
        self.x, self.y = x, y
        self.type = ttype
        self.range = TOWER_TYPES[ttype]["range"]
        self.cooldown = TOWER_TYPES[ttype]["cooldown"]
        self.fire_rate = TOWER_TYPES[ttype]["fire_rate"]
        self.acquire_delay = TOWER_TYPES[ttype]["acquire_delay"]
        self.target = None

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
        # Blue tower (type 0) does not shoot
        if self.type == 0:
            return
        if self.target not in enemies or (
            self.target and math.hypot(self.target.pos[0] - self.x, self.target.pos[1] - self.y) > self.range
        ):
            self.target = None
            self.acquire_delay = 0

        if self.cooldown > 0:
            self.cooldown -= 1
            return

        if self.target is None:
            for enemy in enemies:
                dx = enemy.pos[0] - self.x
                dy = enemy.pos[1] - self.y
                dist = math.hypot(dx, dy)
                if dist <= self.range:
                    self.target = enemy
                    self.acquire_delay = int(1.5 * 60)
                    break

        if self.target:
            if self.acquire_delay > 0:
                self.acquire_delay -= 1
                return
            if not any(bullet.target == self.target and bullet.x == self.x and bullet.y == self.y for bullet in bullets):
                bullets.append(Bullet(self.x, self.y, self.target))
                self.cooldown = self.fire_rate

class Enemy:
    def __init__(self, path):
        self.path = path
        self.pos = list(path[0])
        self.path_index = 0
        self.speed = 1  # Slower base enemy
        self.hp = 1
        self.original_speed = self.speed  # <-- Add this line

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

class FastEnemy(Enemy):
    def __init__(self, path):
        super().__init__(path)
        self.speed = 2  # Faster
        self.original_speed = self.speed  # <-- Add this line

    def draw(self, surf):
        color = (0, 200, 255) if not invert else invert_color((0, 200, 255))
        pygame.draw.circle(surf, color, (int(self.pos[0]), int(self.pos[1])), 18)

class DurableEnemy(Enemy):
    def __init__(self, path):
        super().__init__(path)
        self.hp = 3
        self.speed = 1
        self.original_speed = self.speed  # <-- Add this line

    def draw(self, surf):
        color = (128, 0, 128) if not invert else invert_color((128, 0, 128))
        pygame.draw.circle(surf, color, (int(self.pos[0]), int(self.pos[1])), 24)
        hp_label = small_font.render(str(self.hp), True, (255,255,255) if not invert else (0,0,0))
        surf.blit(hp_label, (int(self.pos[0])-10, int(self.pos[1])-10))

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
    VIRTUAL_WIDTH - pause_button_size - 10,
    VIRTUAL_HEIGHT - pause_button_size - 10,
    pause_button_size,
    pause_button_size
)
paused = False

placing_tower = False
placement_preview = None
dragging = False

# --- Wave system ---
current_wave = 1
max_wave = 3
enemies_to_spawn = []
spawn_cooldown = 0
next_enemy_spawn_offset = 0  # <-- Add this line
wave_in_progress = False
game_won = False
game_lost = False

def setup_wave(wave):
    if wave == 1:
        wave_list = [Enemy(PATH) for _ in range(15)]
    elif wave == 2:
        wave_list = [Enemy(PATH) for _ in range(15)] + [FastEnemy(PATH) for _ in range(5)]
    elif wave == 3:
        wave_list = [Enemy(PATH) for _ in range(15)] + [FastEnemy(PATH) for _ in range(10)] + [DurableEnemy(PATH) for _ in range(5)]
    else:
        wave_list = []
    random.shuffle(wave_list)
    # Add spawn_offset to each enemy so they spawn apart
    for i, enemy in enumerate(wave_list):
        enemy.spawn_offset = i * 20  # 20 frames apart, adjust as needed
    return wave_list

def draw_pause_menu(surface):
    overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    surface.blit(overlay, (0, 0))

    resume_rect = pygame.Rect(VIRTUAL_WIDTH//2 - 120, VIRTUAL_HEIGHT//2 - 120, 240, 60)
    settings_rect = pygame.Rect(VIRTUAL_WIDTH//2 - 120, VIRTUAL_HEIGHT//2 - 40, 240, 60)
    restart_rect = pygame.Rect(VIRTUAL_WIDTH//2 - 120, VIRTUAL_HEIGHT//2 + 40, 240, 60)
    mainmenu_rect = pygame.Rect(VIRTUAL_WIDTH//2 - 120, VIRTUAL_HEIGHT//2 + 120, 240, 60)

    resume_color = (100, 200, 100) if not invert else invert_color((100, 200, 100))
    settings_color = (100, 100, 255) if not invert else invert_color((100, 100, 255))
    restart_color = (200, 200, 0) if not invert else invert_color((200, 200, 0))
    mainmenu_color = (200, 0, 0) if not invert else invert_color((200, 0, 0))

    pygame.draw.rect(surface, resume_color, resume_rect)
    pygame.draw.rect(surface, settings_color, settings_rect)
    pygame.draw.rect(surface, restart_color, restart_rect)
    pygame.draw.rect(surface, mainmenu_color, mainmenu_rect)

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

# Helper to shuffle puzzle options and update answer index
def get_shuffled_puzzle(puzzle):
    options = list(puzzle["options"])
    answer = puzzle["answer"]
    zipped = list(enumerate(options))
    random.shuffle(zipped)
    new_options = [opt for idx, opt in zipped]
    new_answer = [i for i, (orig_idx, _) in enumerate(zipped) if orig_idx == answer][0]
    return {
        "question": puzzle["question"],  # Removed extra text
        "options": new_options,
        "answer": new_answer
    }

def is_valid_tower_position(x, y, ttype):
    for tower in towers:
        if math.hypot(tower.x - x, tower.y - y) < 40:
            return False
    for i in range(len(PATH) - 1):
        x1, y1 = PATH[i]
        x2, y2 = PATH[i + 1]
        px, py = x, y
        dx, dy = x2 - x1, y2 - y1  # <-- FIXED HERE
        if dx == dy == 0:
            dist = math.hypot(px - x1, py - y1)
        else:
            t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
            proj_x = x1 + t * dx
            proj_y = y1 + t * dy
            dist = math.hypot(px - proj_x, py - proj_y)
        if dist < 40:
            return False
    return True

running = True
while running:
    for event in pygame.event.get():
        # --- Puzzle answer handling ---
        if puzzle_active and current_puzzle and event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            vx = int(mx * VIRTUAL_WIDTH / SCREEN_WIDTH)
            vy = int(my * VIRTUAL_HEIGHT / SCREEN_HEIGHT)
            for idx, opt_rect in enumerate(puzzle_option_rects):
                if opt_rect.collidepoint(vx, vy):
                    ttype = placement_preview[2] if placement_preview else 0
                    if idx == current_puzzle["answer"]:
                        if is_valid_tower_position(placement_preview[0], placement_preview[1], ttype):
                            towers.append(Tower(placement_preview[0], placement_preview[1], ttype))
                            puzzle_result = True
                            placing_tower = False
                            placement_preview = None
                            dragging = False
                            tower_place_cooldowns[ttype] = 120  # 2 seconds for this tower
                            puzzle_active = False
                        else:
                            puzzle_result = "invalid"
                            # Re-shuffle puzzle for next attempt
                            available = [i for i in range(len(PUZZLES)) if i != last_puzzle_index]
                            if not available:
                                available = list(range(len(PUZZLES)))
                            idx2 = random.choice(available)
                            current_puzzle = get_shuffled_puzzle(PUZZLES[idx2])
                            last_puzzle_index = idx2
                            puzzle_active = True
                            continue  # Skip rest of event loop for this click
                    else:
                        puzzle_result = False
                        placing_tower = False
                        placement_preview = None
                        dragging = False
                        tower_place_cooldowns[ttype] = 120  # 2 seconds for this tower
                        puzzle_active = False

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

            if not paused and not game_won and not game_lost and not puzzle_active:
                menu_left = VIRTUAL_WIDTH - MENU_WIDTH
                menu_y = 60
                if not placing_tower:
                    if vx >= menu_left:
                        for i, ttype in enumerate(TOWER_TYPES):
                            rect = pygame.Rect(menu_left + 10, menu_y + i * 70, 100, 60)
                            if rect.collidepoint(vx, vy):
                                if tower_place_cooldowns[i] == 0:
                                    selected_tower_type = i
                    elif selected_tower_type is not None:
                        placing_tower = True
                        placement_preview = [vx, vy, selected_tower_type]
                        dragging = True
                        selected_tower_type = None
                else:
                    accept_rect = pygame.Rect(placement_preview[0] + 50, placement_preview[1] - 30, 80, 40)
                    cancel_rect = pygame.Rect(placement_preview[0] - 130, placement_preview[1] - 30, 80, 40)
                    if accept_rect.collidepoint(vx, vy):
                        ttype = placement_preview[2]
                        if not puzzle_active and tower_place_cooldowns[ttype] == 0:
                            # Pick a random puzzle, not the same as last time if possible
                            available = [i for i in range(len(PUZZLES)) if i != last_puzzle_index]
                            if not available:
                                available = list(range(len(PUZZLES)))
                            idx = random.choice(available)
                            current_puzzle = get_shuffled_puzzle(PUZZLES[idx])
                            last_puzzle_index = idx
                            puzzle_active = True
                            puzzle_result = None
                    elif cancel_rect.collidepoint(vx, vy):
                        placing_tower = False
                        placement_preview = None
                        dragging = False
                    else:
                        tower_rect = pygame.Rect(placement_preview[0] - 20, placement_preview[1] - 20, 40, 40)
                        if tower_rect.collidepoint(vx, vy):
                            dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if placing_tower and dragging:
                mx, my = pygame.mouse.get_pos()
                vx = int(mx * VIRTUAL_WIDTH / SCREEN_WIDTH)
                vy = int(my * VIRTUAL_HEIGHT / SCREEN_HEIGHT)
                placement_preview[0] = vx
                placement_preview[1] = vy

    # --- Wave logic ---
    if not wave_in_progress and not enemies and not enemies_to_spawn and not game_won and not game_lost:
        if current_wave <= max_wave:
            enemies_to_spawn = setup_wave(current_wave)
            wave_in_progress = True
            spawn_cooldown = 0
        else:
            game_won = True

    if wave_in_progress and enemies_to_spawn and not game_won and not game_lost:
        spawn_cooldown -= 1
        if spawn_cooldown <= 0:
            # Only spawn if the next enemy's offset is reached
            if hasattr(enemies_to_spawn[0], "spawn_offset") and enemies_to_spawn[0].spawn_offset > 0:
                enemies_to_spawn[0].spawn_offset -= 1
                spawn_cooldown = 1  # Check again next frame
            else:
                enemy = enemies_to_spawn.pop(0)
                enemies.append(enemy)
                spawn_cooldown = 30  # base interval between spawns

    if wave_in_progress and not enemies_to_spawn and not enemies and not game_won and not game_lost:
        current_wave += 1
        wave_in_progress = False

    if not paused and not game_won and not game_lost:
        # --- Apply Blue tower slow effect ---
        for enemy in enemies:
            enemy.speed = enemy.original_speed  # Reset speed each frame

        for tower in towers:
            if tower.type == 0:  # Blue tower
                for enemy in enemies:
                    dx = enemy.pos[0] - tower.x
                    dy = enemy.pos[1] - tower.y
                    dist = math.hypot(dx, dy)
                    if dist <= tower.range:
                        enemy.speed = enemy.original_speed * 0.35  # Slow to 35% speed

        for tower in towers:
            tower.shoot(enemies, bullets)

        for bullet in bullets[:]:
            bullet.update()
            if bullet.target and math.hypot(bullet.x - bullet.target.pos[0], bullet.y - bullet.target.pos[1]) < bullet.radius + 20:
                if bullet.target in enemies:
                    bullet.target.hp -= 1
                    if bullet.target.hp <= 0:
                        enemies.remove(bullet.target)
                        score += 1
                bullets.remove(bullet)

        for enemy in enemies[:]:
            enemy.update()
            if enemy.path_index == len(enemy.path) - 1:
                enemies.remove(enemy)
                lives -= 1
                if lives <= 0:
                    game_lost = True

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
    wave_label = font.render(f"Wave: {min(current_wave, max_wave)}", True, fg)
    virtual_surface.blit(wave_label, (10, 50))
    # Removed: small = small_font.render("ESC to quit, click to place towers", True, fg)
    # Removed: virtual_surface.blit(small, (10, 90))

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
        # Draw cooldown overlay if needed
        if tower_place_cooldowns[i] > 0:
            cooldown_overlay = pygame.Surface((100, 60), pygame.SRCALPHA)
            cooldown_overlay.fill((0, 0, 0, 180))
            virtual_surface.blit(cooldown_overlay, (rect.x, rect.y))
            cd_text = small_font.render(f"{tower_place_cooldowns[i]//60+1}s", True, (255,255,0))
            cd_rect = cd_text.get_rect(center=rect.center)
            virtual_surface.blit(cd_text, cd_rect)

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

    # Draw placement preview if needed
    if placing_tower and placement_preview:
        px, py, ttype = placement_preview
        valid = is_valid_tower_position(px, py, ttype)
        if valid:
            preview_color = TOWER_TYPES[ttype]["color"] if not invert else invert_color(TOWER_TYPES[ttype]["color"])
            radius_color = (100, 100, 255) if not invert else invert_color((100, 100, 255))
        else:
            preview_color = (200, 50, 50) if not invert else invert_color((200, 50, 50))
            radius_color = (200, 50, 50) if not invert else invert_color((200, 50, 50))
        pygame.draw.rect(virtual_surface, preview_color, (px - 20, py - 20, 40, 40), 2)
        pygame.draw.circle(
            virtual_surface,
            radius_color,
            (px, py),
            TOWER_TYPES[ttype]["range"],
            1,
        )
        accept_rect = pygame.Rect(px + 50, py - 30, 80, 40)
        cancel_rect = pygame.Rect(px - 130, py - 30, 80, 40)
        pygame.draw.rect(virtual_surface, (0, 200, 0), accept_rect)
        pygame.draw.rect(virtual_surface, (200, 0, 0), cancel_rect)
        accept_label = small_font.render("Accept", True, (255, 255, 255))
        cancel_label = small_font.render("Cancel", True, (255, 255, 255))
        virtual_surface.blit(accept_label, (px + 60, py - 22))
        virtual_surface.blit(cancel_label, (px - 120, py - 22))

    # --- Puzzle UI ---
    if puzzle_active and current_puzzle:
        # Calculate question height
        lines = current_puzzle["question"].split('\n')
        line_height = small_font.get_height() + 4
        question_height = len(lines) * line_height

        option_height = 40
        option_spacing = 8
        total_options_height = len(current_puzzle["options"]) * (option_height + option_spacing)

        padding = 24
        box_width = 640
        box_height = padding*2 + question_height + total_options_height

        puzzle_rect = pygame.Rect(
            VIRTUAL_WIDTH//2 - box_width//2,
            VIRTUAL_HEIGHT//2 - box_height//2,
            box_width,
            box_height
        )
        pygame.draw.rect(virtual_surface, (30,30,30), puzzle_rect)
        pygame.draw.rect(virtual_surface, (200,200,200), puzzle_rect, 3)

        # Draw question
        for i, line in enumerate(lines):
            q_text = small_font.render(line, True, (255,255,255))
            virtual_surface.blit(q_text, (puzzle_rect.x + 20, puzzle_rect.y + padding + i*line_height))

        # Draw options
        option_rects = []
        options_start_y = puzzle_rect.y + padding + question_height + 10
        for i, opt in enumerate(current_puzzle["options"]):
            opt_rect = pygame.Rect(
                puzzle_rect.x + 40,
                options_start_y + i*(option_height + option_spacing),
                box_width - 80,
                option_height
            )
            pygame.draw.rect(virtual_surface, (80,80,80), opt_rect)
            pygame.draw.rect(virtual_surface, (200,200,200), opt_rect, 2)
            # Wrap answer text if too long
            opt_text = small_font.render(opt, True, (255,255,0))
            virtual_surface.blit(opt_text, (opt_rect.x + 10, opt_rect.y + 8))
            option_rects.append(opt_rect)
        puzzle_option_rects = option_rects
    elif puzzle_result == "invalid":
        res_text = font.render("Invalid position!", True, (255,0,0))
        virtual_surface.blit(res_text, res_text.get_rect(center=(VIRTUAL_WIDTH//2, VIRTUAL_HEIGHT//2)))
    elif puzzle_result is not None:
        result_text = "Correct!" if puzzle_result else "Incorrect!"
        color = (0,255,0) if puzzle_result else (255,0,0)
        res_text = font.render(result_text, True, color)
        virtual_surface.blit(res_text, res_text.get_rect(center=(VIRTUAL_WIDTH//2, VIRTUAL_HEIGHT//2)))

    if paused:
        draw_pause_menu(virtual_surface)

    # WIN/LOSE SCENES
    if game_won:
        win_text = big_font.render("You Win!", True, (0, 255, 0))
        text_rect = win_text.get_rect(midtop=(VIRTUAL_WIDTH//2, 60))
        bg_rect = pygame.Rect(text_rect.left - 20, text_rect.top - 10, text_rect.width + 40, text_rect.height + 20)
        pygame.draw.rect(virtual_surface, (0, 0, 0), bg_rect)
        virtual_surface.blit(win_text, text_rect)
        unlock_level(2)
        scaled = pygame.transform.scale(virtual_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaled, (0, 0))
        pygame.display.flip()
        pygame.time.wait(2000)
        subprocess.Popen([sys.executable, "level_select.py"])
        break

    if game_lost:
        lose_text = big_font.render("You Lose!", True, (255, 0, 0))
        text_rect = lose_text.get_rect(midtop=(VIRTUAL_WIDTH//2, 60))
        bg_rect = pygame.Rect(text_rect.left - 20, text_rect.top - 10, text_rect.width + 40, text_rect.height + 20)
        pygame.draw.rect(virtual_surface, (0, 0, 0), bg_rect)
        virtual_surface.blit(lose_text, text_rect)
        restart_rect = pygame.Rect(VIRTUAL_WIDTH//2 - 120, VIRTUAL_HEIGHT//2 + 10, 240, 60)
        levelselect_rect = pygame.Rect(VIRTUAL_WIDTH//2 - 120, VIRTUAL_HEIGHT//2 + 90, 240, 60)
        mainmenu_rect = pygame.Rect(VIRTUAL_WIDTH//2 - 120, VIRTUAL_HEIGHT//2 + 170, 240, 60)
        pygame.draw.rect(virtual_surface, (100, 200, 100), restart_rect)
        pygame.draw.rect(virtual_surface, (100, 100, 255), levelselect_rect)
        pygame.draw.rect(virtual_surface, (200, 0, 0), mainmenu_rect)
        restart_label = font.render("Restart", True, (255,255,255))
        levelselect_label = font.render("Level Select", True, (255,255,255))
        mainmenu_label = font.render("Main Menu", True, (255,255,255))
        virtual_surface.blit(restart_label, restart_label.get_rect(center=restart_rect.center))
        virtual_surface.blit(levelselect_label, levelselect_label.get_rect(center=levelselect_rect.center))
        virtual_surface.blit(mainmenu_label, mainmenu_label.get_rect(center=mainmenu_rect.center))
        scaled = pygame.transform.scale(virtual_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(scaled, (0, 0))
        pygame.display.flip()
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    vx = int(mx * VIRTUAL_WIDTH / SCREEN_WIDTH)
                    vy = int(my * VIRTUAL_HEIGHT / SCREEN_HEIGHT)
                    if restart_rect.collidepoint(vx, vy):
                        subprocess.Popen([sys.executable, "level1.py"])
                        waiting = False
                        running = False
                    elif levelselect_rect.collidepoint(vx, vy):
                        subprocess.Popen([sys.executable, "level_select.py"])
                        waiting = False
                        running = False
                    elif mainmenu_rect.collidepoint(vx, vy):
                        subprocess.Popen([sys.executable, "Start-Menu.py"])
                        waiting = False
                        running = False
        break

    scaled = pygame.transform.scale(virtual_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled, (0, 0))
    pygame.display.flip()

    # Puzzle cooldown decrement (now per-tower-type)
    for i in range(len(tower_place_cooldowns)):
        if tower_place_cooldowns[i] > 0:
            tower_place_cooldowns[i] -= 1
    if puzzle_result is not None and tower_place_cooldowns[0] == 0:
        puzzle_result = None

pygame.quit()
sys.exit()
