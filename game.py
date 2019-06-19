import pygame as pg
import gamerepo as gr
import random

SCREEN_WIDTH = 648
SCREEN_HEIGHT = 864 - 150  # Changed for test purposes

if __name__ == '__main__':
    pg.init()
    screen = pg.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
    screen_rect = screen.get_rect()  # <rect(0, 0, 648, 864)>
    pg.display.flip()
    run = True
    clock = pg.time.Clock()
    frames = 20
    size = 96  # Ship's sprite size
    laser_speed = 7
    bottom_center = [screen_rect.centerx - size / 2, SCREEN_HEIGHT - size]
    previous = bottom_center[0]  # Previous player's pos

    # GROUPS
    players = pg.sprite.Group()
    lasers = pg.sprite.Group()
    enemies = pg.sprite.Group()
    enemies_lasers = pg.sprite.Group()
    explosions = pg.sprite.Group()

    # Player data
    player_laser = pg.transform.smoothscale(pg.image.load(
        'images/player/laser.png'), (size // 4, size // 4))
    player_ship = []
    for i in range(1, 9):
        img_player = pg.transform.smoothscale(pg.image.load(
            'images/player/{0}.png'.format(str(i))), (size, size))
        player_ship.append(img_player)
    player = gr.Player(screen_rect, player_ship, bottom_center)  # Player centered at the bottom
    players.add(player)

    # Enemy data
    enemy_laser = pg.transform.smoothscale(pg.image.load(
        'images/enemy/laser.png'), (size // 4, size // 4))
    enemy_ship = []
    for i in range(1, 9):
        img_enemy = pg.transform.smoothscale(pg.image.load(
            'images/enemy/{0}.png'.format(str(i))), (size, size))
        enemy_ship.append(img_enemy)

    # Effects data
    laser_hit_explosion = []
    for i in range(1, 18):
        img_hit = pg.transform.smoothscale(pg.image.load(
            'images/effects/{0}.png'.format(str(i))), (size // 2, size // 2))
        laser_hit_explosion.append(img_hit)

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

            if e.timer == 0:
                # Create enemy's lasers
                e_laser = gr.Laser(enemy_laser, laser_speed,
                                   [e.rect.centerx, e.rect.y + size])
                enemies_lasers.add(e_laser)
                e.timer = random.randrange(70)

        # Player's lasers control
        for l in lasers:
            if l.rect.y < -l.rect.height:
                # Deletes the laser when it reaches the end of the screen
                lasers.remove(l)

            # Collision with enemies
            lasers_hits = pg.sprite.spritecollide(l, enemies, False,
                                                  pg.sprite.collide_circle)
            for enemy in lasers_hits:
                pos_l = l.rect.center
                lasers.remove(l)  # Delete blue laser when it hits
                # Create explosion when blue laser hits
                explosion = gr.Explosion(laser_hit_explosion, pos_l)
                explosions.add(explosion)
                if enemy.health == 0:
                    pos_e = enemy.rect.center
                    enemies.remove(enemy)
                    # todo agregar RED BLAST
                    # explosion = gr.Explosion(laser_hit_explosion, pos_e)
                    # explosions.add(explosion)
                else:
                    enemy.health -= 1

        # Enemies' lasers control
        for l in enemies_lasers:
            if l.rect.y > screen_rect[3]:
                # Delete enemies' lasers when they leave the screen
                enemies_lasers.remove(l)

            enemy_lasers_hits = pg.sprite.spritecollide(l, players, False,
                                                        pg.sprite.collide_circle)
            for p in enemy_lasers_hits:
                pos_l = l.rect.center
                enemies_lasers.remove(l)  # Delete red lasers that hit
                # Create explosion when blue laser hits
                explosion = gr.Explosion(laser_hit_explosion, pos_l)
                explosions.add(explosion)

                # todo implementar cuando tenga vida el jugador
                # if p.health == 0:
                #     pos = p.rect.center
                #     players.remove(p)
                #     explosion = gr.Explosion(effects_matrix[2], pos)
                #     explosions.add(explosion)
                # else:
                #     p.health -= 1

        # Lasers' hits explosion control
        for h in explosions:
            if h.index == (len(laser_hit_explosion) - 1):
                # Delete the explosion when animation is over
                explosions.remove(h)

        # Update
        players.update(keys)
        lasers.update()
        enemies.update(previous)
        enemies_lasers.update()
        explosions.update()

        previous = player.rect.centerx  # Updates previous player's pos

        # Draw
        screen.fill(gr.BLACK)
        players.draw(screen)
        lasers.draw(screen)
        enemies.draw(screen)
        enemies_lasers.draw(screen)
        explosions.draw(screen)

        pg.display.flip()
        clock.tick(frames)

        # print(pg.time.get_ticks())
