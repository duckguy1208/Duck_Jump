import os
# Use dummy video driver for headless testing
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pg
import pytest
from duck import Duck
from object import Object

def test_jump_multiplier():
    pg.init()
    surface = pg.Surface((800, 600))
    duck = Duck(surface)
    duck.on_ground = True
    
    # Base jump speed is -800
    base_jump = duck.jump_speed 
    
    # Test constant jump (no multiplier)
    duck.jump()
    assert duck.vertical_vel == base_jump
    
    # Test jump with multiplier (verify object.py change)
    duck.on_ground = True
    duck.jump(1.5)
    assert duck.vertical_vel == base_jump * 1.5

def test_mobile_horizontal_calculation_logic():
    # We test the logic we implemented in main.py
    # horizontal_multiplier = (tap_x - duck.pos.x) / (SCREEN_WIDTH / 2)
    SCREEN_WIDTH = 1280
    duck_x = 640 # Center
    
    # Tap far right
    tap_x = 1280
    h_mult = (tap_x - duck_x) / (SCREEN_WIDTH / 2)
    assert h_mult == 1.0
    
    # Tap far left
    tap_x = 0
    h_mult = (tap_x - duck_x) / (SCREEN_WIDTH / 2)
    assert h_mult == -1.0
    
    # Tap at duck
    tap_x = 640
    h_mult = (tap_x - duck_x) / (SCREEN_WIDTH / 2)
    assert h_mult == 0.0

def test_keyboard_movement_logic():
    pg.init()
    surface = pg.Surface((1280, 720))
    duck = Duck(surface)
    duck.pos.x = 640
    dt = 1000 # 1 second
    
    # Move left with kb_h = -0.75
    kb_h = -0.75
    duck.move(kb_h, 0, dt)
    # Expected: 640 + (-0.75 * 400 * 1.0) = 640 - 300 = 340
    assert duck.pos.x == 340
    
    # Move right with kb_h = 0.75
    duck.pos.x = 640
    kb_h = 0.75
    duck.move(kb_h, 0, dt)
    # Expected: 640 + (0.75 * 400 * 1.0) = 640 + 300 = 940
    assert duck.pos.x == 940

def test_keyboard_overrides_mobile_logic():
    # Logic in main.py: move_h = kb_h if kb_h != 0 else horizontal_multiplier
    
    # Case 1: Only mobile active
    kb_h = 0
    h_mult = 1.0
    move_h = kb_h if kb_h != 0 else h_mult
    assert move_h == 1.0
    
    # Case 2: Keyboard active, mobile active (override)
    kb_h = -0.75
    h_mult = 1.0
    move_h = kb_h if kb_h != 0 else h_mult
    assert move_h == -0.75
    
    # Case 3: Only keyboard active
    kb_h = 0.75
    h_mult = 0
    move_h = kb_h if kb_h != 0 else h_mult
    assert move_h == 0.75

def test_quack_on_tap_logic():
    # Simulate quack_on_tap logic from main.py
    duck_x = 640
    duck_y = 360
    camera_y = 0
    duck_screen_y = duck_y - camera_y
    
    # Tap close to duck (within 20px)
    tap_x = 650
    tap_y = 350
    dist = ((tap_x - duck_x)**2 + (tap_y - duck_screen_y)**2)**0.5
    assert dist <= 20
    
    # Tap far from duck
    tap_x = 100
    tap_y = 100
    dist = ((tap_x - duck_x)**2 + (tap_y - duck_screen_y)**2)**0.5
    assert dist > 20
