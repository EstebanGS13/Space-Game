import pygame as pg
import gamerepo as gr
import random


if __name__ == '__main__':
    pg.init()
    screen = pg.display.set_mode([gr.SCREEN_WIDTH, gr.SCREEN_HEIGHT])
    screen_rect = screen.get_rect()  # <rect(0, 0, 648, 864)>
    pg.display.flip()
    bg = pg.image.load('background/corona_up.png')
    run = True
    clock = pg.time.Clock()
    frames = 20
    size = 96  # Ship's sprite size
    laser_speed = 7
    bottom_center = [screen_rect.centerx - size / 2, gr.SCREEN_HEIGHT - size]
    previous = bottom_center[0]  # Previous player's pos

    # Load animations
    player_ship = gr.load_animation('images/player/{0}.png', 1, 9, 1)
    enemy_ship = gr.load_animation('images/enemy/{0}.png', 1, 9, 1)
    laser_hit_explosion = gr.load_animation('images/effects/laser/{0}.png', 1, 18, 1 / 2)
    red_blast = gr.load_animation('images/effects/red/1_{0}.png', 0, 17, 7 / 6)
    # warp = gr.load_animation('images/effects/warp/{0}.png', 1, 10, 1/2, 320)

    # Load images
    player_laser = gr.load_image('images/player/laser.png', 1 / 4)
    enemy_laser = gr.load_image('images/enemy/laser.png', 1 / 4)

    # GROUPS
    players = pg.sprite.Group()
    lasers = pg.sprite.Group()
    enemies = pg.sprite.Group()
    enemies_lasers = pg.sprite.Group()
    explosions = pg.sprite.Group()

    # Player data
    player = gr.Player(screen_rect, player_ship, bottom_center)  # Player centered at the bottom
    players.add(player)

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
                    player.sfx.play()
                    lasers.add(laser)
            if event.type == pg.KEYUP:
                player.vel_x = 0
                player.vel_y = 0

        # Enemies control
        if len(enemies) < 5:  # todo cambiar cantidad conforme pasa el tiempo
            start_state = gr.generate_start_state()
            enemy = gr.Enemy(enemy_ship, start_state[0])
            enemy.vel_x = start_state[1][0]
            enemy.vel_y = start_state[1][1]
            enemies.add(enemy)

        for e in enemies:
            if e.rect.y > (gr.SCREEN_HEIGHT * 2 / 3) - size:
                # Changes enemy vel when it reaches 2/3 of the screen
                e.vel_y = -e.speed
                e.dice()
            if (e.rect.y < 0) and (e.vel_y < 0):
                # Changes enemy vel before it leaves the screen
                e.vel_y = e.speed
                e.dice()
            if (e.rect.x < 0) and (e.vel_x < 0):
                e.vel_x = e.speed
                e.dice()
            if (e.rect.x > gr.SCREEN_WIDTH - size) and (e.vel_x > 0):
                e.vel_x = -e.speed
                e.dice()

            enemy_collide = pg.sprite.spritecollide(e, enemies, False,
                                                    pg.sprite.collide_circle)
            for e2 in enemy_collide:
                if e != e2:
                    e.dice()
                    e2.dice()

            if e.timer == 0:
                # Create enemy's lasers
                e_laser = gr.Laser(enemy_laser, laser_speed,
                                   [e.rect.centerx, e.rect.centery + size / 4])
                enemies_lasers.add(e_laser)
                e.timer = random.randrange(70)

        # Player's lasers control
        for l in lasers:
            if l.rect.y < -l.rect.height:
                # Deletes the laser when it reaches the end of the screen
                lasers.remove(l)

            # Collision with enemies
            lasers_hits = pg.sprite.spritecollide(l, enemies, False,
                                                  pg.sprite.collide_mask)
            for enemy in lasers_hits:
                pos_l = l.rect.center
                lasers.remove(l)  # Delete blue laser when it hits
                # Create explosion when blue laser hits
                explosion = gr.Explosion(laser_hit_explosion, pos_l)
                explosions.add(explosion)
                if enemy.health == 0:
                    pos_e = enemy.rect.center
                    enemies.remove(enemy)
                    explosion = gr.Explosion(red_blast, pos_e)
                    explosions.add(explosion)
                else:
                    enemy.health -= 1

        # Enemies' lasers control
        for l in enemies_lasers:
            if l.rect.y > gr.SCREEN_HEIGHT:
                # Delete enemies' lasers when they leave the screen
                enemies_lasers.remove(l)

            enemy_lasers_hits = pg.sprite.spritecollide(l, players, False,
                                                        pg.sprite.collide_mask)
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
        for ex in explosions:
            if ex.index == (len(ex.motion) - 1):
                # Delete the explosion when animation is over
                explosions.remove(ex)

        # Update
        players.update(keys)
        lasers.update()
        enemies.update(previous)
        enemies_lasers.update()
        explosions.update()

        previous = player.rect.centerx  # Updates previous player's pos

        # Draw
        screen.blit(bg, screen_rect)  # todo mostrar correctamente
        # screen.fill(gr.BLACK)
        players.draw(screen)
        lasers.draw(screen)
        enemies.draw(screen)
        enemies_lasers.draw(screen)
        explosions.draw(screen)
        pg.display.flip()
        clock.tick(frames)

        # print(pg.time.get_ticks())
