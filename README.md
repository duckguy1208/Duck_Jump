# Tie and Jon Pygame Project

A simple Pygame project.

## Setup Instructions

### 1. Prerequisites
- Python 3.x installed.

### 2. Create and Activate Virtual Environment (Optional but Recommended)

**Windows:**
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
python -m pip install -r requirements.txt
```
Note: This project uses `pygame-ce` (Community Edition), which is a drop-in replacement for `pygame` with more frequent updates and better performance.

### 4. Run the Game
```bash
python main.py
```

### 5. Web Deployment (PWA)
This project uses `pygbag` to build a web-compatible version of the game.

To build the web version locally:
```bash
python -m pip install pygbag
python -m pygbag --build --disable-sound-format-error main.py
```
The build artifacts will be located in the `build/web` directory.

#### Deployment to GitHub Pages
A GitHub Actions workflow is set up to automatically build and deploy the game to the `gh-pages` branch whenever you push to the `main` branch. 

To enable this, go to your repository settings on GitHub:
1. **Settings** -> **Pages**
2. **Build and deployment** -> **Source**: "Deploy from a branch"
3. **Branch**: `gh-pages` / `/(root)`
4. Save and your game will be live at `https://<your-username>.github.io/<repo-name>/`

## Troubleshooting
If you encounter issues with `pygame-ce` installation on Linux, you may need to install additional system dependencies (e.g., `libsdl2-dev`, `libsdl2-image-dev`, `libsdl2-mixer-dev`, `libsdl2-ttf-dev`).
