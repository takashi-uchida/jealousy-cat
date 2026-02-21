#!/usr/bin/env python3
# healing_cat_window.py
# Floating window for Healing Cat (Cat A)
# Clicking/Hovering triggers 'petting' and increases jealousy level in the system.

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

# ─── Heart Particles ───
class HeartParticle:
    """Explosion of hearts effect when petted"""
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
        self.vy += 0.05  # Slight gravity
        self.life -= 0.03
        self.canvas.coords(self.id, self.x, self.y)
        if self.life <= 0:
            self.canvas.delete(self.id)
            return False
        return True


class HealingCatWindow:
    """Floating window for the Healing Cat"""

    WINDOW_SIZE = 220
    PURR_MESSAGES = [
        "Meow~♪", "Purr...", "Nuzzle♡",
        "More pets~", "Mew♪", "Prrr...",
        "Miaow♪", "...zzz", "Nyah♡",
    ]

    def __init__(self, game_state=None):
        self.game_state = game_state
        self.root = tk.Tk()
        self.root.title("Cat A — Healing Cat")

        # ─── Window Setup (Frameless, Transparent, Topmost) ───
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.root.wm_attributes("-transparent", True)
        self.root.config(bg='systemTransparent')

        self.screen_w = self.root.winfo_screenwidth()
        self.screen_h = self.root.winfo_screenheight()

        # Initial Position: Bottom-right
        start_x = self.screen_w - self.WINDOW_SIZE - 60
        start_y = self.screen_h - self.WINDOW_SIZE - 120
        self.root.geometry(f"{self.WINDOW_SIZE}x{self.WINDOW_SIZE + 50}+{start_x}+{start_y}")

        # ─── Canvas (Drawing animation on transparent background) ───
        self.canvas = tk.Canvas(
            self.root,
            width=self.WINDOW_SIZE,
            height=self.WINDOW_SIZE + 50,
            bg='systemTransparent',
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill="both", expand=True)

        # ─── Jealousy Gauge (Background) ───
        self.gauge_bg = self.canvas.create_rectangle(
            40, self.WINDOW_SIZE + 35, 
            self.WINDOW_SIZE - 40, self.WINDOW_SIZE + 45,
            fill="#444444", outline="", width=0
        )
        # ─── Jealousy Gauge (Fill) ───
        self.gauge_fill = self.canvas.create_rectangle(
            40, self.WINDOW_SIZE + 35, 
            40, self.WINDOW_SIZE + 45,
            fill="#00FF00", outline="", width=0
        )
        # ─── Jealousy Gauge (Label) ───
        self.gauge_label = self.canvas.create_text(
            self.WINDOW_SIZE // 2, self.WINDOW_SIZE + 25,
            text="Jealousy: 0%", font=("Arial", 9, "bold"), fill="white"
        )

        # ─── Load Cat Images ───
        self.cat_photo = None
        self.load_cat_image()

        # ─── Draw Cat ───
        cx = self.WINDOW_SIZE // 2
        cy = self.WINDOW_SIZE // 2
        if self.cat_photo:
            self.cat_id = self.canvas.create_image(cx, cy, image=self.cat_photo, anchor="center")
        else:
            self.cat_id = self.canvas.create_text(cx, cy, text="🐱", font=("Arial", 80))

        # ─── "Pet me" Bubble ───
        self.bubble_y_base = self.WINDOW_SIZE + 10
        self.bubble_id = self.canvas.create_text(
            cx, self.bubble_y_base,
            text="🐱 Pet me♪",
            font=("Helvetica Neue", 11, "bold"),
            fill="#FFD700",
            anchor="center",
        )

        # ─── Particle Management ───
        self.particles = []
        self.pet_count = 0

        # ─── Animation State ───
        self.float_angle = 0.0
        self.is_purring = False
        self.purr_frames = 0
        self.jump_y = 0.0
        self.jump_vy = 0.0
        self.original_img = None
        self.original_happy_img = None
        self.cat_happy_photo = None
        
        # Blink control
        self.blink_timer = random.randint(100, 300)
        self.is_blinking = False
        self.blink_duration = 0

        self.last_pet_time = 0

        # ─── Movement Logic (Wandering) ───
        self.move_state = "IDLE" # IDLE | MOVING
        self.idle_timer = random.randint(60, 120)
        self.target_x = start_x
        self.target_y = start_y
        self.vx = 0
        self.vy = 0
        self.is_facing_right = False 

        # ─── Mouse Interaction ───
        self.drag_data = {"x": 0, "y": 0}
        self.root.bind("<Button-1>", self.on_click)
        self.root.bind("<B1-Motion>", self.on_drag)
        self.root.bind("<ButtonRelease-1>", self.on_release)
        
        # Hover (Petting) Detection
        self.root.bind("<Motion>", self.on_motion)
        self.root.bind("<Enter>", self.on_enter)
        
        self._drag_valid = False

        # ─── Animation Loop ───
        self.root.focus_force() 
        self.animate()

    def load_cat_image(self):
        """Loads regular and happy cat images"""
        try:
            img = Image.open(HEALING_CAT_IMG).convert("RGBA")
            happy_img = Image.open(HEALING_CAT_HAPPY_IMG).convert("RGBA") if os.path.exists(HEALING_CAT_HAPPY_IMG) else img.copy()

            size = self.WINDOW_SIZE - 40

            try:
                resample_filter = Image.Resampling.LANCZOS
            except AttributeError:
                resample_filter = Image.LANCZOS

            img = img.resize((size, size), resample_filter)
            happy_img = happy_img.resize((size, size), resample_filter)

            # Apply circular mask
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
            print("✅ Cat images (Normal & Happy) loaded successfully")
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
        if self._drag_valid:
            return

        dx = event.x - self.last_mouse_x
        dy = event.y - self.last_mouse_y
        dist = math.sqrt(dx*dx + dy*dy)
        
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y
        
        if dist < 100:
            self.pet_accumulated_dist += dist
        else:
            self.pet_accumulated_dist = 0
        
        now = time.time()
        if self.pet_accumulated_dist > 150 and (now - self.last_pet_time > 0.3):
            self.pet_cat(event)
            self.pet_accumulated_dist = 0 

    def pet_cat(self, event):
        """Pet execution logic"""
        self.last_pet_time = time.time()
        self.pet_count += 1
        self.is_purring = True
        self.purr_frames = 20
        
        if self.jump_y == 0:
            self.jump_vy = -8 

        msg = random.choice(self.PURR_MESSAGES)
        self.canvas.itemconfig(self.bubble_id, text=f"💖 {msg}")

        for _ in range(random.randint(3, 6)):
            px = event.x + random.randint(-30, 30)
            py = event.y + random.randint(-20, 20)
            self.particles.append(HeartParticle(self.canvas, px, py))

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
        self._drag_valid = False

    def animate(self):
        """Per-frame animation loop"""
        try:
            if self.game_state and not self.game_state.is_running:
                self.root.destroy()
                return

            if self.game_state and self.game_state.game_phase == "ending":
                if self.root.state() != "withdrawn":
                    self.root.withdraw()
                self.root.after(500, self.animate)
                return
            elif self.root.state() == "withdrawn":
                self.root.deiconify()

            self.root.lift()
            self.root.wm_attributes("-topmost", True)

            cx = self.WINDOW_SIZE // 2
            cy = self.WINDOW_SIZE // 2

            # ─── Gauge Update ───
            if self.game_state:
                level = self.game_state.jealousy_level
                max_w = self.WINDOW_SIZE - 80
                current_w = max_w * (min(level, 100) / 100)
                
                if level < 50:
                    color = "#00FF00" # Green
                elif level < 80:
                    color = "#FFFF00" # Yellow
                else:
                    color = "#FF0000" # Red
                
                self.canvas.coords(self.gauge_fill, 40, self.WINDOW_SIZE + 35, 40 + current_w, self.WINDOW_SIZE + 45)
                self.canvas.itemconfig(self.gauge_fill, fill=color)
                self.canvas.itemconfig(self.gauge_label, text=f"Jealousy: {int(level)}%")

            # ─── Wandering Logic ───
            if not self._drag_valid:
                if self.move_state == "IDLE":
                    self.idle_timer -= 1
                    if self.idle_timer <= 0:
                        self.move_state = "MOVING"
                        margin = 50
                        max_x = self.screen_w - self.WINDOW_SIZE - margin
                        max_y = self.screen_h - self.WINDOW_SIZE - margin
                        self.target_x = random.randint(margin, max(margin, max_x))
                        self.target_y = random.randint(margin, max(margin, max_y))
                        
                        self.start_x = self.root.winfo_x()
                        self.start_y = self.root.winfo_y()
                        
                        dx = self.target_x - self.start_x
                        dy = self.target_y - self.start_y
                        self.move_dist = math.sqrt(dx*dx + dy*dy)
                        if self.move_dist == 0: self.move_dist = 1
                        
                        avg_speed = random.uniform(3.0, 6.0) 
                        self.move_duration_frames = int(self.move_dist / avg_speed)
                        if self.move_duration_frames < 10: self.move_duration_frames = 10
                        self.move_frame_count = 0

                elif self.move_state == "MOVING":
                    self.move_frame_count += 1
                    progress = self.move_frame_count / self.move_duration_frames
                    
                    if progress >= 1.0:
                        self.root.geometry(f"+{int(self.target_x)}+{int(self.target_y)}")
                        self.move_state = "IDLE"
                        if random.random() < 0.7:
                            self.idle_timer = random.randint(30, 90) 
                        else:
                            self.idle_timer = random.randint(120, 240) 
                    else:
                        t = progress
                        if t < 0.5:
                            ease = 2 * t * t
                        else:
                            ease = -1 + (4 - 2 * t) * t
                        
                        dx = self.target_x - self.start_x
                        dy = self.target_y - self.start_y
                        
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
                        
                        bounce = abs(math.sin(self.move_frame_count * 0.5)) * 10
                        final_y -= bounce
                        
                        curr_x = self.root.winfo_x()
                        diff_x = final_x - curr_x
                        if abs(diff_x) > 1.0:
                            self.is_facing_right = (diff_x > 0)

                        self.root.geometry(f"+{int(final_x)}+{int(final_y)}")

            # ─── Physics (Jump) ───
            if self.jump_y < 0 or self.jump_vy != 0:
                self.jump_y += self.jump_vy
                self.jump_vy += 1.5 
                if self.jump_y >= 0:
                    self.jump_y = 0
                    self.jump_vy = 0

            # ─── Floating Animation ───
            self.float_angle += 0.05
            float_offset = math.sin(self.float_angle) * 4

            # ─── Purr Vibe ───
            shake_x, shake_y = 0, 0
            if self.is_purring and self.purr_frames > 0:
                shake_x = random.uniform(-2, 2)
                shake_y = random.uniform(-1, 1)
                self.purr_frames -= 1
                if self.purr_frames <= 0:
                    self.is_purring = False
                    self.canvas.itemconfig(self.bubble_id, text="🐱 Pet me♪")
            
            # ─── Image Transformations (Scaling, Breathing, Blinking, Flipped) ───
            if self.original_img:
                breath_scale = 1.0 + math.sin(self.float_angle * 0.1) * 0.02
                
                self.blink_timer -= 1
                if self.blink_timer <= 0:
                    self.is_blinking = True
                    self.blink_duration = 5 
                    self.blink_timer = random.randint(100, 300) 

                if self.is_blinking:
                    self.blink_duration -= 1
                    if self.blink_duration <= 0:
                        self.is_blinking = False
                    scale_y = 0.1 
                else:
                    scale_y = breath_scale

                scale_x = breath_scale

                tilt = math.sin(self.float_angle * 0.8) * 4 
                
                try:
                    try:
                        resample_filter = Image.Resampling.BILINEAR
                    except AttributeError:
                        resample_filter = Image.BILINEAR
                    try:
                        flip_method = Image.Transpose.FLIP_LEFT_RIGHT
                    except AttributeError:
                        flip_method = Image.FLIP_LEFT_RIGHT

                    base_img = self.original_happy_img if self.is_purring else self.original_img
                    if self.is_facing_right:
                        base_img = base_img.transpose(flip_method)

                    transformed = base_img.rotate(tilt, resample=resample_filter)
                    
                    w, h = transformed.size
                    new_w = int(w * scale_x)
                    new_h = int(h * scale_y)
                    if new_w > 0 and new_h > 0:
                        transformed = transformed.resize((new_w, new_h), resample=resample_filter)
                    
                    self.cat_current_photo = ImageTk.PhotoImage(transformed)
                    self.canvas.itemconfig(self.cat_id, image=self.cat_current_photo)
                except Exception:
                    pass

            total_y = cy + float_offset + self.jump_y + shake_y
            self.canvas.coords(self.cat_id, cx + shake_x, total_y)

            self.particles = [p for p in self.particles if p.update()]

        except Exception as e:
            print(f"⚠️ Animation Error: {e}")

        self.root.after(33, self.animate)  

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    win = HealingCatWindow()
    win.run()
