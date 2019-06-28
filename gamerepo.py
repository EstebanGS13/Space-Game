import pygame as pg
import random

# Screen related dimensions
SCREEN_WIDTH = 648
SCREEN_HEIGHT = 864 - 150  # Changed for testing purposes
UI = 20  # UI's height

# Attribute's constants
PLAYER_SPEED = 5
ENEMY_SPEED = 4
KIT_SPEED = 5

# Score modifiers
KILL_POINTS = 10
HIT_POINTS = 3
TAKE_DAMAGE = 2

# Drop ratios
HEAL_DROP_RATIO = 20  # 20 out of 100
SHIELD_DROP_RATIO = 50  # 10 out of 100

# Timers
SHIELD_UP_TIME = 20  # In seconds

# Colors
BLACK = [0, 0, 0]
WHITE = [255, 255, 255]
RED = [255, 0, 0]
GREEN = [0, 255, 0]
BLUE = [0, 0, 255]
YELLOW = [255, 255, 0]
BROWN = [128, 0, 0]
PURPLE = [128, 0, 128]
GRAY = [128, 128, 128]


def load_image(path, factor=1, size=96):
    """
    Takes an image's path, loads it up, then resizes it
    Args:

    Returns:
        An scaled image
    """
    resize = int(size * factor)
    img = pg.transform.smoothscale(pg.image.load(path), (resize, resize))
    return img


def load_animation(path, start, end, factor_x=1, factor_y=1, size_x=96, size_y=96):
    """
    Loops through several images' path, loads them up, resizes them
    and then appends them to a list
    Returns:
        A list of resized images
    """
    resize_x = int(size_x * factor_x)
    resize_y = int(size_y * factor_y)
    img_list = []
    for i in range(start, end):
        img = pg.transform.smoothscale(pg.image.load(
            path.format(str(i))), (resize_x, resize_y))
        img_list.append(img)
    return img_list


def cut_sprite(img, column, row, width, height):
    cut = img.subsurface(column * width, row * height, width, height)
    return cut


def sprites_matrix(img, sprite_width, sprite_height):
    img_info = img.get_rect()
    img_width = img_info[2]
    img_height = img_info[3]

    rows = img_height // sprite_height
    columns = img_width // sprite_width

    matrix = []
    for i in range(rows):
        row_list = []
        for j in range(columns):
            cut = cut_sprite(img, j, i, sprite_width, sprite_height)
            row_list.append(cut)
        matrix.append(row_list)
    return matrix


def generate_start_state(size=96):
    """
    Generates a random position to create
    the enemies either above the screen
    or to the sides of it and sets the
    enemy's speed accordingly
    """
    x_vel = 0
    y_vel = 0
    value = random.randrange(1000)
    if 0 < value <= 333:
        # Above
        x = random.randrange(0, SCREEN_WIDTH + 1 - size)
        y = -size
        y_vel = ENEMY_SPEED
    else:
        if 333 < value <= 666:
            # Right
            x = -size
            x_vel = ENEMY_SPEED
        else:
            # Left
            x = SCREEN_WIDTH
            x_vel = -ENEMY_SPEED
        y = random.randrange(0, int(SCREEN_HEIGHT * 2 / 3) + 1 - size)
    return [[x, y], [x_vel, y_vel]]


class Player(pg.sprite.Sprite):

    def __init__(self, screen_rect, motion, position):
        pg.sprite.Sprite.__init__(self)
        self.screen_rect = screen_rect
        self.motion = motion
        self.index = 0
        self.image = self.motion[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]
        self.mask = pg.mask.from_surface(self.image)
        self.speed = PLAYER_SPEED
        self.health = 10
        self.dead = False
        self.shield = False
        self.score = 0
        self.kills = 0

        self.sfx_laser = pg.mixer.Sound('sfx/laserfire01.ogg')
        self.sfx_laser_diag = pg.mixer.Sound('sfx/laserfire02.wav')
        self.sfx_health = pg.mixer.Sound('sfx/health.ogg')
        self.sfx_shield = pg.mixer.Sound('sfx/shield.ogg')
        self.sfx_shield_up = pg.mixer.Sound('sfx/Fx_shield.wav')  # todo cambiar a algo audible?
        self.sfx_impact_enemy = pg.mixer.Sound('sfx/impact.ogg')  # todo no se escucha
        self.sfx_take_dmg = pg.mixer.Sound('sfx/impact_enemy.ogg')
        self.sfx_kill = pg.mixer.Sound('sfx/destruction_enemy.wav')
        self.sfx_death = pg.mixer.Sound('sfx/destruction.ogg')

    def update(self, keys):
        self.rect.clamp_ip(self.screen_rect)  # Prevents it from moving outside the screen
        self.image = self.motion[self.index]
        if self.index < len(self.motion) - 1:
            self.index += 1
        else:
            self.index = 0

        if self.score < 0:
            self.score = 0

        # Movement
        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.rect.x -= self.speed
        elif keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.rect.x += self.speed
        elif keys[pg.K_UP] or keys[pg.K_w]:
            self.rect.y -= self.speed
        elif keys[pg.K_DOWN] or keys[pg.K_s]:
            self.rect.y += self.speed


