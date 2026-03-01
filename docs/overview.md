# Duck Jump Project Overview

Duck Jump is a vertical platformer built using `pygame-ce`, featuring a duck that must jump across procedurally generated platforms to ascend through various levels.

## Core Gameplay

- **Objective:** Navigate the duck upward as high as possible. The score increases as the duck reaches new heights.
- **Progression:** The game features a progression of backgrounds as the player ascends:
  - Initial level: `game_background.png`
  - Sky levels: `sky1` through `sky5`
  - Space levels: `space1` through `space4`
  - Infinite Loop: After space, the game continues through a series of colored backgrounds.
- **Game Over:** Falling off the bottom of the screen ends the game.
- **Winning:** Reaching the end of the stitched background sequence triggers a "YOU WIN!" screen, though the game can continue infinitely if configured.

## Controls

### Desktop
- **Arrow Keys (Left/Right):** Move the duck horizontally.
- **Up Arrow:** Jump (only when on a platform).
- **Space:** Quack! (Plays sound and shows text).
- **P:** Pause the game.
- **R:** Restart (from pause menu).

### Mobile / Mouse
- **Tap/Click:** Jump in a direction relative to the duck's current horizontal position. Tapping far to the left or right of the duck gives more horizontal momentum.
- **Tap on Duck:** Quack!
- **Any Key/Tap:** Restart from the Game Over or Win screen.

## Technical Details

- **Engine:** [pygame-ce](https://pyga.me/) (Pygame Community Edition).
- **Web Deployment:** Prepared for [pygbag](https://github.com/pygame-web/pygbag) to be deployed as a Progressive Web App (PWA) on GitHub Pages.
- **Procedural Generation:** Platforms are generated on-the-fly, ensuring they are always within the duck's maximum jump height (~213 pixels) and reachable horizontal distance.
- **Camera System:** The camera follows the duck upward, but never downward, creating the "don't fall" challenge.
- **Responsive Design:** The game automatically detects screen width and adjusts to Portrait mode (405x720) for mobile and Landscape mode (1280x720) for desktop.
- **Physics:** Implemented in the `Object` class with gravity, acceleration, and basic collision detection with platforms.

## Project Structure

- `main.py`: Entry point, game loop, platform generation, and camera logic.
- `duck.py`: `Duck` class, extending the base `Object` with quacking functionality.
- `object.py`: Base `Object` class for physics and the `Platform` class.
- `utils.py`: Utility functions like clamping.
- `assets/`: Contains images (sprites, backgrounds) and sounds (ogg format).
- `scripts/`: Development scripts for testing, asset management, and deployment.
- `docs/`: Project documentation.

## Development & Testing

- **Linting:** `ruff` is used for Python standard enforcement.
- **Formatting:** `prettier` or standard Python formatters via VS Code.
- **Testing:** `pytest` is used for unit and behavioral tests. Use `py -m pytest test_game.py`.
- **Quick Run:** Use `py scripts/run_game_briefly.py` to verify the game runs without crashing.
