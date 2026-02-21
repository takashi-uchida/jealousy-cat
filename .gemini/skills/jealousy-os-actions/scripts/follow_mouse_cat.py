#!/usr/bin/env python3
# follow_mouse_cat.py
# マウスカーソルを追いかける猫を表示するスクリプト

import sys
import os
import time

try:
    import tkinter as tk
    from PIL import Image, ImageTk
except ImportError:
    print("tkinter and pillow are required for this script")
    sys.exit(1)

class FollowMouseCat:
    def __init__(self, root):
        self.root = root
        
        # タイトル・枠線を消す
        self.root.overrideredirect(True)
        # 常に最前面に表示
        self.root.wm_attributes("-topmost", True)
        # マウスイベントを透過させない（猫自体は掴めるように）
        # ただし、クリックがブラウザに届かないと困る場合は調整が必要
        
        # macOS専用の透明背景化
        self.root.wm_attributes("-transparent", True)
        self.root.config(bg='systemTransparent')
        
        # 追加: フォーカスを奪わないように設定（マウス操作の邪魔をしすぎない）
        self.root.attributes("-hidetitlebar", True)
        
        # アセットのパス
        # scripts -> jealousy-core -> skills -> .agent -> jealousy-cat
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
        self.asset_path = os.path.join(project_root, "assets", "walking_black_cat.png")
        
        # アニメーション設定
        self.frames = []
        try:
            full_img = Image.open(self.asset_path)
            # 640x640, 3 columns x 4 rows (assuming same format as walking_black_cat.png)
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
                    frame = frame.resize((100, 100), Image.Resampling.LANCZOS)
                    self.frames.append(ImageTk.PhotoImage(frame))
        except Exception as e:
            print(f"Error loading animated sprite: {e}")
            self.frames = None

        self.index = 0
        if self.frames:
            self.label = tk.Label(self.root, image=self.frames[self.index], bg='systemTransparent')
        else:
            self.label = tk.Label(self.root, text="🐈‍⬛", font=("Arial", 60), bg='systemTransparent', fg='black')
            
        self.label.pack(expand=True, fill="both")
        
        # 初期位置
        self.x, self.y = self.root.winfo_pointerxy()
        
        self.update_animation()
        self.update_position()

    def update_animation(self):
        if self.frames:
            self.index = (self.index + 1) % len(self.frames)
            self.label.configure(image=self.frames[self.index])
        self.root.after(100, self.update_animation)

    def update_position(self):
        # マウスの位置を取得
        mx, my = self.root.winfo_pointerxy()
        
        # マウスに向かって少しずつ移動（追従）
        # 猫の中心がマウスに来るようにオフセット
        target_x = mx - 50
        target_y = my - 50
        
        # 滑らかに動かすために線形補間
        self.x += (target_x - self.x) * 0.15
        self.y += (target_y - self.y) * 0.15
        
        self.root.geometry(f"100x100+{int(self.x)}+{int(self.y)}")
        self.root.after(20, self.update_position)

if __name__ == "__main__":
    root = tk.Tk()
    cat = FollowMouseCat(root)
    # 2秒後に自動で終了するように設定（デモ用）
    # root.after(5000, root.destroy) 
    root.mainloop()
