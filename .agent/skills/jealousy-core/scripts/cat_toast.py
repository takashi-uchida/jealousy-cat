#!/usr/bin/env python3
# cat_toast.py
# 猫が妨害を行ったことをユーザーに知らせるmacOS通知（トースト）を表示する

import sys
import subprocess
import random

# レベルに応じた猫のセリフ（サブタイトル）
LEVEL_SUBTITLES = {
    "1": [
        "...チッ",
        "ふーん、そっちが大事なんだ",
        "ちょっとだけ、イタズラするニャ",
    ],
    "2": [
        "ボクを無視するんだ？",
        "ねぇ、こっち見てよ...",
        "そろそろ本気出すニャ",
    ],
    "3": [
        "もう我慢の限界ニャ...",
        "どうして...ボクじゃダメなの？",
        "最終警告だニャ",
    ],
    "MAX": [
        "もう限界ニャ...",
        "全部終わりにしてやるニャ",
        "...さよなら",
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
    msg = sys.argv[2] if len(sys.argv) > 2 else "猫がイタズラしました"
    show_toast(lvl, msg)
