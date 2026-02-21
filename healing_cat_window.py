#!/usr/bin/env python3
# healing_cat_window.py
# 癒やし猫（Cat A）のフローティングウィンドウ
# クリックでナデナデ → 嫉妬レベル上昇をゲーム状態に通知

import os
import sys
import random
import math

try:
    import tkinter as tk
    from PIL import Image, ImageTk
except ImportError:
    print("❌ tkinter and pillow are required. Run: pip install Pillow")
    sys.exit(1)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HEALING_CAT_IMG = os.path.join(BASE_DIR, "assets", "healing_cat_sprite.png")

# ─── ハートパーティクル ───
class HeartParticle:
    """クリック時に飛ぶハートの演出"""
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-4, -1.5)
        self.life = 1.0
        self.size = random.randint(14, 24)
        hearts = ["❤️", "🧡", "💛", "💖", "💕", "✨", "🐾"]
        self.char = random.choice(hearts)
        self.id = canvas.create_text(
            x, y, text=self.char,
            font=("Arial", self.size),
            fill="white", anchor="center"
        )

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.05  # 微重力
        self.life -= 0.03
        self.canvas.coords(self.id, self.x, self.y)
        if self.life <= 0:
            self.canvas.delete(self.id)
            return False
        return True


class HealingCatWindow:
    """癒やし猫のフローティングウィンドウ"""

    WINDOW_SIZE = 220
    PURR_MESSAGES = [
        "にゃ〜ん♪", "ゴロゴロ...", "すりすり♡",
        "もっとナデナデ〜", "うにゃ♪", "ぷるるる...",
        "ミャー♪", "...zzz", "にゃふ♡",
    ]

    def __init__(self, game_state=None):
        self.game_state = game_state
        self.root = tk.Tk()
        self.root.title("Cat A — 癒やし猫")

        # ─── ウィンドウ設定（枠なし・透明・最前面） ───
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-transparent", True)
        self.root.config(bg='systemTransparent')

        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()

        # 初期位置: 画面右下
        start_x = self.screen_w - self.WINDOW_SIZE - 60
        start_y = self.screen_h - self.WINDOW_SIZE - 120
        self.root.geometry(f"{self.WINDOW_SIZE}x{self.WINDOW_SIZE + 50}+{start_x}+{start_y}")

        # ─── キャンバス（透明背景にアニメーション描画） ───
        self.canvas = tk.Canvas(
            self.root,
            width=self.WINDOW_SIZE,
            height=self.WINDOW_SIZE + 50,
            bg='systemTransparent',
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill="both", expand=True)

        # ─── 嫉妬ゲージ（背景） ───
        self.gauge_bg = self.canvas.create_rectangle(
            40, self.WINDOW_SIZE + 35, 
            self.WINDOW_SIZE - 40, self.WINDOW_SIZE + 45,
            fill="#444444", outline="", width=0
        )
        # ─── 嫉妬ゲージ（中身） ───
        self.gauge_fill = self.canvas.create_rectangle(
            40, self.WINDOW_SIZE + 35, 
            40, self.WINDOW_SIZE + 45,
            fill="#00FF00", outline="", width=0
        )
        # ─── 嫉妬ゲージ（ラベル） ───
        self.gauge_label = self.canvas.create_text(
            self.WINDOW_SIZE // 2, self.WINDOW_SIZE + 25,
            text="Jealousy: 0%", font=("Arial", 9, "bold"), fill="white"
        )

        # ─── 猫画像をロード ───
        self.cat_photo = None
        self.load_cat_image()

        # ─── 猫を描画 ───
        cx = self.WINDOW_SIZE // 2
        cy = self.WINDOW_SIZE // 2
        if self.cat_photo:
            self.cat_id = self.canvas.create_image(cx, cy, image=self.cat_photo, anchor="center")
        else:
            self.cat_id = self.canvas.create_text(cx, cy, text="🐱", font=("Arial", 80))

        # ─── 「ナデナデしてね」吹き出し ───
        self.bubble_y_base = self.WINDOW_SIZE + 10
        self.bubble_id = self.canvas.create_text(
            cx, self.bubble_y_base,
            text="🐱 ナデナデしてね♪",
            font=("Helvetica Neue", 11, "bold"),
            fill="#FFD700",
            anchor="center",
        )

        # ─── パーティクル管理 ───
        self.particles = []
        self.pet_count = 0

        # ─── アニメーション状態 ───
        self.float_angle = 0.0
        self.is_purring = False
        self.purr_frames = 0
        self.jump_y = 0.0
        self.jump_vy = 0.0
        self.original_img = None

        # ─── ドラッグ移動 ───
        self.drag_data = {"x": 0, "y": 0}
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self._drag_valid = False

        # ─── アニメーションループ ───
        self.animate()

    def load_cat_image(self):
        """猫画像を円形クリップ風にリサイズして読み込む"""
        try:
            img = Image.open(HEALING_CAT_IMG).convert("RGBA")
            size = self.WINDOW_SIZE - 40 # 回転時に見切れないよう少し小さく

            # Pillowのバージョン互換性対応
            try:
                resample_filter = Image.Resampling.LANCZOS
            except AttributeError:
                resample_filter = Image.LANCZOS

            img = img.resize((size, size), resample_filter)

            # 円形マスクを適用
            mask = Image.new("L", (size, size), 0)
            from PIL import ImageDraw
            draw = ImageDraw.Draw(mask)
            draw.ellipse([0, 0, size, size], fill=255)
            img.putalpha(mask)

            self.original_img = img
            self.cat_photo = ImageTk.PhotoImage(img)
            print("✅ 猫画像をロードしました")
        except Exception as e:
            print(f"⚠️ Could not load cat image: {e}")
            self.cat_photo = None
            self.original_img = None

    def on_click(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        self._drag_valid = False

    def on_drag(self, event):
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        if abs(dx) > 5 or abs(dy) > 5:
            self._drag_valid = True

        x = self.root.winfo_x() + dx
        y = self.root.winfo_y() + dy
        self.root.geometry(f"+{x}+{y}")

    def on_release(self, event):
        if self._drag_valid:
            return  # ドラッグだったのでナデナデ判定しない

        # ── ナデナデ実行！ ──
        self.pet_count += 1
        self.is_purring = True
        self.purr_frames = 20
        
        # ぴょんとジャンプ！
        if self.jump_y == 0:
            self.jump_vy = -12

        # 吹き出しを更新
        msg = random.choice(self.PURR_MESSAGES)
        self.canvas.itemconfig(self.bubble_id, text=f"💖 {msg}")

        # ハートパーティクルを飛ばす
        for _ in range(random.randint(3, 6)):
            px = event.x + random.randint(-30, 30)
            py = event.y + random.randint(-20, 20)
            self.particles.append(HeartParticle(self.canvas, px, py))

        # ゲーム状態に通知
        if self.game_state:
            self.game_state.on_pet()

    def animate(self):
        """毎フレームのアニメーション（浮遊 + パーティクル + 振動）"""
        # 常に最前面を維持（ブラウザなどの裏に行かないように）
        self.root.lift()
        self.root.wm_attributes("-topmost", True)

        cx = self.WINDOW_SIZE // 2
        cy = self.WINDOW_SIZE // 2

        # ─── ゲージ更新 ───
        if self.game_state:
            level = self.game_state.jealousy_level
            # 0〜100% → 幅 0〜(WINDOW_SIZE-80)
            max_w = self.WINDOW_SIZE - 80
            current_w = max_w * (min(level, 100) / 100)
            
            # 色の変化: 緑 → 黄 → 赤
            if level < 50:
                color = "#00FF00" # Green
            elif level < 80:
                color = "#FFFF00" # Yellow
            else:
                color = "#FF0000" # Red
            
            self.canvas.coords(self.gauge_fill, 40, self.WINDOW_SIZE + 35, 40 + current_w, self.WINDOW_SIZE + 45)
            self.canvas.itemconfig(self.gauge_fill, fill=color)
            self.canvas.itemconfig(self.gauge_label, text=f"Jealousy: {int(level)}%")

        # ─── 物理演算（ジャンプ） ───
        if self.jump_y < 0 or self.jump_vy != 0:
            self.jump_y += self.jump_vy
            self.jump_vy += 1.5 # 重力
            if self.jump_y >= 0:
                self.jump_y = 0
                self.jump_vy = 0

        # ─── 浮遊アニメーション ───
        self.float_angle += 0.05
        float_offset = math.sin(self.float_angle) * 4

        # ─── 喜び振動 ───
        shake_x, shake_y = 0, 0
        if self.is_purring and self.purr_frames > 0:
            shake_x = random.uniform(-2, 2)
            shake_y = random.uniform(-1, 1)
            self.purr_frames -= 1
            if self.purr_frames <= 0:
                self.is_purring = False
                self.canvas.itemconfig(self.bubble_id, text="🐱 ナデナデしてね♪")
        
        # ─── 画像の回転（ゆらゆら） ───
        if self.original_img:
            tilt = math.sin(self.float_angle * 0.8) * 4 # ±4度
            try:
                # Pillowのバージョン互換性対応
                try:
                    resample_filter = Image.Resampling.BILINEAR
                except AttributeError:
                    resample_filter = Image.BILINEAR
                
                rotated = self.original_img.rotate(tilt, resample=resample_filter)
                self.cat_photo = ImageTk.PhotoImage(rotated)
                self.canvas.itemconfig(self.cat_id, image=self.cat_photo)
            except Exception:
                pass

        # 座標更新（中心位置 + 浮遊 + ジャンプ + 振動）
        total_y = cy + float_offset + self.jump_y + shake_y
        self.canvas.coords(self.cat_id, cx + shake_x, total_y)

        # ─── パーティクル更新 ───
        self.particles = [p for p in self.particles if p.update()]

        self.root.after(33, self.animate)  # ~30fps

    def run(self):
        self.root.mainloop()


# ─── スタンドアロン実行用 ───
if __name__ == "__main__":
    win = HealingCatWindow()
    win.run()
