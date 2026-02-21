#!/usr/bin/env python3
# overlay_effects.py
# 画面全体にオーバーレイ効果を表示する（爪痕、メッセージ、フラッシュ）
# 既存のアプリ起動（Preview, TextEdit）を置き換え、よりシームレスな妨害演出を行う

import sys
import time
import random
import tkinter as tk
from PIL import Image, ImageTk
import os

class OverlayEffect:
    def __init__(self, duration=3.0):
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-fullscreen", True)
        
        # macOS特有の透明設定
        if sys.platform == "darwin":
            self.root.config(bg='systemTransparent')
            self.root.attributes("-transparent", True)
        else:
            self.root.config(bg='black')
            self.root.attributes("-alpha", 0.7)

        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()
        
        self.canvas = tk.Canvas(
            self.root, 
            width=self.screen_w, 
            height=self.screen_h, 
            bg='systemTransparent' if sys.platform == 'darwin' else 'black',
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        
        # 強制的に最前面へ
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.focus_force()

        # 終了タイマー
        self.root.after(int(duration * 1000), self.close)
        
        # クリックで消える（デバッグ用、本番では無効化してもいいがUX的には残すのもあり）
        self.canvas.bind("<Button-1>", lambda e: self.close())

    def close(self):
        self.root.destroy()
        sys.exit(0)

    def run(self):
        self.root.mainloop()

class ScratchEffect(OverlayEffect):
    def __init__(self, image_path, count=5):
        super().__init__(duration=2.0)
        self.image_path = image_path
        self.count = count
        self.images = [] # 参照保持用
        self.draw_scratches()

    def draw_scratches(self):
        if not os.path.exists(self.image_path):
            return

        try:
            original = Image.open(self.image_path).convert("RGBA")
            # 少し回転やサイズを変えてランダムに配置
            for _ in range(self.count):
                angle = random.uniform(-30, 30)
                scale = random.uniform(0.8, 1.5)
                
                w, h = original.size
                new_w = int(w * scale)
                new_h = int(h * scale)
                
                img = original.resize((new_w, new_h), Image.LANCZOS).rotate(angle, expand=True)
                photo = ImageTk.PhotoImage(img)
                self.images.append(photo)
                
                x = random.randint(0, self.screen_w - new_w)
                y = random.randint(0, self.screen_h - new_h)
                
                self.canvas.create_image(x, y, image=photo, anchor="nw")
                
                # 画面を赤くフラッシュさせる矩形も追加
                flash_id = self.canvas.create_rectangle(
                    0, 0, self.screen_w, self.screen_h, 
                    fill="#FF0000", outline=""
                )
                self.canvas.tag_lower(flash_id)
                
        except Exception as e:
            print(f"Error loading image: {e}")

class TypeMessageEffect(OverlayEffect):
    def __init__(self, message):
        # メッセージの長さに応じて時間を調整
        duration = max(3.0, len(message) * 0.2 + 2.0)
        super().__init__(duration=duration)
        self.message = message
        self.current_text = ""
        self.char_index = 0
        
        # 中央に背景帯
        self.bg_rect = self.canvas.create_rectangle(
            0, self.screen_h // 2 - 60, 
            self.screen_w, self.screen_h // 2 + 60,
            fill="#000000", outline=""
        )
        if sys.platform == 'darwin':
             # tkinterのcanvas itemにはalphaがないので、stippleを使うか、
             # 諦めて黒帯にする。今回は黒帯でOK（不気味さを出す）。
             pass

        self.text_id = self.canvas.create_text(
            self.screen_w // 2, self.screen_h // 2,
            text="",
            font=("Courier New", 36, "bold"),
            fill="#FF0000",
            anchor="center",
            width=self.screen_w - 100
        )
        
        self.type_next_char()

    def type_next_char(self):
        if self.char_index < len(self.message):
            char = self.message[self.char_index]
            self.current_text += char
            self.canvas.itemconfig(self.text_id, text=self.current_text + " █") # カーソル
            self.char_index += 1
            
            delay = random.randint(50, 150)
            if char in [",", ".", "...", "!", "?", ";"]:
                delay += 300
            
            self.root.after(delay, self.type_next_char)
        else:
            # 点滅カーソルのみ
            self.blink_cursor()

    def blink_cursor(self):
        current = self.canvas.itemcget(self.text_id, "text")
        if "█" in current:
            new_text = current.replace(" █", "")
        else:
            new_text = current + " █"
        self.canvas.itemconfig(self.text_id, text=new_text)
        self.root.after(500, self.blink_cursor)

class PopupEffect(OverlayEffect):
    def __init__(self, image_path, title, message, sound_path=None, duration=3.0):
        super().__init__(duration=duration)
        self.image_path = image_path
        self.title = title
        self.message = message
        self.sound_path = sound_path
        
        # 半透明の黒背景（シミュレーション）
        # tkinterのcanvasでalphaは難しいので、stipple="gray50"などで代用するか
        # 全画面黒背景（透過ウィンドウ設定済み）の上に描画する
        
        cx = self.screen_w // 2
        cy = self.screen_h // 2
        
        # 背景プレート
        self.canvas.create_rectangle(
            cx - 300, cy - 200, cx + 300, cy + 200,
            fill="#222222", outline="#FFD700", width=4
        )
        
        # 画像
        self.photo = None
        if os.path.exists(self.image_path):
            try:
                img = Image.open(self.image_path).convert("RGBA")
                img = img.resize((128, 128), Image.LANCZOS)
                self.photo = ImageTk.PhotoImage(img)
                self.canvas.create_image(cx, cy - 50, image=self.photo, anchor="center")
            except Exception:
                pass
        else:
            self.canvas.create_text(cx, cy - 50, text="🐈‍⬛", font=("Arial", 80), fill="white")

        # タイトル
        self.canvas.create_text(
            cx, cy - 150, text=self.title,
            font=("Helvetica", 24, "bold"), fill="#FFD700", anchor="center"
        )
        
        # メッセージ
        self.canvas.create_text(
            cx, cy + 80, text=self.message,
            font=("Helvetica", 18), fill="white", anchor="center", width=500
        )
        
        # サウンド再生
        if self.sound_path and os.path.exists(self.sound_path):
            import subprocess
            subprocess.Popen(["afplay", self.sound_path])
        elif self.sound_path == "default":
            # システム音
            import subprocess
            subprocess.Popen(["afplay", "/System/Library/Sounds/Ping.aiff"])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python overlay_effects.py [scratch|type|popup] [args...]")
        sys.exit(1)

    mode = sys.argv[1]
    
    if mode == "scratch":
        # python overlay_effects.py scratch /path/to/image.png
        if len(sys.argv) > 2:
            img_path = sys.argv[2]
        else:
            # デフォルトパス
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            img_path = os.path.join(base_dir, "assets", "scratch_mark.png")
            
        app = ScratchEffect(img_path)
        app.run()
        
    elif mode == "type":
        # python overlay_effects.py type "メッセージ内容"
        if len(sys.argv) > 2:
            msg = sys.argv[2]
        else:
            msg = "Don't ignore me..."
        app = TypeMessageEffect(msg)
        app.run()

    elif mode == "popup":
        # python overlay_effects.py popup img_path title message [sound_path]
        img = sys.argv[2] if len(sys.argv) > 2 else ""
        title = sys.argv[3] if len(sys.argv) > 3 else "Notification"
        msg = sys.argv[4] if len(sys.argv) > 4 else ""
        snd = sys.argv[5] if len(sys.argv) > 5 else None
        
        app = PopupEffect(img, title, msg, snd)
        app.run()
