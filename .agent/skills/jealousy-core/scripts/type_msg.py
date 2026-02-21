#!/usr/bin/env python3
# type_msg.py
# Types eerie messages on screen (Overlay version)

import sys
import subprocess
import os
from dotenv import load_dotenv

def get_jealous_cat_message():
    try:
        from google import genai
        # Load .env from project root
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
        load_dotenv(os.path.join(root_dir, ".env"))
        
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return "Look at me, meow... don't look anywhere else..."

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.0-flash',
            contents='You are a cat jealous of your owner who is not giving you enough attention. Create a short, slightly yandere but cute cat-themed message in 1-2 sentences to grab the owner\'s attention. Use words like "meow" or "mew". Output only the message text.'
        )
        msg = response.text.strip(' \n"')
        if not msg:
            raise ValueError("Empty response from Gemini")
        return msg
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "Look only at me... don't look at other cats, meow..."

def type_message(msg):
    print(f"📝 Displaying message...: {msg}")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    overlay_script = os.path.join(script_dir, "overlay_effects.py")
    
    if not os.path.exists(overlay_script):
        print(f"Error: {overlay_script} not found")
        return

    # Asynchronous execution
    subprocess.Popen([sys.executable, overlay_script, "type", msg])

if __name__ == "__main__":
    if len(sys.argv) > 1:
        msg = sys.argv[1]
    else:
        msg = get_jealous_cat_message()
    type_message(msg)
