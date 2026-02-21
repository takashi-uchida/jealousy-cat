#!/usr/bin/env python3
# reconcile_gui.py
# 和解用のGUIダイアログ (tkinter版)
# 猫のイラスト付きで、ユーザーに謝罪を促す

import tkinter as tk
from tkinter import messagebox
import sys
import random
import os
import time
from PIL import Image, ImageTk

RECONCILE_KEYWORDS = [
    "好き", "大好き", "ごめん", "ごめんね", "すき", "一番",
    "かわいい", "可愛い", "大切", "愛してる", "許して",
    "ごめんなさい", "仲直り", "love", "sorry",
    "なでなで", "よしよし", "いい子", "構ってあげる",
]

class ReconcileApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Jealousy.sys — 和解交渉")
        
        # 画面中央に配置
        w, h = 500, 400
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        
        # 背景色（少し暗く）
        self.root.configure(bg="#2C2C2C")

        # 試行回数
        self.attempts = 3

        # アイコン画像読み込み（あれば）
        self.cat_img = None
        self.load_image()

        # UI構築
        self.setup_ui()

    def load_image(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        img_path = os.path.join(base_dir, "assets", "walking_black_cat.png") # 嫉妬猫の画像があればそれを使う
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
        # メインフレーム
        frame = tk.Frame(self.root, bg="#2C2C2C")
        frame.pack(expand=True, fill="both", padx=20, pady=20)

        # 画像
        if self.cat_img:
            lbl_img = tk.Label(frame, image=self.cat_img, bg="#2C2C2C")
            lbl_img.pack(pady=(0, 10))
        else:
            lbl_img = tk.Label(frame, text="🐈‍⬛", font=("Arial", 60), bg="#2C2C2C", fg="white")
            lbl_img.pack(pady=(0, 10))

        # メッセージ
        self.lbl_msg = tk.Label(
            frame, 
            text="もう我慢できないニャ！\nボクのこと、どう思ってるの？\nちゃんと説明してよ！",
            font=("Helvetica", 14, "bold"),
            bg="#2C2C2C", fg="#FFD700",
            justify="center"
        )
        self.lbl_msg.pack(pady=10)

        # 入力欄
        self.entry = tk.Entry(frame, font=("Helvetica", 14), width=30)
        self.entry.pack(pady=10)
        self.entry.bind("<Return>", lambda e: self.check_reconcile())
        self.entry.focus_set()
        
        # 強制フォーカス（macOSなどで後ろに行かないように）
        self.root.lift()
        self.root.focus_force()
        self.entry.focus_force()

        # ヒント
        self.lbl_hint = tk.Label(
            frame, 
            text="（ヒント: 「好き」「ごめんね」など、素直な気持ちを伝えよう...）",
            font=("Helvetica", 10),
            bg="#2C2C2C", fg="#888888"
        )
        self.lbl_hint.pack(pady=(0, 10))

        # ボタン
        btn_frame = tk.Frame(frame, bg="#2C2C2C")
        btn_frame.pack(pady=20)

        btn_submit = tk.Button(
            btn_frame, text="送信", command=self.check_reconcile,
            highlightbackground="#2C2C2C", font=("Helvetica", 12)
        )
        btn_submit.pack(side="left", padx=10)

        btn_cancel = tk.Button(
            btn_frame, text="無視する", command=self.on_cancel,
            highlightbackground="#2C2C2C", font=("Helvetica", 12)
        )
        btn_cancel.pack(side="right", padx=10)

        # 残り回数
        self.lbl_status = tk.Label(
            frame, text=f"残りチャンス: {self.attempts}回",
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
            messagebox.showinfo("和解成功", f"「{text}」...？\nほんとに？\n\n...わかった、許してあげるニャ。", parent=self.root)
            print(text) # 標準出力に結果を出して親プロセスに渡す
            self.root.destroy()
            sys.exit(0) # Success
        else:
            self.attempts -= 1
            self.lbl_status.config(text=f"残りチャンス: {self.attempts}回")
            self.entry.delete(0, tk.END)
            self.shake_window()
            
            if self.attempts > 0:
                msgs = [
                    "全然気持ちがこもってないニャ！",
                    "嘘つき！もっと本音で話して！",
                    "それだけ？",
                    "もっと褒めてよ！"
                ]
                self.lbl_msg.config(text=random.choice(msgs), fg="#FF4444")
            else:
                messagebox.showerror("交渉決裂", "もう知らない！\nプイッ！")
                self.root.destroy()
                sys.exit(1) # Failure

    def on_cancel(self):
        self.root.destroy()
        sys.exit(1)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ReconcileApp()
    app.run()
