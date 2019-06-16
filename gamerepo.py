import pygame

BLACK = [0, 0, 0]
WHITE = [255, 255, 255]
RED = [255, 0, 0]
GREEN = [0, 255, 0]
BLUE = [0, 0, 255]
YELLOW = [255, 255, 0]
BROWN = [128, 0, 0]
PURPLE = [128, 0, 128]
GRAY = [128, 128, 128]


class Player(pygame.sprite.Sprite):
    """
    Clase jugador
    """

    def __init__(self, motion, position):
        pygame.sprite.Sprite.__init__(self)
        self.motion = motion
        self.index = 0
        self.image = self.motion[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = position[0]
        self.rect.y = position[1]
        self.vel_x = 0
        self.vel_y = 0

    def update(self):
        self.image = self.motion[self.index]
        if self.index < len(self.motion) - 1:
            self.index += 1
        else:
            self.index = 0
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

