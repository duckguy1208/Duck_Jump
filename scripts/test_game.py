import os

# Use dummy video driver for headless testing
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame as pg
import random
from object import Platform, Object


def is_reachable(p1, p2, jump_speed=-800, gravity=1500, horizontal_vel=400):
    """
    Check if p2 is reachable from p1.
    p1, p2 are Platform objects.
    """
    dy = p1.rect.top - p2.rect.top
    if dy <= 0:
        return True  # It's below or at the same level

    # Max height check
    max_h = (jump_speed**2) / (2 * gravity)
    if dy > max_h:
        return False

    # Horizontal distance check
    # Solve 0.5 * gravity * t^2 + jump_speed * t + dy = 0
    a = 0.5 * gravity
    b = jump_speed
    c = dy
    discriminant = b**2 - 4 * a * c
    if discriminant < 0:
        return False

    t2 = (-b + (discriminant**0.5)) / (2 * a)

    # t2 is the later time (when falling back down through the height)
    max_t = t2
    max_dx = horizontal_vel * max_t

    # Closest horizontal distance between platforms
    if p2.rect.right < p1.rect.left:
        dist_x = p1.rect.left - p2.rect.right
    elif p2.rect.left > p1.rect.right:
        dist_x = p2.rect.left - p1.rect.right
    else:
        dist_x = 0

    return dist_x <= max_dx


def test_platform_reachability_logic():
    random.seed(42)
    SCREEN_WIDTH = 1280

    # This matches the implementation in main.py
    def generate_platform_new(prev_platform):
        max_dy = 180
        min_dy = 120
        dy = random.randint(min_dy, max_dy)
        y_pos = prev_platform.rect.y - dy
        width = random.randint(200, 400)
        max_dx = 250
        min_x = max(0, prev_platform.rect.x - max_dx)
        max_x = min(SCREEN_WIDTH - width, prev_platform.rect.right + max_dx - width)
        if min_x <= max_x:
            x_pos = random.randint(int(min_x), int(max_x))
        else:
            x_pos = random.randint(0, SCREEN_WIDTH - width)
        return Platform(x_pos, y_pos, width, 40)

    platforms = [Platform(100, 600, 400, 40)]

    for _ in range(100):
        new_p = generate_platform_new(platforms[-1])
        assert is_reachable(platforms[-1], new_p), (
            f"Platform at {new_p.rect} not reachable from {platforms[-1].rect}"
        )
        platforms.append(new_p)


def test_platform_creation():
    p = Platform(100, 200, 50, 10)
    assert p.rect.x == 100
    assert p.rect.y == 200
    assert p.rect.width == 50
    assert p.rect.height == 10


def test_object_movement():
    pg.init()
    surface = pg.Surface((2000, 600))  # Larger surface to avoid boundary cap
    obj = Object(surface)
    initial_x = obj.pos.x
    obj.move(1, 0, 1000)  # Move right for 1 second at vel=400
    # Boundary check might still hit if random start is too far right
    if initial_x + 400 <= 2000 - 60:
        assert obj.pos.x == initial_x + 400
    else:
        assert obj.pos.x == 2000 - 60


def test_camera_rendering():
    pg.init()
    surface = pg.Surface((800, 600))
    p = Platform(100, 200, 50, 10)
    # This just tests it doesn't crash, since we can't easily check the surface content here without more complex mocking
    p.draw(surface, camera_y=50)
    assert True


def test_procedural_generation_logic():
    # Simulate the logic in main.py
    platforms = [Platform(100, 600, 400, 40)]
    highest_platform_y = 600
    camera_y = 0
    SCREEN_HEIGHT = 720

    def generate_platform(y_pos):
        return Platform(0, y_pos, 200, 40)

    # Duck moves up
    duck_pos_y = 200
    if duck_pos_y < camera_y + SCREEN_HEIGHT / 2:
        camera_y = duck_pos_y - SCREEN_HEIGHT / 2

    # Should trigger generation if camera moved up enough
    while highest_platform_y > camera_y - SCREEN_HEIGHT:
        highest_platform_y -= 200
        platforms.append(generate_platform(highest_platform_y))

    assert len(platforms) > 1
    assert platforms[-1].rect.y < 600


def test_score_increment():
    score = 0
    max_height = 360  # Initial

    # Duck moves up
    duck_pos_y = 300
    if duck_pos_y < max_height:
        score += int((max_height - duck_pos_y) / 10)
        max_height = duck_pos_y

    assert score == 6
    assert max_height == 300

    # Duck moves down
    duck_pos_y = 400
    if duck_pos_y < max_height:
        score += int((max_height - duck_pos_y) / 10)
        max_height = duck_pos_y

    assert score == 6  # Score should not change
    assert max_height == 300


def test_reset_spawns_on_starting_platform():
    """After resetting the game the duck should be positioned over the first
    platform and marked as on the ground."""
    import main as mainmod

    pg.init()

    duck, camera_y, platforms, hpy, score, mh, go, w = mainmod.reset_game()
    assert platforms, "no platforms were created"
    first = platforms[0]
    # duck x should match platform center
    assert duck.pos.x == first.rect.centerx
    # duck y should sit directly above or on top of the platform
    assert duck.pos.y <= first.rect.top
    assert duck.pos.y >= first.rect.top - duck.sprite_size / 2
    assert duck.on_ground


def test_initial_platforms_reachable():
   
    import main as mainmod

    pg.init()
    # reproducible starter platforms during tests
    random.seed(0)
    duck, camera_y, platforms, *_ = mainmod.reset_game()
    assert len(platforms) >= 3

    # reuse helper from above tests
    assert is_reachable(platforms[0], platforms[1]), (
        f"Second starter platform {platforms[1].rect} not reachable from {platforms[0].rect}"
    )
    assert is_reachable(platforms[1], platforms[2]), (
        f"Third starter platform {platforms[2].rect} not reachable from {platforms[1].rect}"
    )


def test_game_over_condition():
    # Simulate game over condition logic
    SCREEN_HEIGHT = 720
    camera_y = -1000  # Camera has moved up significantly

    # Duck is above the bottom of the view
    duck_pos_y = -500
    game_over = duck_pos_y > camera_y + SCREEN_HEIGHT
    assert not game_over

    # Duck falls below the bottom of the view
    duck_pos_y = -200  # -200 is "below" -1000 + 720 = -280
    game_over = duck_pos_y > camera_y + SCREEN_HEIGHT
    assert game_over
