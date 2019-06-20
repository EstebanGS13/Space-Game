import pygame as pg
import random

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


def generate_enemy_pos(x_range, size, y_range):
    """
    Generates a random position to create
    the enemies above the screen
    """
    x = random.randrange(x_range)
    y = random.randrange(size, y_range)
    return [x, -y]


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
        self.radius = (self.rect[2] // 2) - 15
        self.speed = PLAYER_SPEED

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
        self.radius = (self.rect[2] // 2) - 6  # Approx. radius
        self.speed = random.randrange(3, 6)
        self.vel_x = 1
        self.vel_y = self.speed
        self.health = 2
        self.timer = random.randrange(70)

    def update(self, player_pos):
        self.image = self.motion[self.index]
        if self.index < len(self.motion) - 1:
            self.index += 1
        else:
            self.index = 0

        # Movement
        if self.rect.centerx < player_pos:
            self.rect.x += self.vel_x
        else:
            self.rect.x -= self.vel_x
        self.rect.y += self.vel_y
        self.timer -= 1


class Laser(pg.sprite.Sprite):

    def __init__(self, img, vel, position):
        pg.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = position[0] - self.rect.centerx  # Puts the laser at the top center
        self.rect.y = position[1]
        self.radius = self.rect[2] // 2
        self.vel = vel

    def update(self):
        self.rect.y += self.vel


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
