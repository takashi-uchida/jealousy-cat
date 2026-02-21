#!/usr/bin/env python3
# type_msg.py
# TextEditを起動し、タイプライターのようにメッセージを打ち込む（嫉妬の表現）

import sys
import subprocess
import time

def type_message(msg):
    print("📝 メッセージをタイピングしています...")
    # TextEditを起動して新規ドキュメントを開く
    setup_script = """
    tell application "TextEdit"
        activate
        make new document
    end tell
    """
    subprocess.run(["osascript", "-e", setup_script])
    time.sleep(1.0) # ウィンドウが準備されるまで待つ

    # ゆっくりタイピング（感情を込める）
    for char in msg:
        if char == "\n":
            script = 'tell application "System Events" to keystroke return'
        else:
            # エスケープ処理
            escaped_char = char.replace('"', '\\"').replace('\\', '\\\\')
            script = f'tell application "System Events" to keystroke "{escaped_char}"'
        
        subprocess.run(["osascript", "-e", script])
        time.sleep(0.12) # 少し重めのタイピングスピード（イライラ / 拗ねを表現）

if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else "ボクだけを見て... 他の子ばっかり見ないで..."
    type_message(msg)
