import pygame
import random
import asyncio
from pathlib import Path
from duck import Duck
from object import Platform
from utils import clamp_platform_distance

# Base directory for this script (ensure asset paths are resolved relative to the
# location of this file, not the current working directory)
BASE_DIR = Path(__file__).resolve().parent

pygame.init()
mixer_available = False
try:
    pygame.mixer.init()
    mixer_available = True
except pygame.error:
    print("Warning: Audio device not available. Sound disabled.")

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

clock = pygame.time.Clock()

def generate_platform(prev_platform):
    max_dy = 210 
    min_dy = 100
    dy = random.randint(min_dy, max_dy)
    y_pos = prev_platform.rect.y - dy
    width = random.randint(50, 200)
    max_dx_init = 250 + int(prev_platform.rect.y / 100)  
    max_dx = clamp_platform_distance(max_dx_init)

    min_x = max(0, prev_platform.rect.x - max_dx)
    max_x = min(SCREEN_WIDTH - width, prev_platform.rect.right + max_dx - width) 
    
    if min_x <= max_x:
        x_pos = random.randint(int(min_x), int(max_x))
    else:
        x_pos = random.randint(0, SCREEN_WIDTH - width)
        
    return Platform(x_pos, y_pos, width, 40)



def reset_game():
    """Return initial game state and put the duck over the first platform.

    This helper lives at module scope so it can be imported directly by tests.
    """
    d = Duck(screen)
    # three starter platforms (bottom first)
    platforms = [
        Platform(100, 600, 400, 40),
        Platform(600, 450, 400, 40),
        Platform(200, 300, 300, 40)
    ]
    # position duck above the first platform so it always starts there
    first = platforms[0]
    d.pos = pygame.Vector2(first.rect.centerx, first.rect.top - d.sprite_size / 2)
    d.on_ground = True

    hpy = first.rect.y
    s = 0
    mh = SCREEN_HEIGHT / 2
    go = False
    w = False
    cy = 0  # camera start at bottom of stitched image
    return d, cy, platforms, hpy, s, mh, go, w


async def main():
    stitched_bg_path = BASE_DIR / "assets" / "images" / "stitched_background.png"
    try:
        stitched_bg = pygame.image.load(str(stitched_bg_path)).convert()
    except Exception as e:
        print(f"Error loading background image: {stitched_bg_path} -> {e}")
        raise
    stitched_bg_height = stitched_bg.get_height()
    num_backgrounds = stitched_bg_height // SCREEN_HEIGHT

    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 36)

    quack_sound = None
    wing_flap = None
    if mixer_available:
        quack_sound_path = BASE_DIR / "assets" / "sounds" / "quack_sound.mp3"
        wing_flap_path = BASE_DIR / "assets" / "sounds" / "wing_flap.mp3"
        try:
            quack_sound = pygame.mixer.Sound(str(quack_sound_path))
        except Exception as e:
            print(f"Error loading quack sound: {quack_sound_path} -> {e}")
        try:
            wing_flap = pygame.mixer.Sound(str(wing_flap_path))
        except Exception as e:
            print(f"Error loading wing flap sound: {wing_flap_path} -> {e}")


    #def paused(): ran out of time in class


    duck, camera_y, platforms, highest_platform_y, score, max_height, game_over, won = reset_game()
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
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN]:
                    # reset timing variables as we exit menu to avoid leftover
                    # motion from a prior session
                    start_menu = False
                    duck.vertical_vel = 0
                    duck.on_ground = True

            bg_y_offset = -(stitched_bg_height - SCREEN_HEIGHT)
            screen.blit(stitched_bg, (0, bg_y_offset))
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            title_text = font.render("DUCK JUMP", True, (255, 255, 0))
            instruction_text = small_font.render("Tap to Jump in a Direction", True, (255, 255, 255))
            screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
            pygame.display.flip()
            await asyncio.sleep(0)
            continue

        prev_vertical_vel = duck.vertical_vel
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            
            if (game_over or won):
                if event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN]:
                    duck, camera_y, platforms, highest_platform_y, score, max_height, game_over, won = reset_game()
                    horizontal_multiplier = 0
                    start_menu = True
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if duck.on_ground:
                        duck.jump()
                        horizontal_multiplier = 0
                if event.key == pygame.K_LEFT:
                    if duck.on_ground:
                        duck.jump()
                    horizontal_multiplier = -0.75
                if event.key == pygame.K_RIGHT:
                    if duck.on_ground:
                        duck.jump()
                    horizontal_multiplier = 0.75
                if event.key == pygame.K_SPACE:
                    duck.quack()
                    if quack_sound:
                        quack_sound.play()
                if event.key == pygame.K_p:
                    paused = True

        while paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit

                if event.type in [pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN]:
                    paused = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        paused = False
                    if event.key == pygame.K_r:
                        duck, camera_y, platforms, highest_platform_y, score, max_height, game_over, won = reset_game()
                        paused = False
                        start_menu = True

            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            continue_text = font.render("Press P To Continue", True, (255, 255, 0))
            restart_text = font.render("Press R To Restart", True, (255, 255, 0))

            screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

            pygame.display.flip()
            await asyncio.sleep(0)

        # dt already computed at the top of the loop; no need to tick again here.
        if not game_over and not won:
            duck.quack_timer -= dt
            if duck.quack_timer < 0:
                duck.quack_timer = 0

            # If duck lands, reset lateral movement
            if duck.on_ground:
                horizontal_multiplier = 0

            if horizontal_multiplier != 0:
                duck.move(horizontal_multiplier, 0, dt)

            if prev_vertical_vel >= 0 and duck.vertical_vel < 0:
                if wing_flap:
                    wing_flap.play()

            duck.applyGravity(dt, platforms)

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

            platforms = [p for p in platforms if p.rect.y < camera_y + SCREEN_HEIGHT + 100]

            if duck.pos.y > camera_y + SCREEN_HEIGHT:
                game_over = True

        bg_y_offset = -(stitched_bg_height - SCREEN_HEIGHT + camera_y)
        bg_y_offset = min(0, max(-(stitched_bg_height - SCREEN_HEIGHT), bg_y_offset))
        screen.blit(stitched_bg, (0, bg_y_offset))

        for p in platforms:
            p.draw(screen, camera_y)
        duck.draw(camera_y)

        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        if game_over or won:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            title_text = font.render("YOU WIN!" if won else "GAME OVER", True, (255, 255, 0))
            restart_text = small_font.render("Tap to Restart", True, (255, 255, 255))
            screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

        pygame.display.flip()
        await asyncio.sleep(0)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
