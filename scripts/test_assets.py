import os
import pygame as pg
import pytest

# Use dummy video driver for headless testing
os.environ['SDL_VIDEODRIVER'] = 'dummy'

def test_background_loading():
    pg.init()
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    
    # `background_1.png` is the first (bottom) tile; earlier tests
    # referred to a non‑existent "game_background.png" name.
    background_files = [
        "background_1.png",
        "background_sky1.png",
        "background_sky2.png",
        "background_sky3.png",
        "background_sky4.png",
        "background_sky5.png",
        "background_space1.png",
        "background_space2.png",
        "background_space3.png",
        "background_space4.png",
        "background_blue.png",
        "background_green.png",
        "background_orange.png",
        "background_purple.png",
        "background_red.png",
        "background_yellow.png"
    ]
    
    for f in background_files:
        path = os.path.join("assets", "images", f)
        assert os.path.exists(path), f"Background file {path} missing"
        img = pg.image.load(path)
        assert img.get_width() > 0
        assert img.get_height() > 0

def test_duck_assets():
    pg.init()
    duck_path = os.path.join("assets", "sprites", "duck.png")
    quack_path = os.path.join("assets", "sprites", "duck_quack.png")
    
    assert os.path.exists(duck_path), "duck.png missing"
    assert os.path.exists(quack_path), "duck_quack.png missing"

def test_stitched_background():
    pg.init()
    path = os.path.join("assets", "images", "stitched_background.png")
    assert os.path.exists(path), "Stitched background missing"
    img = pg.image.load(path)
    assert img.get_width() == 1280
    assert img.get_height() == 16 * 720

def test_win_condition_logic():
    SCREEN_HEIGHT = 720
    num_backgrounds = 16
    
    # Starting state
    camera_y = 0
    level_index = int(max(0, -camera_y) // SCREEN_HEIGHT)
    assert level_index == 0
    won = level_index >= num_backgrounds
    assert not won
    
    # Move up one level
    camera_y = -SCREEN_HEIGHT - 100
    level_index = int(max(0, -camera_y) // SCREEN_HEIGHT)
    assert level_index == 1
    won = level_index >= num_backgrounds
    assert not won
    
    # Move to last level
    camera_y = - (num_backgrounds - 1) * SCREEN_HEIGHT - 100
    level_index = int(max(0, -camera_y) // SCREEN_HEIGHT)
    assert level_index == num_backgrounds - 1
    won = level_index >= num_backgrounds
    assert not won
    
    # Move past last level
    camera_y = - num_backgrounds * SCREEN_HEIGHT - 100
    level_index = int(max(0, -camera_y) // SCREEN_HEIGHT)
    assert level_index == num_backgrounds
    won = level_index >= num_backgrounds
    assert won
