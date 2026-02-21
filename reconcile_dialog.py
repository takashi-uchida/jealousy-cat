#!/usr/bin/env python3
# reconcile_dialog.py
# 和解用のダイアログランチャー
# reconcile_gui.py (tkinter版) を呼び出して結果を受け取る

import subprocess
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 通常の配置場所: .agent/skills/jealousy-core/scripts/
# もしルート直下に配置されている場合のフォールバックも考慮
GUI_SCRIPT = os.path.join(SCRIPT_DIR, ".agent", "skills", "jealousy-core", "scripts", "reconcile_gui.py")
if not os.path.exists(GUI_SCRIPT):
     # 同じディレクトリにある場合
    GUI_SCRIPT = os.path.join(SCRIPT_DIR, "reconcile_gui.py")

def show_reconcile_sequence():
    """tkinter版のGUIを起動"""
    print(f"Debug: Trying to launch GUI script at: {GUI_SCRIPT}")
    if not os.path.exists(GUI_SCRIPT):
        print(f"Error: GUI script NOT FOUND at {GUI_SCRIPT}")
        # Try to find it recursively? No, just fail explicitly.
        return False, ""

    try:
        # GUIスクリプトを実行
        cmd = [sys.executable, GUI_SCRIPT]
        print(f"Debug: Running command: {cmd}")
        
        result = subprocess.run(
            cmd,
            capture_output=True, text=True
        )
        
        if result.returncode == 0:
            # 成功時、stdoutの最後の行が入力テキストの可能性が高いが、
            # printデバッグが混じっているかもしれないので strip してそのまま返す
            user_text = result.stdout.strip().split('\n')[-1] if result.stdout.strip() else "仲直り"
            return True, user_text
        else:
            if result.stderr:
                print(f"❌ GUI Error: {result.stderr}")
            return False, ""
            
    except Exception as e:
        print(f"Error launching GUI: {e}")
        return False, ""

if __name__ == "__main__":
    success, text = show_reconcile_sequence()
    if success:
        print(f"Success: {text}")
        sys.exit(0)
    else:
        print("Failed")
        sys.exit(1)
