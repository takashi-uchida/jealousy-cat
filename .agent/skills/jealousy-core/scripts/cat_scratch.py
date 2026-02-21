#!/usr/bin/env python3
# cat_scratch.py
# 画面に爪痕を残す（オーバーレイ版）

import sys
import subprocess
import os

def cat_scratch_screen():
    # 同じディレクトリにある overlay_effects.py を実行
    script_dir = os.path.dirname(os.path.abspath(__file__))
    overlay_script = os.path.join(script_dir, "overlay_effects.py")
    
    if not os.path.exists(overlay_script):
        print(f"Error: {overlay_script} not found")
        return

    print("🐱 爪痕を残します...")
    # 非同期（バックグラウンド）で実行して、呼び出し元をブロックしない
    subprocess.Popen([sys.executable, overlay_script, "scratch"])

if __name__ == "__main__":
    cat_scratch_screen()
