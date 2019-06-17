import pygame as pg

BLACK = [0, 0, 0]
WHITE = [255, 255, 255]
RED = [255, 0, 0]
GREEN = [0, 255, 0]
BLUE = [0, 0, 255]
YELLOW = [255, 255, 0]
BROWN = [128, 0, 0]
PURPLE = [128, 0, 128]
GRAY = [128, 128, 128]


class Player(pg.sprite.Sprite):
    """
    Clase jugador
    """

    def __init__(self, screen_rect, motion, position):
        pg.sprite.Sprite.__init__(self)
        self.screen_rect = screen_rect
        self.motion = motion
        self.index = 0
        self.image = self.motion[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]
        self.speed = 7
        # self.vel_x = 0
        # self.vel_y = 0

    def update(self, keys):
        self.rect.clamp_ip(self.screen_rect)    # Prevents it from moving outside the screen
        self.image = self.motion[self.index]
        if self.index < len(self.motion) - 1:
            self.index += 1
        else:
            self.index = 0

        if keys[pg.K_LEFT]:
            self.rect.x -= self.speed
        elif keys[pg.K_RIGHT]:
            self.rect.x += self.speed
        elif keys[pg.K_UP]:
            self.rect.y -= self.speed
        elif keys[pg.K_DOWN]:
            self.rect.y += self.speed

        #
        # self.rect.x += self.vel_x
        # self.rect.y += self.vel_y


class Laser(pg.sprite.Sprite):
    
    def __init__(self, img, vel, position):
        pg.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.x = position[0] - self.rect.centerx
        self.rect.y = position[1]
        self.vel = vel

    def update(self):
        self.rect.y += self.vel

    
