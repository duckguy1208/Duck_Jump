# Gemini CLI - Project Context

## Project Overview

This is a Pygame-based game featuring a duck navigating platforms. The project uses `pygame-ce` and `pytest` for testing.

## Development Workflows

### Running the Game

To verify that the game runs without crashes (especially in environments where `timeout` might not behave as expected), use the `run_game_briefly.py` script found in the scripts directory. This script spawns the game and terminates it after 5 seconds.

```powershell
py scripts/run_game_briefly.py
```

### Testing

Always run tests before submitting a PR.

```powershell
py -m pytest test_game.py
```

### PowerShell Command Separation

When running multiple commands in a single line, use `;` instead of `&&` as this environment uses PowerShell.

## Style & Conventions

- Use `pygame-ce` features where applicable.
- Maintain the procedural generation logic that ensures platforms are always reachable.
- Prefer `pytest` for unit and behavioral tests.
- Keep `TODO.md` updated with progress.
