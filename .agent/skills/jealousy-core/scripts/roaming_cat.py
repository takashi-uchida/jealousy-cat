#!/usr/bin/env python3
# roaming_cat.py
# 画面上を猫（🐈）がうろうろ動き回るスクリプト（Computer Use / OS APIを利用した干渉）

import sys
import random
import os

try:
    import tkinter as tk
    from PIL import Image, ImageTk
except ImportError:
    print("tkinter and pillow are required for this script")
    sys.exit(1)

class RoamingCat:
    def __init__(self, root):
        self.root = root
        
        # タイトル・枠線を消す
        self.root.overrideredirect(True)
        # 常に最前面に表示
        self.root.wm_attributes("-topmost", True)
        
        # macOS専用の透明背景化
        self.root.wm_attributes("-transparent", True)
        self.root.config(bg='systemTransparent')
        
        # 画面サイズを取得
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # アセットのパス
        # scripts/ -> jealousy-core/ -> skills/ -> .agent/ -> project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
        self.asset_path = os.path.join(project_root, "assets", "walking_black_cat.png")
        
        # アニメーション設定
        self.frames = []
        try:
            full_img = Image.open(self.asset_path)
            # 640x640, 3 columns x 4 rows
            w, h = full_img.size
            cols, rows = 3, 4
            frame_w = w // cols
            frame_h = h // rows
            
            for r in range(rows):
                for c in range(cols):
                    left = c * frame_w
                    top = r * frame_h
                    right = left + frame_w
                    bottom = top + frame_h
                    frame = full_img.crop((left, top, right, bottom))
                    # Resize to be a bit smaller if needed, but 120 seems okay
                    frame = frame.resize((120, 120), Image.NEAREST)
                    self.frames.append(ImageTk.PhotoImage(frame))
        except Exception as e:
            print(f"Error loading animated sprite: {e}")
            self.frames = None

        self.index = 0
        if self.frames:
            self.label = tk.Label(self.root, image=self.frames[self.index], bg='systemTransparent')
        else:
            self.label = tk.Label(self.root, text="🐈‍⬛", font=("Arial", 80), bg='systemTransparent', fg='black')
            
        self.label.pack(expand=True, fill="both")
        
        # 初期位置と速度
        self.x = random.randint(100, self.screen_width - 120)
        self.y = random.randint(100, self.screen_height - 120)
        self.dx = random.choice([-4, -2, 2, 4])
        self.dy = random.choice([-2, -1, 1, 2])
        
        self.update_animation()
        self.update_position()

    def update_animation(self):
        if self.frames:
            self.index = (self.index + 1) % len(self.frames)
            self.label.configure(image=self.frames[self.index])
        self.root.after(150, self.update_animation) # 150ms per frame

    def update_position(self):
        self.x += self.dx
        self.y += self.dy
        
        if self.x <= 0 or self.x >= self.screen_width - 120:
            self.dx = -self.dx
        if self.y <= 0 or self.y >= self.screen_height - 120:
            self.dy = -self.dy
        
        if random.random() < 0.03:
            self.dx = max(-8, min(8, self.dx + random.choice([-1, 0, 1])))
            self.dy = max(-5, min(5, self.dy + random.choice([-1, 0, 1])))

        self.root.geometry(f"120x120+{int(self.x)}+{int(self.y)}")
        self.root.after(30, self.update_position)

if __name__ == "__main__":
    root = tk.Tk()
    cat = RoamingCat(root)
    root.mainloop()
