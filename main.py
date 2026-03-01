import pygame as pg
import random
import asyncio
from pathlib import Path
from duck import Duck
from object import Platform
from utils import clamp_platform_distance

# Base directory for this script (ensure asset paths are resolved relative to the
# location of this file, not the current working directory)
BASE_DIR = Path(__file__).resolve().parent



pg.init()
mixer_available = False
try:
    pg.mixer.init()
    pg.mixer.set_num_channels(32)
    mixer_available = True
except pg.error:
    print("Warning: Audio device not available. Sound disabled.")

sizes = pg.display.get_desktop_sizes()
width = sizes[0][0]

isMobile = width < 767

# Portrait for mobile, Landscape for desktop
if isMobile:
    SCREEN_WIDTH = 405  # Standard 9:16 aspect ratio roughly
    SCREEN_HEIGHT = 720
else:
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720

print("Screen Dimensions: " + str(SCREEN_WIDTH) + ", " + str(SCREEN_HEIGHT))

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

clock = pg.time.Clock()


def generate_platform(prev_platform):
    # Max vertical gap should be less than the duck's max jump height (~213 pixels)
    max_dy = 210 
    min_dy = 100
    dy = random.randint(min_dy, max_dy)
    y_pos = prev_platform.rect.y - dy
    
    width = random.randint(50, 200)
    
    # Based on dy=180, duck can travel ~290 pixels horizontally during the jump.
    # We'll use a slightly more conservative max_dx to ensure it's comfortably reachable.
    max_dx_init = 250 + int(prev_platform.rect.y / 100)  
    max_dx = clamp_platform_distance(max_dx_init)

    min_x = max(0, prev_platform.rect.x - max_dx)
    max_x = min(SCREEN_WIDTH - width, prev_platform.rect.right + max_dx - width)

    if min_x <= max_x:
        x_pos = random.randint(int(min_x), int(max_x))
    else:
        x_pos = random.randint(0, SCREEN_WIDTH - width)

    return Platform(x_pos, y_pos, width, 40)

