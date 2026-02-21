#!/usr/bin/env python3
# type_msg.py
# 画面に不気味なメッセージをタイピング表示する（オーバーレイ版）

import sys
import subprocess
import os
from dotenv import load_dotenv

def get_jealous_cat_message():
    try:
        from google import genai
        # プロジェクトルートの.envを読み込む
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
        load_dotenv(os.path.join(root_dir, ".env"))
        
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return "ボクのこと見てニャ... 他のとこ見ないで..."

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents='あなたは構ってくれない飼い主に嫉妬している猫です。飼い主の注意を引くために、短く、少しヤンデレ気味な、でも可愛らしい猫語のメッセージを1〜2文で作成してください。「にゃ」「ニャ」などを付けてください。出力はメッセージ本文のみにしてください。'
        )
        msg = response.text.strip(' \n"')
        if not msg:
            raise ValueError("Empty response from Gemini")
        return msg
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return "ボクだけを見て... 他の子ばっかり見ないでニャ..."

def type_message(msg):
    print(f"📝 メッセージを表示します...: {msg}")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    overlay_script = os.path.join(script_dir, "overlay_effects.py")
    
    if not os.path.exists(overlay_script):
        print(f"Error: {overlay_script} not found")
        return

    # 非同期実行
    subprocess.Popen([sys.executable, overlay_script, "type", msg])

if __name__ == "__main__":
    if len(sys.argv) > 1:
        msg = sys.argv[1]
    else:
        msg = get_jealous_cat_message()
    type_message(msg)
