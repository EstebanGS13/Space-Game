from moviepy.editor import VideoFileClip
from gamerepo import *
import os

os.environ['SDL_VIDEO_CENTERED'] = '0'

if __name__ == '__main__':
    pg.init()
    pg.display.set_caption('HellStar')

    clip = VideoFileClip('multimedia/v1.mp4')
    clip.preview()

    bg_music = pg.mixer.Sound('multimedia/Lava Hellfire.ogg')
    screen = pg.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT + UI])
    screen_rect = screen.get_rect(height=SCREEN_HEIGHT)  # <rect(0, 0, 648, 864)>
    ui_rect = screen.get_rect(y=SCREEN_HEIGHT, height=UI)

    print(screen_rect, ui_rect)
    pg.display.flip()
    run_lv1 = True
    pass_lv1 = False
    run_lv2 = False
    delay_over = False
    clock = pg.time.Clock()
    current_time = pg.time.get_ticks()
    frames = 20
    game_font = pg.font.Font(None, 24)

    size = 96  # Base size for sprites
    laser_speed = 7
    bottom_center = [screen_rect.centerx - size / 2, SCREEN_HEIGHT - size]

    # Load animations
    player_ship = load_animation('images/player/{0}.png', 1, 9)
    enemy_ship = load_animation('images/enemy/lv1/{0}.png', 1, 9)
    laser_hit_explosion = load_animation('images/effects/laser/{0}.png', 1, 18, 1 / 2, 1 / 2)
    red_blast = load_animation('images/effects/red/1_{0}.png', 0, 17, 7 / 6, 7 / 6)
    blue_blast = load_animation('images/effects/blue/1_{0}.png', 0, 17, 7 / 6, 7 / 6)
    # warp = load_animation('images/effects/warp/{0}.png', 1, 10, 1/2, 320)
    health_bar_img = load_animation('images/ui/health/VIDA_{0}.png', 0, 11, 1 / 2, 1 / 2, 378, 38)

    # Load images
    bg_1 = pg.image.load('images/background/bg1.png')
    bg_2 = pg.image.load('images/background/bg2.png')
    player_laser = load_image('images/player/laser.png', 1 / 4)
    enemy_laser = load_image('images/enemy/laser.png', 1 / 4)
    healing = load_image('images/mod/heal.png', 1, 36)
    shield_upgrade = load_image('images/mod/shield_upgrade.png', 1, 36)
    shield_ui = load_image('images/mod/shield_upgrade.png', 1, 28)
    shield_img = load_image('images/player/shield.png')
    diagonal_upg = load_image('images/mod/atom/p_Sprite_0.png', 1)

    # GROUPS
    players = pg.sprite.Group()
    lasers = pg.sprite.Group()
    enemies = pg.sprite.Group()
    enemies_lasers = pg.sprite.Group()
    explosions = pg.sprite.Group()
    health_kits = pg.sprite.Group()
    shield_kits = pg.sprite.Group()
    shields = pg.sprite.Group()
    backgrounds = pg.sprite.Group()
    ui_stuff = pg.sprite.Group()

    # Player data
    player = Player(screen_rect, player_ship, bottom_center)  # Player centered at the bottom
    players.add(player)
    player_shield = Shield(shield_img, player.rect.center)
    shields.add(player_shield)
    background_1 = Background(bg_1)
    backgrounds.add(background_1)
    health_bar = HealthBar(health_bar_img, ui_rect.center)
    ui_stuff.add(health_bar)

    bg_music.play(-1)

    while run_lv1 and not delay_over:
        keys = pg.key.get_pressed()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                run_lv1 = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    run_lv1 = False
                if event.key == pg.K_SPACE:
                    if players:  # If player is not dead
                        laser = Laser(player_laser, -laser_speed,
                                      [player.rect.centerx - 2, player.rect.y])
                        player.sfx_laser.play()
                        lasers.add(laser)
            if event.type == pg.KEYUP:
                player.vel_x = 0
                player.vel_y = 0

        # Enemies control
        if len(enemies) < 3:  # todo cambiar cantidad conforme pasa el tiempo
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
                    # e.dice()
                    e2.dice()

            if e.timer == 0:
                # Create enemy's lasers
                e_laser = Laser(enemy_laser, laser_speed,
                                [e.rect.centerx, e.rect.centery + size / 4])
                enemies_lasers.add(e_laser)
                e.timer = random.randrange(50)

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
                player.sfx_impact_enemy.play()
                if enemy.health == 0:
                    pos_e = enemy.rect.center
                    enemies.remove(enemy)
                    explosion = Explosion(red_blast, pos_e)
                    explosions.add(explosion)
                    player.sfx_kill.play()
                    player.score += KILL_POINTS
                    player.kills += 1

                    value = random.randrange(100)
                    if value < HEAL_DROP_RATIO:
                        # Drop health kit
                        aid = Aid(healing, pos_e)
                        health_kits.add(aid)
                    elif value > SHIELD_DROP_RATIO:
                        # Drop shield upgrade
                        shield = Aid(shield_upgrade, pos_e)
                        shield_kits.add(shield)
                else:
                    enemy.health -= 1
                    player.score += HIT_POINTS

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
                player.sfx_health.play()

        # Shield's upgrades control
        for s in shield_kits:
            if s.rect.y > SCREEN_HEIGHT:
                shield_kits.remove(s)

        # Collision player with shield upgrades
        shield_collide = pg.sprite.spritecollide(player, shield_kits, True,
                                                 pg.sprite.collide_mask)
        for s_upg in shield_collide:
            player.shield = True
            player_shield.active = True
            player.sfx_shield.play()
            player_shield.start = pg.time.get_ticks()

        # Enemies' lasers control
        for l in enemies_lasers:
            if l.rect.y > SCREEN_HEIGHT:
                # Delete enemies' lasers when they leave the screen
                enemies_lasers.remove(l)

            if player.shield:
                # Enemies' lasers collide with shield instead
                enemy_lasers_hits = pg.sprite.spritecollide(l, shields, False,
                                                            pg.sprite.collide_circle)
                for s in enemy_lasers_hits:
                    pos_l = l.rect.center
                    enemies_lasers.remove(l)  # Delete red lasers that hit
                    # Create explosion when red laser hits
                    explosion = Explosion(laser_hit_explosion, pos_l)
                    explosions.add(explosion)
                    player.sfx_take_dmg.play()

            else:
                enemy_lasers_hits = pg.sprite.spritecollide(l, players, False,
                                                            pg.sprite.collide_mask)
                for p in enemy_lasers_hits:
                    pos_l = l.rect.center
                    enemies_lasers.remove(l)  # Delete red lasers that hit
                    # Create explosion when red laser hits
                    explosion = Explosion(laser_hit_explosion, pos_l)
                    explosions.add(explosion)
                    player.sfx_take_dmg.play()

                    # Reduce player's health
                    if p.health == 1:
                        pos_p = p.rect.center
                        player.dead = True
                        p.sfx_death.play()
                        players.remove(player)
                        start_time = pg.time.get_ticks()
                        explosion = Explosion(blue_blast, pos_p)
                        explosions.add(explosion)
                    p.health -= 1
                    p.score -= TAKE_DAMAGE

        # Lasers' hits explosion control
        for ex in explosions:
            if ex.index == (len(ex.motion) - 1):
                # Delete the explosion when animation is over
                explosions.remove(ex)

        # Update
        backgrounds.update()
        players.update(keys)
        if player.shield:
            shields.update(player, pg.time.get_ticks())
        lasers.update()
        enemies.update()
        enemies_lasers.update()
        explosions.update()
        health_kits.update()
        shield_kits.update()
        health_bar.update(player.health)

        # Draw

        backgrounds.draw(screen)

        players.draw(screen)
        if player.shield:
            shields.draw(screen)
        lasers.draw(screen)
        enemies.draw(screen)
        enemies_lasers.draw(screen)
        explosions.draw(screen)
        health_kits.draw(screen)
        shield_kits.draw(screen)

        # UI section
        screen.fill(BLACK, ui_rect)  # Fills UI section with black
        ui_stuff.draw(screen)

        # Text info
        if player.shield:
            shield_str = str(int(player_shield.remain_time / 1000)) + " s"
            shield_txt = game_font.render(shield_str, True, WHITE, BLACK)
            screen.blit(shield_ui, [ui_rect.centerx * 4 / 3, ui_rect.y - 8])
            screen.blit(shield_txt, [ui_rect.centerx * 4 / 3 + 30, ui_rect.y])
        score_str = "Score: " + str(player.score)
        kills_str = "Kills: " + str(player.kills)
        score_text = game_font.render(score_str, True, WHITE, BLACK)
        kills_text = game_font.render(kills_str, True, WHITE, BLACK)
        screen.blit(kills_text, ui_rect)
        screen.blit(score_text, [ui_rect.centerx / 3, ui_rect.y])

        pg.display.flip()
        clock.tick(frames)

        # Delay handling
        if background_1.rect.y >= 0 and not player.dead:
            run_lv1 = False  # todo poner delay
            pass_lv1 = True
            run_lv2 = True
        if not players:
            if current_time - start_time > 5000:
                # run_lv1 = False
                delay_over = True
        current_time = pg.time.get_ticks()
        # if current_time - start_time > 5000:
        #     delay_over = True

    # Clean groups
    backgrounds.empty()
    lasers.empty()
    enemies.empty()
    enemies_lasers.empty()
    explosions.empty()
    health_kits.empty()
    shield_kits.empty()

    background_2 = Background(bg_2)
    backgrounds.add(background_2)

    enemy_ship_2 = load_animation('images/enemy/lv2/{0}.png', 1, 4)
    enemies_2 = pg.sprite.Group()

    player.health = 10

    previous_pos = bottom_center[0]
    delay_over = False

    while run_lv2 and pass_lv1 and not delay_over:
        keys = pg.key.get_pressed()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                run_lv2 = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    run_lv2 = False
                if event.key == pg.K_SPACE:
                    if players:  # If player is not dead
                        laser = Laser(player_laser, -laser_speed,
                                      [player.rect.centerx - 2, player.rect.y])
                        player.sfx_laser.play()
                        lasers.add(laser)
            if event.type == pg.KEYUP:
                player.vel_x = 0
                player.vel_y = 0

        # Enemies control
        if len(enemies) < 3:
            start_state = generate_start_state()
            enemy = Enemy(enemy_ship, start_state[0])
            enemy.vel_x = start_state[1][0]
            enemy.vel_y = start_state[1][1]
            enemies.add(enemy)

        if len(enemies_2) < 2:
            pos = generate_enemy_pos(SCREEN_WIDTH, size, size * 3)
            enemy_2 = EnemyLvTwo(enemy_ship_2, pos)
            enemies_2.add(enemy_2)

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
                    # e.dice()
                    e2.dice()

            if e.timer == 0:
                # Create enemy's lasers
                e_laser = Laser(enemy_laser, laser_speed,
                                [e.rect.centerx, e.rect.centery + size / 4])
                enemies_lasers.add(e_laser)
                e.timer = random.randrange(50)

        for e_2 in enemies_2:
            if e_2.rect.y > (SCREEN_HEIGHT * 2 / 3) - size:
                # Changes enemy vel when it reaches 2/3 of the screen
                e_2.vel_y = -e_2.speed
            elif (e_2.rect.y < 0) and (e_2.vel_y < 0):
                # Changes enemy vel before it leaves the screen
                e_2.vel_y = e_2.speed

            if e_2.timer == 0:
                # Create enemy's lasers
                e_laser = Laser(enemy_laser, laser_speed,
                                [e_2.rect.centerx, e_2.rect.y + size])
                enemies_lasers.add(e_laser)
                e_2.timer = random.randrange(30)

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
                player.sfx_impact_enemy.play()
                if enemy.health == 0:
                    pos_e = enemy.rect.center
                    enemies.remove(enemy)
                    explosion = Explosion(red_blast, pos_e)
                    explosions.add(explosion)
                    player.sfx_kill.play()
                    player.score += KILL_POINTS
                    player.kills += 1

                    value = random.randrange(100)
                    if value < HEAL_DROP_RATIO:
                        # Drop health kit
                        aid = Aid(healing, pos_e)
                        health_kits.add(aid)
                    elif value > SHIELD_DROP_RATIO:
                        # Drop shield upgrade
                        shield = Aid(shield_upgrade, pos_e)
                        shield_kits.add(shield)
                else:
                    enemy.health -= 1
                    player.score += HIT_POINTS

            lasers_hits_2 = pg.sprite.spritecollide(l, enemies_2, False,
                                                    pg.sprite.collide_mask)
            for enemy_2 in lasers_hits_2:
                pos_l = l.rect.center
                lasers.remove(l)  # Delete blue laser when it hits
                # Create explosion when blue laser hits
                explosion = Explosion(laser_hit_explosion, pos_l)
                explosions.add(explosion)
                player.sfx_impact_enemy.play()
                if enemy_2.health == 0:
                    pos_e = enemy_2.rect.center
                    enemies_2.remove(enemy_2)
                    explosion = Explosion(red_blast, pos_e)
                    explosions.add(explosion)
                    player.sfx_kill.play()
                    player.score += KILL_POINTS
                    player.kills += 1

                    value_2 = random.randrange(100)
                    if value_2 < DIAGONAL_DROP_RATIO:
                        # Drop diagonal laser upgrade
                        aid_2 = Aid(diagonal_upg, pos_e)
                        health_kits.add(aid_2)
                        print("aniade")
                else:
                    enemy_2.health -= 1
                    player.score += HIT_POINTS

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
                player.sfx_health.play()

        # Shield's upgrades control
        for s in shield_kits:
            if s.rect.y > SCREEN_HEIGHT:
                shield_kits.remove(s)

        # Collision player with shield upgrades
        shield_collide = pg.sprite.spritecollide(player, shield_kits, True,
                                                 pg.sprite.collide_mask)
        for s_upg in shield_collide:
            player.shield = True
            player_shield.active = True
            player.sfx_shield.play()
            player_shield.start = pg.time.get_ticks()

        # Enemies' lasers control
        for l in enemies_lasers:
            if l.rect.y > SCREEN_HEIGHT:
                # Delete enemies' lasers when they leave the screen
                enemies_lasers.remove(l)

            if player.shield:
                # Enemies' lasers collide with shield instead
                enemy_lasers_hits = pg.sprite.spritecollide(l, shields, False,
                                                            pg.sprite.collide_circle)
                for s in enemy_lasers_hits:
                    pos_l = l.rect.center
                    enemies_lasers.remove(l)  # Delete red lasers that hit
                    # Create explosion when red laser hits
                    explosion = Explosion(laser_hit_explosion, pos_l)
                    explosions.add(explosion)
                    player.sfx_take_dmg.play()

            else:
                enemy_lasers_hits = pg.sprite.spritecollide(l, players, False,
                                                            pg.sprite.collide_mask)
                for p in enemy_lasers_hits:
                    pos_l = l.rect.center
                    enemies_lasers.remove(l)  # Delete red lasers that hit
                    # Create explosion when red laser hits
                    explosion = Explosion(laser_hit_explosion, pos_l)
                    explosions.add(explosion)
                    player.sfx_take_dmg.play()

                    # Reduce player's health
                    if p.health == 1:
                        pos_p = p.rect.center
                        player.dead = True
                        p.sfx_death.play()
                        players.remove(player)
                        start_time = pg.time.get_ticks()
                        explosion = Explosion(blue_blast, pos_p)
                        explosions.add(explosion)
                    p.health -= 1
                    p.score -= TAKE_DAMAGE

        # Lasers' hits explosion control
        for ex in explosions:
            if ex.index == (len(ex.motion) - 1):
                # Delete the explosion when animation is over
                explosions.remove(ex)

        # Update
        backgrounds.update()
        players.update(keys)
        if player.shield:
            shields.update(player, pg.time.get_ticks())
        lasers.update()
        enemies.update()
        enemies_2.update(previous_pos)
        enemies_lasers.update()
        explosions.update()
        health_kits.update()
        shield_kits.update()
        health_bar.update(player.health)

        previous_pos = player.rect.centerx

        # Draw

        backgrounds.draw(screen)

        players.draw(screen)
        if player.shield:
            shields.draw(screen)
        lasers.draw(screen)
        enemies.draw(screen)
        enemies_2.draw(screen)
        enemies_lasers.draw(screen)
        explosions.draw(screen)
        health_kits.draw(screen)
        shield_kits.draw(screen)

        # UI section
        screen.fill(BLACK, ui_rect)  # Fills UI section with black
        ui_stuff.draw(screen)

        # Text info
        if player.shield:
            shield_str = str(int(player_shield.remain_time / 1000)) + " s"
            shield_txt = game_font.render(shield_str, True, WHITE, BLACK)
            screen.blit(shield_ui, [ui_rect.centerx * 4 / 3, ui_rect.y - 8])
            screen.blit(shield_txt, [ui_rect.centerx * 4 / 3 + 30, ui_rect.y])
        score_str = "Score: " + str(player.score)
        kills_str = "Kills: " + str(player.kills)
        score_text = game_font.render(score_str, True, WHITE, BLACK)
        kills_text = game_font.render(kills_str, True, WHITE, BLACK)
        screen.blit(kills_text, ui_rect)
        screen.blit(score_text, [ui_rect.centerx / 3, ui_rect.y])

        pg.display.flip()
        clock.tick(frames)

        # Delay handling
        if background_2.rect.y >= 0:
            run_lv2 = False  # todo poner delay
        if not players:
            if current_time - start_time > 5000:
                # run_lv1 = False
                delay_over = True
        current_time = pg.time.get_ticks()

    print("Kills: " + kills_str)
    print("Score: " + score_str)
