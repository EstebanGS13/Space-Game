import pygame as pg
import random

SCREEN_WIDTH = 648
SCREEN_HEIGHT = 864 - 150  # Changed for testing purposes
UI = 50  # UI's height

BLACK = [0, 0, 0]
WHITE = [255, 255, 255]
RED = [255, 0, 0]
GREEN = [0, 255, 0]
BLUE = [0, 0, 255]
YELLOW = [255, 255, 0]
BROWN = [128, 0, 0]
PURPLE = [128, 0, 128]
GRAY = [128, 128, 128]

PLAYER_SPEED = 5
ENEMY_SPEED = 4
KIT_SPEED = 5


def load_image(path, factor, size=96):
    """
    Takes an image's path, loads it up, then resizes it
    Args:

    Returns:
        An scaled image
    """
    resize = int(size * factor)
    img = pg.transform.smoothscale(pg.image.load(path), (resize, resize))
    return img


def load_animation(path, start, end, factor, size=96):
    """
    Loops through several images' path, loads them up, resizes them
    and then appends them to a list
    Returns:
        A list of resized images
    """
    resize = int(size * factor)
    img_list = []
    for i in range(start, end):
        img = pg.transform.smoothscale(pg.image.load(
            path.format(str(i))), (resize, resize))
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
        self.sfx = pg.mixer.Sound('sfx/laserfire01.ogg')
        self.image = self.motion[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]
        self.mask = pg.mask.from_surface(self.image)
        self.speed = PLAYER_SPEED
        self.health = 10
        self.shield = False  # todo crear propia clase para shield?
        self.kills = 0

    def update(self, keys):
        self.rect.clamp_ip(self.screen_rect)  # Prevents it from moving outside the screen
        self.image = self.motion[self.index]
        if self.index < len(self.motion) - 1:
            self.index += 1
        else:
            self.index = 0

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
        self.radius = (self.rect[2] // 2)  # Approx. radius
        self.mask = pg.mask.from_surface(self.image)
        self.speed = random.randrange(3, 6)
        self.vel_x = 0
        self.vel_y = 0
        self.health = 2
        self.timer = random.randrange(70)

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
