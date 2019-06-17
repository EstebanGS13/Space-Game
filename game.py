import pygame as pg
import gamerepo as gp

SCREEN_WIDTH = 648
SCREEN_HEIGHT = 864

if __name__ == '__main__':
    pg.init()
    screen = pg.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
    screen_rect = screen.get_rect()
    pg.display.flip()
    clock = pg.time.Clock()
    run = True
    player_speed = 5
    laser_speed = 7

    # GROUPS
    players = pg.sprite.Group()
    lasers = pg.sprite.Group()

    # Player data
    player_laser = pg.transform.smoothscale(pg.image.load(
        'images/player/laser.png'), (24, 24))
    player_ship = []
    for i in range(1, 9):
        img = pg.transform.smoothscale(pg.image.load(
            'images/player/{0}.png'.format(str(i))), (96, 96))
        player_ship.append(img)
    player = gp.Player(screen_rect, player_ship,
                       [screen_rect.centerx - 96/2, SCREEN_HEIGHT])
    players.add(player)


    while run:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    run = False
                if event.key == pg.K_SPACE:
                    laser = gp.Laser(player_laser, -laser_speed,
                                     [player.rect.centerx, player.rect.y])
                    lasers.add(laser)
            if event.type == pg.KEYUP:
                player.vel_x = 0
                player.vel_y = 0

        keys = pg.key.get_pressed()




        players.update(keys)
        lasers.update()
        screen.fill(gp.BLACK)

        lasers.draw(screen)
        players.draw(screen)

        pg.display.flip()
        clock.tick(40)
