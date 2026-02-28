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
    print(max_dx)

    # The new platform should be placed such that it's reachable from the previous one.
    # The closest point of the new platform must be within max_dx of the previous platform.
    min_x = max(0, prev_platform.rect.x - max_dx)
    max_x = min(SCREEN_WIDTH - width, prev_platform.rect.right + max_dx - width) 
    
    if min_x <= max_x:
        x_pos = random.randint(int(min_x), int(max_x))
    else:
        # Fallback in case of weird constraints, though with SCREEN_WIDTH=1280 it shouldn't happen
        x_pos = random.randint(0, SCREEN_WIDTH - width)
        
    return Platform(x_pos, y_pos, width, 40)

async def main():
    # Load stitched background image
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

    # Load sound effects
    quack_sound = None
    wing_flap = None
    if mixer_available:
        quack_sound_path = BASE_DIR / "assets" / "sounds" / "quack_sound.ogg"
        wing_flap_path = BASE_DIR / "assets" / "sounds" / "wing_flap.ogg"
        try:
            quack_sound = pygame.mixer.Sound(str(quack_sound_path))
        except Exception as e:
            print(f"Error loading quack sound: {quack_sound_path} -> {e}")
        try:
            wing_flap = pygame.mixer.Sound(str(wing_flap_path))
        except Exception as e:
            print(f"Error loading wing flap sound: {wing_flap_path} -> {e}")

        
    def reset_game():
        d = Duck(screen)
        d.pos.y = SCREEN_HEIGHT / 2
        cy = 0
        p = [
            Platform(100, 600, 400, 40),
            Platform(600, 450, 400, 40),
            Platform(200, 300, 300, 40)
        ]
        hpy = 300
        s = 0
        mh = SCREEN_HEIGHT / 2
        go = False
        w = False
        return d, cy, p, hpy, s, mh, go, w


    duck, camera_y, platforms, highest_platform_y, score, max_height, game_over, won = reset_game()
    paused = False
    start_menu = True

    while True:
        if start_menu:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        start_menu = False

            # Rendering start menu
            bg_y_offset = -(stitched_bg_height - SCREEN_HEIGHT)
            screen.blit(stitched_bg, (0, bg_y_offset))

            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            title_text = font.render("DUCK JUMP", True, (255, 255, 0))
            instruction_text = small_font.render("Press SPACE to Start", True, (255, 255, 255))

            screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

            pygame.display.flip()
            await asyncio.sleep(0)
            continue

        # remember previous vertical velocity to detect upward transitions
        prev_vertical_vel = duck.vertical_vel
        # Process player inputs.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if (game_over or won) and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    duck, camera_y, platforms, highest_platform_y, score, max_height, game_over, won = reset_game()
                    start_menu = True
            # Handle single-press actions (jump, quack, pause)
            if not (game_over or won) and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    duck.jump()
                if event.key == pygame.K_SPACE:
                    duck.quack()
                    if quack_sound:
                        quack_sound.set_volume(0.5)
                        quack_sound.play()
                if event.key == pygame.K_p:
                    paused = True

        while paused == True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        paused = False
                    if event.key == pygame.K_r:
                        duck, camera_y, platforms, highest_platform_y, score, max_height, game_over, won = reset_game()
                        paused = False

            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            
            continue_text = font.render("Press P To Continue", True, (255, 255, 0))
            restart_text = font.render("Press R To Restart", True, (255, 255, 0))

           
            screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

            pygame.display.flip()
            await asyncio.sleep(0)

        dt = clock.tick(60)

        if not game_over and not won:
            # Decrement quack timer
            duck.quack_timer -= dt
            if duck.quack_timer < 0:
                duck.quack_timer = 0

            # Handle continuous arrow-key movement
            keys = pygame.key.get_pressed()
            dx = 0
            if keys[pygame.K_LEFT]:
                dx = -1
            if keys[pygame.K_RIGHT]:
                dx = 1
            
            if dx != 0:
                duck.move(dx, 0, dt)

            # Note: jump, quack, and pause are handled on KEYDOWN events above to avoid repeating while held
                

            # Play wing flap only when duck starts moving upward (transition from non-up to up)
            if prev_vertical_vel >= 0 and duck.vertical_vel < 0:
                if wing_flap:
                    wing_flap.play()

            duck.applyGravity(dt, platforms)

            # Update score based on height reached
            if duck.pos.y < max_height:
                score += int((max_height - duck.pos.y) / 10)
                max_height = duck.pos.y

            # Camera follow logic: if duck is in the upper half of the screen, scroll up
            if duck.pos.y < camera_y + SCREEN_HEIGHT / 2:
                camera_y = duck.pos.y - SCREEN_HEIGHT / 2

            # Check for win condition: passed all backgrounds
            level_index = int(max(0, -camera_y) // SCREEN_HEIGHT)
            if level_index >= num_backgrounds:
                won = True

            # Procedural platform generation
            while highest_platform_y > camera_y - SCREEN_HEIGHT:
                new_platform = generate_platform(platforms[-1])
                platforms.append(new_platform)
                highest_platform_y = new_platform.rect.y

            # Clean up old platforms
            platforms = [p for p in platforms if p.rect.y < camera_y + SCREEN_HEIGHT + 100]

            # Check for game over
            if duck.pos.y > camera_y + SCREEN_HEIGHT:
                game_over = True

        # Rendering
        # Calculate background offset: bottom of stitched image is camera_y = 0
        bg_y_offset = -(stitched_bg_height - SCREEN_HEIGHT + camera_y)
        # Clamp to ensure we don't show black at the top if we go past the win line
        bg_y_offset = min(0, max(-(stitched_bg_height - SCREEN_HEIGHT), bg_y_offset))
            
        screen.blit(stitched_bg, (0, bg_y_offset))  # Draw the background image

        # Render platforms
        for p in platforms:
            p.draw(screen, camera_y)

        # Render the graphics here.
        duck.draw(camera_y)

        # Draw score
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))

        if game_over or won:
            # Dim the screen
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            if won:
                title_text = font.render("YOU WIN!", True, (255, 255, 0))
            else:
                title_text = font.render("GAME OVER", True, (255, 255, 255))
                
            restart_text = small_font.render("Press R to Restart", True, (255, 255, 255))
            
            screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))

        pygame.display.flip()  # Refresh on-screen display
        await asyncio.sleep(0)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
