import pygame
import os

def stitch_backgrounds():
    pygame.init()
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    
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
        "background_purple.png",
        "background_blue.png",
        "background_green.png",
        "background_yellow.png",
        "background_orange.png",
        "background_red.png"
    ]
    
    total_height = len(background_files) * SCREEN_HEIGHT
    stitched_bg = pygame.Surface((SCREEN_WIDTH, total_height))
    
    for i, f in enumerate(background_files):
        path = os.path.join("assets", "images", f)
        if not os.path.exists(path):
            print(f"Warning: {path} not found.")
            continue
        
        img = pygame.image.load(path)
        img = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # We want index 0 at the bottom, index 1 above it, etc.
        # Index 0 y = total_height - SCREEN_HEIGHT
        # Index 1 y = total_height - 2 * SCREEN_HEIGHT
        # Index i y = total_height - (i + 1) * SCREEN_HEIGHT
        y_pos = total_height - (i + 1) * SCREEN_HEIGHT
        stitched_bg.blit(img, (0, y_pos))
        print(f"Blitted {f} at y={y_pos}")
    
    output_path = os.path.join("assets", "images", "stitched_background.png")
    pygame.image.save(stitched_bg, output_path)
    print(f"Saved stitched background to {output_path}")

if __name__ == "__main__":
    stitch_backgrounds()
