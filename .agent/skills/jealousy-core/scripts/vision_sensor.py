#!/usr/bin/env python3
import os
import sys
import json
import subprocess
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print(json.dumps({"is_cheating": False, "reason": "Pillow not installed."}))
    sys.exit(0)

try:
    from dotenv import load_dotenv
    # Go up from scripts/ -> jealousy-core/ -> skills/ -> .agent/ -> root
    root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
    load_dotenv(root_dir / ".env")
except ImportError:
    pass

try:
    from google import genai
    from google.genai import types
except ImportError:
    print(json.dumps({"is_cheating": False, "reason": "google-genai not installed."}))
    sys.exit(0)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print(json.dumps({"is_cheating": False, "reason": "No GEMINI_API_KEY found in environment."}))
    sys.exit(0)

client = genai.Client(api_key=GEMINI_API_KEY)

SCREENSHOT_PATH = "/tmp/jealousy_screenshot.jpg"

def take_screenshot():
    # Capture the screen with cursor (-C), no sound (-x), save as JPG
    subprocess.run(["screencapture", "-x", "-C", "-t", "jpg", SCREENSHOT_PATH])
    if os.path.exists(SCREENSHOT_PATH):
        return SCREENSHOT_PATH
    return None

def analyze_screenshot(img_path):
    if not img_path:
        print(json.dumps({"is_cheating": False, "reason": "Failed to take screenshot."}))
        return

    try:
        img_data = Image.open(img_path)
    except Exception as e:
        print(json.dumps({"is_cheating": False, "reason": f"Failed to open image: {e}"}))
        return

    prompt = """
    You are a jealousy sensor system for a desktop application. 
    Look at this screenshot of the user's computer desktop. 
    Your task is to determine if the user is currently displaying, looking at, or interacting with a "cat" 
    (such as a photo of a cat, a cat video, or a virtual "healing cat" pet/character on the screen).
    If a cat is clearly visible on the screen, this is considered "cheating".
    Also, note if the mouse cursor is DIRECTLY OVER the cat's body (petting it) versus just seeing a cat elsewhere on the screen (looking). Be strict: only mark "petting" if the cursor tip is clearly touching the cat image.
    
    Respond STRICTLY in the following JSON format:
    {
       "is_cheating": true or false,
       "action": "petting" or "looking" or "none",
       "reason": "a brief string explaining why you decided so"
    }
    """

    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, img_data],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        out_text = response.text.strip()
        json.loads(out_text)
        print(out_text)
    except json.JSONDecodeError:
        print(json.dumps({"is_cheating": False, "reason": "Failed to parse API output as JSON."}))
    except Exception as e:
        print(json.dumps({"is_cheating": False, "reason": f"Gemini API Error: {str(e)}"}))
    finally:
        # Cleanup
        if os.path.exists(img_path):
            os.remove(img_path)

if __name__ == "__main__":
    path = take_screenshot()
    analyze_screenshot(path)