def main():
    # Load stitched background image
    stitched_bg_path = BASE_DIR / "assets" / "images" / "stitched_background.png"
    try:
        raw_stitched_bg = pg.image.load(str(stitched_bg_path)).convert()
        # original slice height from backgrounds.
        original_slice_height = 720
        # Use "Cover" logic: scale so it fills the screen without squishing.
        # We want each slice to be exactly SCREEN_HEIGHT tall.
        scale = max(
            SCREEN_WIDTH / raw_stitched_bg.get_width(),
            SCREEN_HEIGHT / original_slice_height,
        )
        new_w = int(raw_stitched_bg.get_width() * scale)
        new_h = int(raw_stitched_bg.get_height() * scale)
        stitched_bg = pg.transform.scale(raw_stitched_bg, (new_w, new_h))
    except Exception as e:
        print(f"Error loading background image: {stitched_bg_path} -> {e}")
        raise
    stitched_bg_height = stitched_bg.get_height()
    num_backgrounds = stitched_bg_height // SCREEN_HEIGHT

    font = pg.font.Font(None, 74)
    small_font = pg.font.Font(None, 36)

    quack_sound = None
    wing_flap = None
    if mixer_available:
        quack_sound_path = BASE_DIR / "assets" / "sounds" / "quack_sound.ogg"
        wing_flap_path = BASE_DIR / "assets" / "sounds" / "wing_flap.ogg"
        try:
            quack_sound = pg.mixer.Sound(str(quack_sound_path))
        except Exception as e:
            print(f"Error loading quack sound: {quack_sound_path} -> {e}")
        try:
            wing_flap = pg.mixer.Sound(str(wing_flap_path))
        except Exception as e:
            print(f"Error loading wing flap sound: {wing_flap_path} -> {e}")

    def reset_game():
   
        d = Duck(screen)
        # three starter platforms (bottom first)
        # the very first platform is fixed so the duck has a predictable
        # starting point; subsequent platforms are created via the same
        # logic used during gameplay to guarantee they lie within the duck's
        # jump range.  Prior implementation hard‑coded the second and third
        # platforms which could occasionally place them out of reach on narrow
        # screens or unusual sizes.
        if SCREEN_WIDTH > 400:
            first = Platform(SCREEN_WIDTH // 2 - 200, 600, 400, 40)
        else:
            first = Platform(10, 600, SCREEN_WIDTH - 20, 40)

        platforms = [first]
    
        # Generate initial platforms: one generation cycle (2 on desktop, 1 on mobile)
        num_to_gen = 2 if not isMobile else 1
        for _ in range(num_to_gen):
            new_platform = generate_platform(platforms[-1])
            platforms.append(new_platform)

        # position duck above the first platform so it always starts there
        d.pos = pg.Vector2(first.rect.centerx, first.rect.top - d.sprite_size / 2)
        d.on_ground = True

        hpy = first.rect.y
        s = 0
        mh = SCREEN_HEIGHT / 2
        go = False
        w = False
        cy = 0  # camera start at bottom of stitched image
        return d, cy, platforms, hpy, s, mh, go, w

    duck, camera_y, platforms, highest_platform_y, score, max_height, game_over, won = (
        reset_game()
    )
    paused = False
    start_menu = True

    # Current horizontal velocity multiplier for the current jump
    horizontal_multiplier = 0

    while True:
        # always tick the clock each iteration, even while the start menu is showing
        # so that we don't accumulate a huge delta when the player finally begins.
        dt = clock.tick(60)
        # it is possible for a very large dt (e.g. after resuming from a pause in
        # a debugger); clamp to something reasonable to avoid tunnelling through
        # platforms.
        if dt > 100:
            dt = 100

        if start_menu:
            # Process events to clear the start menu
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    raise SystemExit
                if event.type in [pg.KEYDOWN, pg.MOUSEBUTTONDOWN, pg.FINGERDOWN]:
                    # reset timing variables as we exit menu to avoid leftover
                    # motion from a prior session
                    start_menu = False
                    duck.vertical_vel = 0
                    duck.on_ground = True

            bg_y_offset = -(stitched_bg_height - SCREEN_HEIGHT)
            screen.blit(stitched_bg, ((SCREEN_WIDTH - stitched_bg.get_width()) // 2, bg_y_offset))
            overlay = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            title_text = font.render("DUCK JUMP", True, (255, 255, 0))
            instruction_text = small_font.render(
                "Tap to Jump in a Direction", True, (255, 255, 255)
            )
            screen.blit(
                title_text,
                (
                    SCREEN_WIDTH // 2 - title_text.get_width() // 2,
                    SCREEN_HEIGHT // 2 - 50,
                ),
            )
            screen.blit(
                instruction_text,
                (
                    SCREEN_WIDTH // 2 - instruction_text.get_width() // 2,
                    SCREEN_HEIGHT // 2 + 50,
                ),
            )
            pg.display.flip()
            #await asyncio.sleep(0)
            continue

        prev_vertical_vel = duck.vertical_vel
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                raise SystemExit

            if game_over or won:
                if event.type in [pg.KEYDOWN, pg.MOUSEBUTTONDOWN, pg.FINGERDOWN]:
                    (
                        duck,
                        camera_y,
                        platforms,
                        highest_platform_y,
                        score,
                        max_height,
                        game_over,
                        won,
                    ) = reset_game()
                    horizontal_multiplier = 0
                    start_menu = True
                continue

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_UP:
                    if duck.on_ground:
                        duck.jump()
                if event.key == pg.K_SPACE:
                    duck.quack()
                    if quack_sound:
                        quack_sound.play()
                if event.key == pg.K_p:
                    paused = True

            if event.type in [pg.MOUSEBUTTONDOWN, pg.FINGERDOWN]:
                if event.type == pg.MOUSEBUTTONDOWN:
                    tap_x, tap_y = event.pos
                else:  # pg.FINGERDOWN
                    tap_x = event.x * SCREEN_WIDTH
                    tap_y = event.y * SCREEN_HEIGHT

                # Check if tap is on the duck (within 20 pixels of center)
                # duck.pos.y is world space, we need screen space
                duck_screen_y = duck.pos.y - camera_y
                dist = ((tap_x - duck.pos.x) ** 2 + (tap_y - duck_screen_y) ** 2) ** 0.5

                if dist <= 20:
                    duck.quack()
                    if quack_sound:
                        quack_sound.play()
                else:
                    # Granular horizontal: relative to duck position
                    # If tap is at duck's x, multiplier is 0. If at screen edge, it's ~1.0 or ~-1.0
                    dist_x = tap_x - duck.pos.x
                    horizontal_multiplier = dist_x / (SCREEN_WIDTH / 2)
                    # Clamp multiplier to [-1.0, 1.0]
                    horizontal_multiplier = max(-1.0, min(1.0, horizontal_multiplier))

                    if duck.on_ground:
                        duck.jump()

        while paused:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    raise SystemExit

                if event.type in [pg.KEYDOWN, pg.MOUSEBUTTONDOWN, pg.FINGERDOWN]:
                    paused = False

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_p:
                        paused = False
                    if event.key == pg.K_r:
                        (
                            duck,
                            camera_y,
                            platforms,
                            highest_platform_y,
                            score,
                            max_height,
                            game_over,
                            won,
                        ) = reset_game()
                        paused = False
                        start_menu = True

            overlay = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            continue_text = font.render("Press P To Continue", True, (255, 255, 0))
            restart_text = font.render("Press R To Restart", True, (255, 255, 0))

            screen.blit(
                continue_text,
                (
                    SCREEN_WIDTH // 2 - continue_text.get_width() // 2,
                    SCREEN_HEIGHT // 2 - 50,
                ),
            )
            screen.blit(
                restart_text,
                (
                    SCREEN_WIDTH // 2 - restart_text.get_width() // 2,
                    SCREEN_HEIGHT // 2 + 50,
                ),
            )

            pg.display.flip()
            #await asyncio.sleep(0)

        # dt already computed at the top of the loop; no need to tick again here.
        if not game_over and not won:
            duck.quack_timer -= dt
            if duck.quack_timer < 0:
                duck.quack_timer = 0

            # Keyboard horizontal movement
            keys = pg.key.get_pressed()
            kb_h = 0
            if keys[pg.K_LEFT]:
                kb_h = -0.75
            elif keys[pg.K_RIGHT]:
                kb_h = 0.75

            # effective multiplier: keyboard overrides tap trajectory
            move_h = kb_h if kb_h != 0 else horizontal_multiplier

            # If duck lands, reset lateral movement (trajectory)
            if duck.on_ground:
                horizontal_multiplier = 0

            if move_h != 0:
                duck.move(move_h, 0, dt)

            duck.applyGravity(dt, platforms)

            if prev_vertical_vel >= 0 and duck.vertical_vel < 0:
                if wing_flap:
                    wing_flap.play()

            if duck.pos.y < max_height:
                score += int((max_height - duck.pos.y) / 10)
                max_height = duck.pos.y

            if duck.pos.y < camera_y + SCREEN_HEIGHT / 2:
                camera_y = duck.pos.y - SCREEN_HEIGHT / 2

            # calculate which background slice we're in every frame so the win
            # condition works reliably; this used to be indented under the camera
            # update and could leave ``level_index`` undefined, crashing on input.
            level_index = int(max(0, -camera_y) // SCREEN_HEIGHT)
            if level_index >= num_backgrounds:
                won = True

            while highest_platform_y > camera_y - SCREEN_HEIGHT:
                new_platform = generate_platform(platforms[-1])
                platforms.append(new_platform)
                highest_platform_y = new_platform.rect.y

            # Clean up old platforms
            platforms = [p for p in platforms if p.rect.y < camera_y + SCREEN_HEIGHT + 100]

            # Check for game over
            if duck.pos.y > camera_y + SCREEN_HEIGHT:
                game_over = True

        bg_y_offset = -(stitched_bg_height - SCREEN_HEIGHT + camera_y)
        bg_y_offset = min(0, max(-(stitched_bg_height - SCREEN_HEIGHT), bg_y_offset))
        screen.blit(
            stitched_bg, ((SCREEN_WIDTH - stitched_bg.get_width()) // 2, bg_y_offset)
        )

        for p in platforms:
            p.draw(screen, camera_y)
        duck.draw(camera_y)

        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        if game_over or won:
            overlay = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            title_text = font.render(
                "YOU WIN!" if won else "GAME OVER", True, (255, 255, 0)
            )
            restart_text = small_font.render("Tap to Restart", True, (255, 255, 255))
            screen.blit(
                title_text,
                (
                    SCREEN_WIDTH // 2 - title_text.get_width() // 2,
                    SCREEN_HEIGHT // 2 - 50,
                ),
            )
            screen.blit(
                restart_text,
                (
                    SCREEN_WIDTH // 2 - restart_text.get_width() // 2,
                    SCREEN_HEIGHT // 2 + 50,
                ),
            )

        pg.display.flip()
        #await asyncio.sleep(0)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
