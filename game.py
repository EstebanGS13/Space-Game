from gamerepo import *


if __name__ == '__main__':
    pg.init()
    screen = pg.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT + UI])
    screen_rect = screen.get_rect(height=SCREEN_HEIGHT)  # <rect(0, 0, 648, 864)>
    ui_rect = screen.get_rect(y=SCREEN_HEIGHT, height=UI)
    print(screen_rect, ui_rect)
    pg.display.flip()
    bg = pg.image.load('background/corona_up.png')
    run = True
    clock = pg.time.Clock()
    frames = 20
    size = 96  # Base size for sprites
    laser_speed = 7
    bottom_center = [screen_rect.centerx - size / 2, SCREEN_HEIGHT - size]

    # Load animations
    player_ship = load_animation('images/player/{0}.png', 1, 9)
    enemy_ship = load_animation('images/enemy/{0}.png', 1, 9)
    laser_hit_explosion = load_animation('images/effects/laser/{0}.png', 1, 18, 1 / 2, 1 / 2)
    red_blast = load_animation('images/effects/red/1_{0}.png', 0, 17, 7 / 6, 7 / 6)
    blue_blast = load_animation('images/effects/blue/1_{0}.png', 0, 17, 7 / 6, 7 / 6)
    # warp = load_animation('images/effects/warp/{0}.png', 1, 10, 1/2, 320)
    health_bar = load_animation('images/ui/health/VIDA_{0}.png', 0, 11, 1 / 2, 1 / 2, 378, 38)

    # Load images
    player_laser = load_image('images/player/laser.png', 1 / 4)
    enemy_laser = load_image('images/enemy/laser.png', 1 / 4)
    healing = load_image('images/mod/heal.png', 1, 36)
    shield_upgrade = load_image('images/mod/shield_upgrade.png', 1, 36)
    shield_img = load_image('images/player/shield.png')

    # GROUPS
    players = pg.sprite.Group()
    lasers = pg.sprite.Group()
    enemies = pg.sprite.Group()
    enemies_lasers = pg.sprite.Group()
    explosions = pg.sprite.Group()
    health_kits = pg.sprite.Group()
    shields = pg.sprite.Group()

    # Player data
    player = Player(screen_rect, player_ship, bottom_center)  # Player centered at the bottom
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
                    if players:  # If player is not dead
                        laser = Laser(player_laser, -laser_speed,
                                      [player.rect.centerx - 2, player.rect.y])
                        player.sfx.play()
                        lasers.add(laser)
            if event.type == pg.KEYUP:
                player.vel_x = 0
                player.vel_y = 0

        # Enemies control
        if len(enemies) < 5:  # todo cambiar cantidad conforme pasa el tiempo
            start_state = generate_start_state()
            enemy = Enemy(enemy_ship, start_state[0])
            enemy.vel_x = start_state[1][0]
            enemy.vel_y = start_state[1][1]
            enemies.add(enemy)

        for e in enemies:
            if e.rect.y > (SCREEN_HEIGHT * 2 / 3) - size:
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
            if (e.rect.x > SCREEN_WIDTH - size) and (e.vel_x > 0):
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
                e_laser = Laser(enemy_laser, laser_speed,
                                [e.rect.centerx, e.rect.centery + size / 4])
                enemies_lasers.add(e_laser)
                e.timer = random.randrange(70)

        # Player's lasers control
        for l in lasers:
            if l.rect.y < -l.rect.height:
                # Deletes the laser when it reaches the end of the screen
                lasers.remove(l)

            # Collision lasers with enemies
            lasers_hits = pg.sprite.spritecollide(l, enemies, False,
                                                  pg.sprite.collide_mask)
            for enemy in lasers_hits:
                pos_l = l.rect.center
                lasers.remove(l)  # Delete blue laser when it hits
                # Create explosion when blue laser hits
                explosion = Explosion(laser_hit_explosion, pos_l)
                explosions.add(explosion)
                if enemy.health == 0:
                    pos_e = enemy.rect.center
                    enemies.remove(enemy)
                    explosion = Explosion(red_blast, pos_e)
                    explosions.add(explosion)
                    player.kills += 1

                    value = random.randrange(100)
                    if value < 20:
                        # Drop health kit
                        aid = Aid(healing, pos_e)
                        health_kits.add(aid)
                    elif value > 95:
                        # Drop shield upgrade
                        shield = Aid(shield_upgrade, pos_e)
                        shields.add(shield)
                else:
                    enemy.health -= 1

        # Health Kit's control
        for a in health_kits:
            if a.rect.y > SCREEN_HEIGHT:
                health_kits.remove(a)

        # Collision player with health kits
        health_collide = pg.sprite.spritecollide(player, health_kits, True,
                                                 pg.sprite.collide_mask)
        for h in health_collide:
            if player.health < 10:
                player.health += 1

        # Shield's control
        for s in shields:
            if s.rect.y > SCREEN_HEIGHT:
                shields.remove(s)

        # Collision player with shield upgrades
        shield_collide = pg.sprite.spritecollide(player, shields, True,
                                                 pg.sprite.collide_mask)
        for a in shield_collide:
            if player.health < 10:
                player.shield = True

        # Enemies' lasers control
        for l in enemies_lasers:
            if l.rect.y > SCREEN_HEIGHT:
                # Delete enemies' lasers when they leave the screen
                enemies_lasers.remove(l)

            enemy_lasers_hits = pg.sprite.spritecollide(l, players, False,
                                                        pg.sprite.collide_mask)
            for p in enemy_lasers_hits:
                pos_l = l.rect.center
                enemies_lasers.remove(l)  # Delete red lasers that hit
                # Create explosion when red laser hits
                explosion = Explosion(laser_hit_explosion, pos_l)
                explosions.add(explosion)

                # Reduce player's health
                if p.health == 1:
                    pos_p = p.rect.center
                    players.remove(p)  # todo implementar delay cuando muere
                    explosion = Explosion(blue_blast, pos_p)
                    explosions.add(explosion)
                p.health -= 1

        # Lasers' hits explosion control
        for ex in explosions:
            if ex.index == (len(ex.motion) - 1):
                # Delete the explosion when animation is over
                explosions.remove(ex)

        # Update
        players.update(keys)
        lasers.update()
        enemies.update()
        enemies_lasers.update()
        explosions.update()
        health_kits.update()
        shields.update()

        # Draw
        screen.blit(bg, screen_rect)  # todo mostrar correctamente

        players.draw(screen)
        lasers.draw(screen)
        enemies.draw(screen)
        enemies_lasers.draw(screen)
        explosions.draw(screen)
        health_kits.draw(screen)
        shields.draw(screen)
        screen.blit(shield_img, [300, 400])
        screen.fill(BLACK, ui_rect)  # Fills UI section with black

        screen.blit(health_bar[player.health], ui_rect)


        pg.display.flip()
        clock.tick(frames)

        # print(pg.time.get_ticks())
