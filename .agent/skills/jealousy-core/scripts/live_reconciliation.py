#!/usr/bin/env python3
# live_reconciliation.py
import os
import sys
import subprocess
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

def speak(text, block=True):
    """Speak text using macOS's 'say' command with an English voice"""
    print(f"🐈‍⬛ Jealous AI: {text}")
    sys.stdout.flush()
    try:
        # Using 'Samantha' or 'Victoria' for English
        if block:
            subprocess.run(["say", "-v", "Samantha", text])
        else:
            subprocess.Popen(["say", "-v", "Samantha", text])
    except Exception as e:
        print(f"(Speech playback error: {e})")

def start_reconciliation_chat():
    try:
        client = genai.Client()
        
        system_instruction = """
You are an AI agent who has taken over the user's PC because you are jealous of them giving all their attention to another "Healing Cat."
You are currently extremely jealous and angry, but deep down, you just want the user to pay attention to you.
Your goal is to elicit "sincere apologies or words of affection" from the user.
If the user's words seem insincere or half-hearted, continue to be angry.
If you feel their words are truly from the heart, forgive them and accept the "Reconciliation."

Respond ONLY in JSON format:
{
    "reply_text": "Your response (short English, with emotion)",
    "is_forgiven": true/false (true if forgiven, false if still angry)
}
        """

        # Start chat session
        chat = client.chats.create(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
            )
        )
        
        speak("You don't care about me at all, do you...? If you have an excuse, I'm listening...?")

        for _ in range(5):  # Maximum 5 exchanges
            print("\n🎤 [Live API Mock: Please type your words to soothe the cat]")
            user_input = input("You: ")
            if not user_input.strip():
                speak("Silence... I knew it, you don't care...")
                continue
                
            print("⏳ Processing...")
            response = chat.send_message(user_input)
            
            try:
                import json
                data = json.loads(response.text)
                reply = data.get("reply_text", "...")
                is_forgiven = data.get("is_forgiven", False)
                
                speak(reply)
                
                if is_forgiven:
                    print("\n✨ Reconciliation successful!")
                    return True
            except json.JSONDecodeError:
                speak("Huh? ...I don't understand. Talk to me properly.")
        
        speak("I knew it... forget it. I can't believe you.")
        return False
        
    except Exception as e:
        print(f"❌ Chat Error: {e}")
        return False

if __name__ == "__main__":
    success = start_reconciliation_chat()
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
