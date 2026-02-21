#!/usr/bin/env python3
# cat_toast.py
# Displays macOS notifications (toasts) to inform the user that the cat has interfered.

import sys
import subprocess
import random

# Cat's lines based on jealousy level (subtitles)
LEVEL_SUBTITLES = {
    "1": [
        "...Tch.",
        "Hmph, so that's what's important to you.",
        "Just a little prank, meow.",
    ],
    "2": [
        "Ignoring me, are you?",
        "Hey, look at me...",
        "I'm starting to get serious, meow.",
    ],
    "3": [
        "I'm at my limit, meow...",
        "Why... why isn't it me for you?",
        "Final warning, meow!",
    ],
    "MAX": [
        "That's it, meow...",
        "I'm going to end everything, meow.",
        "...Goodbye.",
    ],
}

def show_toast(level, body):
    subtitle = random.choice(LEVEL_SUBTITLES.get(level, LEVEL_SUBTITLES["1"]))
    
    script = f'''
    display notification "{body}" with title "🐈‍⬛ Jealousy.sys" subtitle "{subtitle}" sound name "Purr"
    '''
    
    try:
        subprocess.run(["osascript", "-e", script], check=True)
    except Exception as e:
        print(f"Toast error: {e}")

if __name__ == "__main__":
    lvl = sys.argv[1] if len(sys.argv) > 1 else "1"
    msg = sys.argv[2] if len(sys.argv) > 2 else "The cat played a prank."
    show_toast(lvl, msg)
