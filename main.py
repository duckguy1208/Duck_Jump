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

# Detect if we should use mobile-style controls
MOBILE_MODE = True 

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
        p = [
            Platform(100, 600, 400, 40),
            Platform(600, 450, 400, 40),
            Platform(200, 300, 300, 40)
        ]
        return d, 0, p, 300, 0, SCREEN_HEIGHT / 2, False, False

    duck, camera_y, platforms, highest_platform_y, score, max_height, game_over, won = reset_game()
    paused = False
    start_menu = True

    # Mobile control regions
    jump_btn = pygame.Rect(SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT - 120, 120, 100)
    left_btn = pygame.Rect(50, SCREEN_HEIGHT - 120, 120, 100)
    right_btn = pygame.Rect(SCREEN_WIDTH - 170, SCREEN_HEIGHT - 120, 120, 100)

    while True:
        if start_menu:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        start_menu = False
                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
                    start_menu = False

            bg_y_offset = -(stitched_bg_height - SCREEN_HEIGHT)
            screen.blit(stitched_bg, (0, bg_y_offset))
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            title_text = font.render("DUCK JUMP", True, (255, 255, 0))
            instruction_text = small_font.render("Press SPACE or Tap to Start", True, (255, 255, 255))
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
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    duck, camera_y, platforms, highest_platform_y, score, max_height, game_over, won = reset_game()
                    start_menu = True
                if event.type in [pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN]:
                    duck, camera_y, platforms, highest_platform_y, score, max_height, game_over, won = reset_game()
                    start_menu = True
                continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    duck.jump()
                if event.key == pygame.K_SPACE:
                    duck.quack()
                    if quack_sound:
                        quack_sound.set_volume(0.5)
                        quack_sound.play()
                if event.key == pygame.K_q:
                    paused = True

            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.FINGERDOWN:
                mpos = getattr(event, 'pos', None)
                if mpos is None and hasattr(event, 'x'):
                    mpos = (event.x * SCREEN_WIDTH, event.y * SCREEN_HEIGHT)
                
                if mpos:
                    if jump_btn.collidepoint(mpos):
                        duck.jump()
                    elif not (left_btn.collidepoint(mpos) or right_btn.collidepoint(mpos)):
                        # Tap elsewhere to quack?
                        duck.quack()
                        if quack_sound:
                            quack_sound.play()

        while paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        paused = False
                    if event.key == pygame.K_r:
                        duck, camera_y, platforms, highest_platform_y, score, max_height, game_over, won = reset_game()
                        paused = False
                        start_menu = True
                if event.type in [pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN]:
                    paused = False

            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            pause_text = font.render("Paused", True, (255, 255, 0))
            continue_text = small_font.render("Tap to Continue", True, (255, 255, 0))
            screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
            pygame.display.flip()
            await asyncio.sleep(0)

        dt = clock.tick(60)

        if not game_over and not won:
            duck.quack_timer -= dt
            if duck.quack_timer < 0:
                duck.quack_timer = 0

            keys = pygame.key.get_pressed()
            dx = 0
            if keys[pygame.K_LEFT]:
                dx = -1
            elif keys[pygame.K_RIGHT]:
                dx = 1
            
            # Touch/Mouse continuous movement
            m_pressed = pygame.mouse.get_pressed()
            if m_pressed[0]:
                mpos = pygame.mouse.get_pos()
                if left_btn.collidepoint(mpos):
                    dx = -1
                elif right_btn.collidepoint(mpos):
                    dx = 1

            if dx != 0:
                duck.move(dx, 0, dt)

            if prev_vertical_vel >= 0 and duck.vertical_vel < 0:
                if wing_flap:
                    wing_flap.play()

            duck.applyGravity(dt, platforms)

            if duck.pos.y < max_height:
                score += int((max_height - duck.pos.y) / 10)
                max_height = duck.pos.y

            if duck.pos.y < camera_y + SCREEN_HEIGHT / 2:
                camera_y = duck.pos.y - SCREEN_HEIGHT / 2

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

        if MOBILE_MODE and not (game_over or won):
            # Draw UI Buttons
            for btn, label in [(left_btn, "<"), (right_btn, ">"), (jump_btn, "^")]:
                pygame.draw.rect(screen, (200, 200, 200, 100), btn, border_radius=10)
                txt = font.render(label, True, (50, 50, 50))
                screen.blit(txt, (btn.centerx - txt.get_width() // 2, btn.centery - txt.get_height() // 2))

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
