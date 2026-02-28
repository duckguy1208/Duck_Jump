import pygame as pg
from pathlib import Path


def debug_sounds():
    pg.init()
    print("Pygame initialized.")

    try:
        pg.mixer.init()
        print("Mixer initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize mixer: {e}")
        return

    BASE_DIR = Path(__file__).resolve().parent.parent
    sound_dir = BASE_DIR / "assets" / "sounds"

    sounds = ["quack_sound.ogg", "wing_flap.ogg"]

    for sound_file in sounds:
        path = sound_dir / sound_file
        print(f"\nChecking: {path}")
        if path.exists():
            print(f"File exists. Size: {path.stat().st_size} bytes")
            try:
                sound = pg.mixer.Sound(str(path))
                print(f"Sound loaded successfully: {sound_file}")
                print(f"Length: {sound.get_length()} seconds")
            except Exception as e:
                print(f"Error loading sound {sound_file}: {e}")
        else:
            print(f"File DOES NOT EXIST: {path}")


if __name__ == "__main__":
    debug_sounds()
    pg.quit()
