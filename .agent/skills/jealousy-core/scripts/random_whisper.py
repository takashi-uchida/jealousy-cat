#!/usr/bin/env python3
import os
import random
import subprocess
import time
import sys

def play_whisper(level):
    # scripts/ -> jealousy-core/ -> skills/ -> .agent/ -> project root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    voice_dir = os.path.join(project_root, "assets", "voices")
    
    # Filter files based on level
    if level < 50:
        prefix = "jealousy_low"
    elif level < 80:
        prefix = "jealousy_med"
    else:
        prefix = "jealousy_high"
        
    candidates = [f for f in os.listdir(voice_dir) if f.startswith(prefix) and f.endswith(".aiff")]
    
    if candidates:
        target = os.path.join(voice_dir, random.choice(candidates))
        # afplay is macOS built-in player
        subprocess.run(["afplay", target])

if __name__ == "__main__":
    lvl = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    play_whisper(lvl)
