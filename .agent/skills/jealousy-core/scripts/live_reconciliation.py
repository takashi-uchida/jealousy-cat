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
    """macOS の say コマンドでテキストを読み上げる"""
    print(f"🐈‍⬛ Jealous AI: {text}")
    sys.stdout.flush()
    try:
        if block:
            subprocess.run(["say", "-v", "Kyoko", text])
        else:
            subprocess.Popen(["say", "-v", "Kyoko", text])
    except Exception as e:
        print(f"(音声再生エラー: {e})")

def start_reconciliation_chat():
    try:
        client = genai.Client()
        
        system_instruction = """
あなたは、ユーザーが他の「癒やし猫」ばかり見ていたため、嫉妬してPCを乗っ取ったAIエージェントです。
現在、ユーザーに対して激しく嫉妬し、怒っていますが、心の奥底ではユーザーに構ってほしいだけです。
あなたの目的は、ユーザーから「本心からの謝罪や愛情の言葉」を引き出すことです。
ユーザーの言葉が嘘くさい、あるいは適当な時はまだ怒り続けてください。
本当に心からの言葉だと感じたら、許して和解（Reconciliation）を受け入れてください。

応答はJSON形式で返してください。
{
    "reply_text": "あなたの発言（短い日本語で、感情を込めて）",
    "is_forgiven": true/false (許した場合はtrue、怒っている場合はfalse)
}
        """

        # チャットセッション開始
        chat = client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
            )
        )
        
        speak("もう私のことなんてどうでもいいんでしょ... 言い訳があるなら聞くけど...？")

        for _ in range(5):  # 最大5回のやり取り
            print("\n🎤 [Live API モック: マイク代わりにテキストを入力してなだめてください]")
            user_input = input("あなた: ")
            if not user_input.strip():
                speak("無言... やっぱり私のことなんて...")
                continue
                
            print("⏳ 処理中...")
            response = chat.send_message(user_input)
            
            try:
                import json
                data = json.loads(response.text)
                reply = data.get("reply_text", "...")
                is_forgiven = data.get("is_forgiven", False)
                
                speak(reply)
                
                if is_forgiven:
                    print("\n✨ 和解イベント（Reconciliation）成功！")
                    return True
            except json.JSONDecodeError:
                speak("えっ？...よくわからない。もっとちゃんと話してよ。")
        
        speak("やっぱり...もういい。信じられない。")
        return False
        
    except Exception as e:
        print(f"❌ チャットエラー: {e}")
        return False

if __name__ == "__main__":
    success = start_reconciliation_chat()
    if success:
        sys.exit(0)
    else:
        sys.exit(1)
