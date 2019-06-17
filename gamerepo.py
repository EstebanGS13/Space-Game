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
        self.speed = 5

    def update(self, keys):
        self.rect.clamp_ip(self.screen_rect)    # Prevents it from moving outside the screen
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
        # self.screen_rect = screen_rect
        self.motion = motion
        self.index = 0
        self.image = self.motion[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]
        self.speed = 4
        self.vel_x = 0
        self.vel_y = self.speed

    def update(self):
        self.image = self.motion[self.index]
        if self.index < len(self.motion) - 1:
            self.index += 1
        else:
            self.index = 0

        # Movement
        self.rect.y += self.vel_y


class Laser(pg.sprite.Sprite):
    
    def __init__(self, img, vel, position):
        pg.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = position[0] - self.rect.centerx   # Puts the laser at the top center
        self.rect.y = position[1]
        self.vel = vel

    def update(self):
        self.rect.y += self.vel
