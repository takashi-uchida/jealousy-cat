#!/usr/bin/env python3
# healing_cat_window.py
# 癒やし猫（Cat A）のフローティングウィンドウ
# クリックでナデナデ → 嫉妬レベル上昇をゲーム状態に通知

import os
import sys
import random
import math
import time

try:
    import tkinter as tk
    from PIL import Image, ImageTk
except ImportError:
    print("❌ tkinter and pillow are required. Run: pip install Pillow")
    sys.exit(1)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HEALING_CAT_IMG = os.path.join(BASE_DIR, "assets", "healing_cat_sprite.png")
HEALING_CAT_HAPPY_IMG = os.path.join(BASE_DIR, "assets", "healing_cat_happy.png")

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
        self.original_happy_img = None
        self.cat_happy_photo = None
        
        # 瞬き用
        self.blink_timer = random.randint(100, 300)
        self.is_blinking = False
        self.blink_duration = 0

        self.last_pet_time = 0

        # ─── 移動ロジック（Wandering） ───
        self.move_state = "IDLE" # IDLE | MOVING
        self.idle_timer = random.randint(60, 120)
        self.target_x = start_x
        self.target_y = start_y
        self.vx = 0
        self.vy = 0
        self.is_facing_right = False # 初期画像が左向きならFalse, 右向きならTrueに合わせて調整（今回は左向き想定でFalseが左？）
        # ※ healing_cat_sprite.png の向き次第ですが、一旦デフォルト左向きと仮定し、移動方向で反転させます

        # ─── ドラッグ移動 ───
        self.drag_data = {"x": 0, "y": 0}
        self.root.bind("<Button-1>", self.on_click)
        self.root.bind("<B1-Motion>", self.on_drag)
        self.root.bind("<ButtonRelease-1>", self.on_release)
        
        # ホバー（ナデナデ）検知
        self.root.bind("<Motion>", self.on_motion)
        self.root.bind("<Enter>", self.on_enter)
        
        self._drag_valid = False

        # ─── アニメーションループ ───
        self.root.focus_force() # 初期フォーカス
        self.animate()

    def load_cat_image(self):
        """通常と喜んでいる時の猫画像を読み込む"""
        try:
            # 通常画像
            img = Image.open(HEALING_CAT_IMG).convert("RGBA")
            # 喜び画像
            happy_img = Image.open(HEALING_CAT_HAPPY_IMG).convert("RGBA") if os.path.exists(HEALING_CAT_HAPPY_IMG) else img.copy()

            size = self.WINDOW_SIZE - 40

            try:
                resample_filter = Image.Resampling.LANCZOS
            except AttributeError:
                resample_filter = Image.LANCZOS

            img = img.resize((size, size), resample_filter)
            happy_img = happy_img.resize((size, size), resample_filter)

            # 円形マスクを適用
            mask = Image.new("L", (size, size), 0)
            from PIL import ImageDraw
            draw = ImageDraw.Draw(mask)
            draw.ellipse([0, 0, size, size], fill=255)
            
            img.putalpha(mask)
            happy_img.putalpha(mask)

            self.original_img = img
            self.original_happy_img = happy_img
            
            self.cat_photo = ImageTk.PhotoImage(img)
            self.cat_happy_photo = ImageTk.PhotoImage(happy_img)
            print("✅ 猫画像（通常＆喜び）をロードしました")
        except Exception as e:
            print(f"⚠️ Could not load cat images: {e}")
            self.cat_photo = None
            self.cat_happy_photo = None
            self.original_img = None
            self.original_happy_img = None

    def on_enter(self, event):
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y
        self.pet_accumulated_dist = 0

    def on_motion(self, event):
        # ドラッグ中はナデナデ判定しない
        if self._drag_valid:
            return

        # 前回の座標との距離を計算
        dx = event.x - self.last_mouse_x
        dy = event.y - self.last_mouse_y
        dist = math.sqrt(dx*dx + dy*dy)
        
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y
        
        # 距離を累積
        # もしカーソルが飛びすぎた場合（ウィンドウ外から入ってきた時など）は累積しない
        if dist < 100:
            self.pet_accumulated_dist += dist
            # print(f"Pet dist: {self.pet_accumulated_dist}") # Debug
        else:
            self.pet_accumulated_dist = 0
        
        # 一定距離（例: 150px）以上動かし、かつクールダウン（0.3秒）経過していればナデナデ判定
        now = time.time()
        if self.pet_accumulated_dist > 150 and (now - self.last_pet_time > 0.3):
            self.pet_cat(event)
            self.pet_accumulated_dist = 0 # リセット

    def pet_cat(self, event):
        """ナデナデ実行処理"""
        self.last_pet_time = time.time()
        self.pet_count += 1
        self.is_purring = True
        self.purr_frames = 20
        
        # ぴょんとジャンプ！
        if self.jump_y == 0:
            self.jump_vy = -8 # ジャンプ力は少し控えめに（連続で起きるので）

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
        # ドラッグ終了時の処理（クリックでのナデナデは廃止し、ホバーのみにする）
        self._drag_valid = False

    def animate(self):
        """毎フレームのアニメーション（浮遊 + パーティクル + 振動）"""
        try:
            # 終了シグナルチェック
            if self.game_state and not self.game_state.is_running:
                self.root.destroy()
                return

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

            # ─── Wandering Logic (自律移動) ───
            if not self._drag_valid: # ドラッグ中でなければ移動
                if self.move_state == "IDLE":
                    self.idle_timer -= 1
                    if self.idle_timer <= 0:
                        self.move_state = "MOVING"
                        # 次の目的地をランダム決定 (画面内)
                        margin = 50
                        max_x = self.screen_w - self.WINDOW_SIZE - margin
                        max_y = self.screen_h - self.WINDOW_SIZE - margin
                        self.target_x = random.randint(margin, max(margin, max_x))
                        self.target_y = random.randint(margin, max(margin, max_y))
                        
                        # 移動開始時刻
                        self.start_x = self.root.winfo_x()
                        self.start_y = self.root.winfo_y()
                        
                        # 距離計算
                        dx = self.target_x - self.start_x
                        dy = self.target_y - self.start_y
                        self.move_dist = math.sqrt(dx*dx + dy*dy)
                        if self.move_dist == 0: self.move_dist = 1
                        
                        # 移動にかける時間 (距離 / 平均速度)
                        avg_speed = random.uniform(3.0, 6.0) # ピクセル/フレーム
                        self.move_duration_frames = int(self.move_dist / avg_speed)
                        if self.move_duration_frames < 10: self.move_duration_frames = 10
                        self.move_frame_count = 0

                elif self.move_state == "MOVING":
                    self.move_frame_count += 1
                    
                    # 進捗率 (0.0 -> 1.0)
                    progress = self.move_frame_count / self.move_duration_frames
                    
                    if progress >= 1.0:
                        # 到着
                        self.root.geometry(f"+{int(self.target_x)}+{int(self.target_y)}")
                        self.move_state = "IDLE"
                        # 休憩時間: 短い休憩(70%) or 長い休憩(30%)
                        if random.random() < 0.7:
                            self.idle_timer = random.randint(30, 90) # 1~3秒
                        else:
                            self.idle_timer = random.randint(120, 240) # 4~8秒（毛づくろい等）
                    else:
                        # イージング (Ease In Out Quad)
                        t = progress
                        if t < 0.5:
                            ease = 2 * t * t
                        else:
                            ease = -1 + (4 - 2 * t) * t
                        
                        # 現在位置の計算
                        dx = self.target_x - self.start_x
                        dy = self.target_y - self.start_y
                        
                        # 寄り道（Wobble）
                        wobble_amp = 30.0 * math.sin(progress * math.pi) 
                        nx, ny = -dy, dx
                        n_len = math.sqrt(nx*nx + ny*ny)
                        if n_len > 0:
                            nx /= n_len
                            ny /= n_len
                        
                        base_x = self.start_x + dx * ease
                        base_y = self.start_y + dy * ease
                        
                        final_x = base_x + nx * wobble_amp * math.sin(self.move_frame_count * 0.1)
                        final_y = base_y + ny * wobble_amp * math.sin(self.move_frame_count * 0.1)
                        
                        # 歩行の上下動（Bouncing）: トコトコ感
                        bounce = abs(math.sin(self.move_frame_count * 0.5)) * 10
                        final_y -= bounce
                        
                        # 向き判定
                        curr_x = self.root.winfo_x()
                        diff_x = final_x - curr_x
                        if abs(diff_x) > 1.0:
                            self.is_facing_right = (diff_x > 0)

                        self.root.geometry(f"+{int(final_x)}+{int(final_y)}")

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
            
            # ─── 画像の変形（回転・呼吸・瞬き・反転） ───
            if self.original_img:
                # 1. 呼吸（ゆっくり拡大縮小）
                breath_scale = 1.0 + math.sin(self.float_angle * 0.1) * 0.02
                
                # 2. 瞬き（ランダムに目を閉じる = 縦につぶす）
                self.blink_timer -= 1
                if self.blink_timer <= 0:
                    self.is_blinking = True
                    self.blink_duration = 5 # 5フレーム閉じる
                    self.blink_timer = random.randint(100, 300) # 次の瞬きまで

                if self.is_blinking:
                    self.blink_duration -= 1
                    if self.blink_duration <= 0:
                        self.is_blinking = False
                    scale_y = 0.1 # 目を閉じた状態（縦につぶす）
                else:
                    scale_y = breath_scale

                scale_x = breath_scale

                # 3. 回転（ゆらゆら）
                tilt = math.sin(self.float_angle * 0.8) * 4 # ±4度
                
                try:
                    # Pillowのバージョン互換性対応
                    try:
                        resample_filter = Image.Resampling.BILINEAR
                    except AttributeError:
                        resample_filter = Image.BILINEAR
                    try:
                        flip_method = Image.Transpose.FLIP_LEFT_RIGHT
                    except AttributeError:
                        flip_method = Image.FLIP_LEFT_RIGHT

                    # 反転（向き）と表情の選択
                    base_img = self.original_happy_img if self.is_purring else self.original_img
                    if self.is_facing_right:
                        base_img = base_img.transpose(flip_method)

                    # 回転
                    transformed = base_img.rotate(tilt, resample=resample_filter)
                    
                    # スケール変更（呼吸・瞬き）
                    w, h = transformed.size
                    new_w = int(w * scale_x)
                    new_h = int(h * scale_y)
                    if new_w > 0 and new_h > 0:
                        transformed = transformed.resize((new_w, new_h), resample=resample_filter)
                    
                    # PhotoImageの更新
                    # （注: ここで毎回 PhotoImage を作るのはあまり効率的ではないが、既存のコードに倣う）
                    self.cat_current_photo = ImageTk.PhotoImage(transformed)
                    self.canvas.itemconfig(self.cat_id, image=self.cat_current_photo)
                except Exception:
                    pass

            # 座標更新（中心位置 + 浮遊 + ジャンプ + 振動）
            total_y = cy + float_offset + self.jump_y + shake_y
            self.canvas.coords(self.cat_id, cx + shake_x, total_y)

            # ─── パーティクル更新 ───
            self.particles = [p for p in self.particles if p.update()]

        except Exception as e:
            print(f"⚠️ Animation Error: {e}")

        self.root.after(33, self.animate)  # ~30fps

    def run(self):
        self.root.mainloop()


# ─── スタンドアロン実行用 ───
if __name__ == "__main__":
    win = HealingCatWindow()
    win.run()
