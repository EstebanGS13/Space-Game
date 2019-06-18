import pygame as pg
import gamerepo as gr

SCREEN_WIDTH = 648
SCREEN_HEIGHT = 864

if __name__ == '__main__':
    pg.init()
    screen = pg.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
    screen_rect = screen.get_rect()
    pg.display.flip()
    run = True
    clock = pg.time.Clock()
    frames = 20
    size = 96  # Ship's sprite size
    laser_speed = 7

    # GROUPS
    players = pg.sprite.Group()
    lasers = pg.sprite.Group()
    enemies = pg.sprite.Group()
    enemies_lasers = pg.sprite.Group()
    explosions = pg.sprite.Group()

    # Player data
    player_laser = pg.transform.smoothscale(pg.image.load(
        'images/player/laser.png'), (24, 24))
    player_ship = []
    for i in range(1, 9):
        img_player = pg.transform.smoothscale(pg.image.load(
            'images/player/{0}.png'.format(str(i))), (size, size))
        player_ship.append(img_player)
    player = gr.Player(screen_rect, player_ship,
                       [screen_rect.centerx - size / 2, SCREEN_HEIGHT - size])  # Player centered at the bottom
    players.add(player)

    # Enemy data
    enemy_laser = pg.transform.smoothscale(pg.image.load(
        'images/enemy/laser.png'), (24, 24))
    enemy_ship = []
    for i in range(1, 9):
        img_enemy = pg.transform.smoothscale(pg.image.load(
            'images/enemy/{0}.png'.format(str(i))), (size, size))
        enemy_ship.append(img_enemy)

    # Effects data
    # todo testear con singular
    img_effects = pg.transform.smoothscale(pg.image.load(
        'images/effects/effects_256x256.png'), (size * 8, size * 2))  # todo hacer la explosion mas grande
    effects_matrix = gr.sprites_matrix(img_effects, size // 2, size // 2)

    while run:
        keys = pg.key.get_pressed()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    run = False
                if event.key == pg.K_SPACE:
                    laser = gr.Laser(player_laser, -laser_speed,
                                     [player.rect.centerx, player.rect.y])
                    lasers.add(laser)
            if event.type == pg.KEYUP:
                player.vel_x = 0
                player.vel_y = 0

        # Enemies control
        if len(enemies) < 5:
            pos = gr.generate_enemy_pos(SCREEN_WIDTH, size, size * 3)
            enemy = gr.Enemy(enemy_ship, pos)
            enemies.add(enemy)

        for e in enemies:
            if e.rect.y > (SCREEN_HEIGHT * 2 / 3) - size:
                # Changes enemy vel when it reaches 2/3 of the screen
                e.vel_y = -e.speed
            elif (e.rect.y < 0) and (e.vel_y < 0):
                # Changes enemy vel before it leaves the screen
                e.vel_y = e.speed

        # Player's lasers control
        for l in lasers:
            if l.rect.y < -l.rect.height:
                # Deletes the laser when it reaches the end of the screen
                lasers.remove(l)

            lasers_hits = pg.sprite.spritecollide(l, enemies, False,
                                                  pg.sprite.collide_circle)
            for enemy in lasers_hits:
                lasers.remove(l)
                if enemy.health == 0:
                    pos = enemy.rect.center
                    enemies.remove(enemy)
                    explosion = gr.Explosion(effects_matrix[2], pos)
                    explosions.add(explosion)
                else:
                    enemy.health -= 1

        # Update
        players.update(keys)
        lasers.update()
        enemies.update()
        explosions.update()

        # Draw
        screen.fill(gr.BLACK)
        players.draw(screen)
        lasers.draw(screen)
        enemies.draw(screen)
        explosions.draw(screen)

        pg.display.flip()
        clock.tick(frames)

        # print(pg.time.get_ticks())
