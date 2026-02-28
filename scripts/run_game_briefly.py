import subprocess
import time
import sys

def run_briefly(seconds=5):
    print(f"Starting main.py for {seconds} seconds...")
    proc = subprocess.Popen([sys.executable, 'main.py'])
    try:
        time.sleep(seconds)
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
    print("Terminated successfully.")

if __name__ == "__main__":
    run_briefly()