class Enemy(pg.sprite.Sprite):

    def __init__(self, motion, position):
        pg.sprite.Sprite.__init__(self)
        self.motion = motion
        self.index = 0
        self.image = self.motion[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]
        self.radius = (self.rect[2] // 2) + 8  # Approx. radius
        self.mask = pg.mask.from_surface(self.image)
        self.speed = random.randrange(3, 6)
        self.vel_x = 0
        self.vel_y = 0
        self.health = 2
        self.timer = random.randrange(50)

    def dice(self):
        value = random.randrange(1000)
        if 0 < value <= 250:
            self.vel_x = 0
            self.vel_y = -self.speed
        elif 250 < value <= 500:
            self.vel_x = 0
            self.vel_y = self.speed
        elif 500 < value <= 750:
            self.vel_x = self.speed
            self.vel_y = 0
        else:
            self.vel_x = -self.speed
            self.vel_y = 0

    def update(self):
        self.image = self.motion[self.index]
        if self.index < len(self.motion) - 1:
            self.index += 1
        else:
            self.index = 0

        # Movement
        if self.vel_x == self.vel_y:
            self.dice()
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.timer -= 1
        # if not self.screen_rect.contains(self.rect):
        #     self.rect.clamp_ip(self.screen_rect)


class Laser(pg.sprite.Sprite):

    def __init__(self, img, vel_y, position):
        pg.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = position[0] - self.rect.centerx  # Puts the laser at the top center
        self.rect.y = position[1]
        self.radius = (self.rect[2] // 2)
        self.mask = pg.mask.from_surface(self.image)
        self.vel_y = vel_y

    def update(self):
        self.rect.y += self.vel_y


class Explosion(pg.sprite.Sprite):

    def __init__(self, motion, position):
        pg.sprite.Sprite.__init__(self)
        self.motion = motion
        self.index = 0
        self.image = self.motion[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = position

    def update(self):
        if self.index < len(self.motion) - 1:
            self.image = self.motion[self.index]
            self.index += 1


class Aid(pg.sprite.Sprite):

    def __init__(self, img, position):
        pg.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.mask = pg.mask.from_surface(self.image)
        self.vel_y = KIT_SPEED

    def update(self):
        self.rect.y += self.vel_y


class Shield(pg.sprite.Sprite):

    def __init__(self, img, position):
        pg.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.center = position
        self.radius = (self.rect[2] // 2) - 6  # Approx. radius
        self.active = False
        self.up_time = SHIELD_UP_TIME * 1000
        self.start = 0
        self.timer = 0
        self.remain_time = 0

    def update(self, player, current_time):
        self.rect.center = player.rect.center
        self.timer = current_time - self.start

        if self.active:
            self.remain_time = self.up_time - self.timer
            if self.timer > self.up_time:
                # if the difference between times is 20 seconds
                player.shield = False
                self.active = False


class HealthBar(pg.sprite.Sprite):

    def __init__(self, motion, position):
        pg.sprite.Sprite.__init__(self)
        self.motion = motion
        self.index = 10
        self.image = self.motion[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = position

    def update(self, player_hp):
        self.image = self.motion[player_hp]


class Background(pg.sprite.Sprite):

    def __init__(self, img):
        pg.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.bottomleft = [0, SCREEN_HEIGHT]
        self.vel_y = 2

    def update(self):
        if not self.rect.y == 0:
            self.rect.y += self.vel_y
