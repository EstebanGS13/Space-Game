import pygame as pg
import gamerepo as gp

SCREEN_WIDTH = 648
SCREEN_HEIGHT = 864

if __name__ == '__main__':
    pg.init()
    screen = pg.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
    pg.display.flip()
    clock = pg.time.Clock()
    run = True
    player_speed = 7

    # GROUPS
    players = pg.sprite.Group()

    ship_sprites = [] # todo usar matriz de sprites
    for i in range(1, 9):
        img = pg.transform.smoothscale(pg.image.load('images/{0}.png'.format(str(i))), (96, 96))
        ship_sprites.append(img)

    player = gp.Player(ship_sprites, [300, 300])
    players.add(player)

    while run:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    run = False
            if event.type == pg.KEYUP:
                player.vel_x = 0
                player.vel_y = 0

        keys = pg.key.get_pressed()

        if keys[pg.K_RIGHT]:
            player.vel_x = player_speed
            player.vel_y = 0
        if keys[pg.K_RIGHT] and keys[pg.K_SPACE]:
            player.vel_x = player_speed
            player.vel_y = 0

        if keys[pg.K_LEFT]:
            player.vel_x = -player_speed
            player.vel_y = 0
        if keys[pg.K_LEFT] and keys[pg.K_SPACE]:
            player.vel_x = -player_speed
            player.vel_y = 0

        if keys[pg.K_DOWN]:
            player.vel_x = 0
            player.vel_y = player_speed
        if keys[pg.K_DOWN] and keys[pg.K_SPACE]:
            player.vel_x = 0
            player.vel_y = player_speed

        if keys[pg.K_UP]:
            player.vel_x = 0
            player.vel_y = -player_speed
        if keys[pg.K_UP] and keys[pg.K_SPACE]:
            player.vel_x = 0
            player.vel_y = -player_speed

        if keys[pg.K_SPACE]:
            print("solo dispara")
        if keys[pg.K_LEFT] and keys[pg.K_RIGHT]:
            player.vel_x = 0
            player.vel_y = 0


        players.update()
        screen.fill(gp.BLACK)

        players.draw(screen)

        pg.display.flip()
        clock.tick(40)
