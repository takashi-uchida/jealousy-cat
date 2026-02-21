#!/usr/bin/env python3
# reconcile_gui.py
# GUI dialog for reconciliation (tkinter version)
# Includes an illustration of the cat and prompts the user for an apology.

import tkinter as tk
from tkinter import messagebox
import sys
import random
import os
import time
from PIL import Image, ImageTk

RECONCILE_KEYWORDS = [
    "love", "like", "sorry", "apologize", "pardon", "forgive",
    "best", "number one", "cute", "adorable", "important",
    "precious", "darling", "sweetheart", "honey", "pet",
    "stroke", "attention", "care", "together", "reconcile",
]

class ReconcileApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Jealousy.sys — Reconciliation Negotiation")
        
        # Center on screen
        w, h = 500, 400
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        
        # Background color
        self.root.configure(bg="#2C2C2C")

        # Number of attempts
        self.attempts = 3

        # Load icon image
        self.cat_img = None
        self.load_image()

        # Build UI
        self.setup_ui()

    def load_image(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        img_path = os.path.join(base_dir, "assets", "walking_black_cat.png")
        if not os.path.exists(img_path):
            img_path = os.path.join(base_dir, "assets", "system_cat_icon.png")

        if os.path.exists(img_path):
            try:
                img = Image.open(img_path).convert("RGBA")
                img = img.resize((100, 100), Image.LANCZOS)
                self.cat_img = ImageTk.PhotoImage(img)
            except Exception:
                pass

    def setup_ui(self):
        # Main Frame
        frame = tk.Frame(self.root, bg="#2C2C2C")
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Image
        if self.cat_img:
            lbl_img = tk.Label(frame, image=self.cat_img, bg="#2C2C2C")
            lbl_img.pack(pady=(0, 10))
        else:
            lbl_img = tk.Label(frame, text="🐈‍⬛", font=("Arial", 60), bg="#2C2C2C", fg="white")
            lbl_img.pack(pady=(0, 10))

        # Message
        self.lbl_msg = tk.Label(
            frame, 
            text="I can't take this anymore, meow!\nWhat do you think of me?\nExplain yourself!",
            font=("Helvetica", 14, "bold"),
            bg="#2C2C2C", fg="#FFD700",
            justify="center"
        )
        self.lbl_msg.pack(pady=10)

        # Entry Field
        self.entry = tk.Entry(frame, font=("Helvetica", 14), width=30)
        self.entry.pack(pady=10)
        self.entry.bind("<Return>", lambda e: self.check_reconcile())
        self.entry.focus_set()
        
        self.root.lift()
        self.root.focus_force()
        self.entry.focus_force()

        # Hint
        self.lbl_hint = tk.Label(
            frame, 
            text="(Hint: Express your sincere feelings with words like 'love' or 'sorry'...)",
            font=("Helvetica", 10),
            bg="#2C2C2C", fg="#888888"
        )
        self.lbl_hint.pack(pady=(0, 10))

        # Buttons
        btn_frame = tk.Frame(frame, bg="#2C2C2C")
        btn_frame.pack(pady=20)

        btn_submit = tk.Button(
            btn_frame, text="Send", command=self.check_reconcile,
            highlightbackground="#2C2C2C", font=("Helvetica", 12)
        )
        btn_submit.pack(side="left", padx=10)

        btn_cancel = tk.Button(
            btn_frame, text="Ignore", command=self.on_cancel,
            highlightbackground="#2C2C2C", font=("Helvetica", 12)
        )
        btn_cancel.pack(side="right", padx=10)

        # Remaining attempts
        self.lbl_status = tk.Label(
            frame, text=f"Chances left: {self.attempts}",
            bg="#2C2C2C", fg="#AAAAAA", font=("Helvetica", 10)
        )
        self.lbl_status.pack(side="bottom")

    def shake_window(self):
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        for _ in range(5):
            for dx in [-5, 5, -5, 5]:
                self.root.geometry(f"+{x+dx}+{y}")
                self.root.update()
                time.sleep(0.02)
        self.root.geometry(f"+{x}+{y}")

    def check_reconcile(self):
        text = self.entry.get().strip()
        if not text:
            return

        score = sum(1 for kw in RECONCILE_KEYWORDS if kw in text.lower())

        if score >= 1:
            messagebox.showinfo("Reconciliation Successful", f"\"{text}\"...?\nReally?\n\n...Fine, I'll forgive you this time, meow.", parent=self.root)
            print(text) 
            self.root.destroy()
            sys.exit(0) 
        else:
            self.attempts -= 1
            self.lbl_status.config(text=f"Chances left: {self.attempts}")
            self.entry.delete(0, tk.END)
            self.shake_window()
            
            if self.attempts > 0:
                msgs = [
                    "You don't mean that at all, meow!",
                    "Liar! Tell me how you really feel!",
                    "Is that all?",
                    "Praise me more!"
                ]
                self.lbl_msg.config(text=random.choice(msgs), fg="#FF4444")
            else:
                messagebox.showerror("Negotiation Failed", "I'm done with you!\nHmph!")
                self.root.destroy()
                sys.exit(1) 

    def on_cancel(self):
        self.root.destroy()
        sys.exit(1)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ReconcileApp()
    app.run()
