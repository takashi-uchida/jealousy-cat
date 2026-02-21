#!/usr/bin/env python3
# type_msg.py
# TextEditを起動し、タイプライターのようにメッセージを打ち込む（嫉妬の表現）

import sys
import subprocess
import time
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
    print(f"📝 メッセージをタイピングしています...: {msg}")
    # TextEditを起動して新規ドキュメントを開く
    setup_script = """
    tell application "TextEdit"
        activate
        make new document
    end tell
    """
    subprocess.run(["osascript", "-e", setup_script])
    time.sleep(1.0) # ウィンドウが準備されるまで待つ

    # クリップボードを保存
    original_clipboard = subprocess.run(["pbpaste"], capture_output=True, text=True).stdout or ""

    # ゆっくりタイピング（感情を込める）
    # IME（日本語入力）の影響を回避するため、クリップボード経由でペーストします
    for char in msg:
        if char == "\n":
            script = 'tell application "System Events" to keystroke return'
            subprocess.run(["osascript", "-e", script])
        else:
            # 1文字をクリップボードにコピー
            subprocess.run(["pbcopy"], input=char, text=True)
            # Cmd+Vをシミュレート
            script = 'tell application "System Events" to keystroke "v" using command down'
            subprocess.run(["osascript", "-e", script])
        
        time.sleep(0.12) # 少し重めのタイピングスピード（イライラ / 拗ねを表現）
        
    # クリップボードを復元
    subprocess.run(["pbcopy"], input=original_clipboard, text=True)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        msg = sys.argv[1]
    else:
        msg = get_jealous_cat_message()
    type_message(msg)
