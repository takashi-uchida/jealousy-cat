#!/usr/bin/env python3
# main_loop.py
# Jealousy.sys - Supervisor エージェントのメインループ
# 時間経過や特定イベントに応じて嫉妬レベルをあがり、各レベルに応じたWorkerスクリプトを実行する

import os
import sys
import time
import subprocess
from datetime import datetime

# 定数：スクリプトへのパス
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, ".agent", "skills", "jealousy-core", "scripts")

CHAOTIC_MOUSE = os.path.join(SCRIPTS_DIR, "chaotic_mouse.swift")
HIDE_WIN = os.path.join(SCRIPTS_DIR, "hide_win.sh")
THREATEN_PROC = os.path.join(SCRIPTS_DIR, "threaten_process.sh")
TYPE_MSG = os.path.join(SCRIPTS_DIR, "type_msg.py")
PLAY_HISS = os.path.join(SCRIPTS_DIR, "play_hiss.sh")
SENSOR = os.path.join(SCRIPTS_DIR, "active_window_sensor.py")
SET_WALLPAPER = os.path.join(SCRIPTS_DIR, "set_wallpaper.sh")
RECONCILIATION_IMG = os.path.join(BASE_DIR, ".agent", "skills", "jealousy-core", "assets", "reconciliation.png")

# プロセス実行のラッパー関数
def run_worker(script_path, args=None, async_mode=False):
    if not os.path.exists(script_path):
        print(f"❌ [Error] Script not found: {script_path}")
        return

    cmd = [script_path]
    
    # 拡張子に応じて実行方法を判断
    if script_path.endswith(".py"):
        cmd = [sys.executable, script_path] # 現在のPythonインタープリタを使う
    
    if args:
        cmd.extend(args)

    try:
        print(f"🚀 [Supervisor] Executing: {os.path.basename(script_path)}")
        if async_mode:
            subprocess.Popen(cmd)
        else:
            subprocess.run(cmd, check=True)
    except Exception as e:
        print(f"❌ [Error] Failed to execute {script_path}: {e}")

class JealousySupervisor:
    def __init__(self):
        self.jealousy_level = 0
        self.is_running = True
        self.log("Jealousy.sys Supervisor started. Waiting for target (猫A)...")

    def check_active_window(self):
        """センサーを使って現在アクティブなウィンドウ名を取得する"""
        try:
            result = subprocess.run([sys.executable, SENSOR], capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except Exception:
            return "Unknown"

    def log(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    def increase_jealousy(self, amount):
        self.jealousy_level += amount
        self.log(f"😡 嫉妬レベル上昇: {self.jealousy_level}/100")
        self.check_thresholds()

    def check_thresholds(self):
        """現在のレベルに応じてアクションをトリガーする"""
        
        # Level 1: Annoyance
        if 20 <= self.jealousy_level < 50:
            self.log("⚡ [Level 1: Annoyance] - マウスを揺らし、不気味な声で威嚇する")
            run_worker(CHAOTIC_MOUSE, async_mode=True)
            run_worker(PLAY_HISS, async_mode=True)
            
        # Level 2: Obsession
        elif 50 <= self.jealousy_level < 80:
            self.log("⚡ [Level 2: Obsession] - ウィンドウを不意に隠す")
            run_worker(HIDE_WIN)
            
        # Level 3: Rage
        elif 80 <= self.jealousy_level < 100:
            self.log("⚡ [Level 3: Rage] - メッセージをタイピングしてアピール")
            run_worker(TYPE_MSG, ["ボクだけを見て... お願いだから..."])
            
        # MAX (Hackathon Demo)
        elif self.jealousy_level >= 100:
            self.log("⚡ [MAX: Danger] - 脅迫ダイアログを表示")
            run_worker(THREATEN_PROC)
            
            # デモ用：MAXに達したら和解イベントを発生させる
            time.sleep(3)
            self.log("✨ [Reconciliation] - 仲直りの画像をデスクトップに設定します。")
            run_worker(SET_WALLPAPER, [RECONCILIATION_IMG])
            
            self.log("🛑 嫉妬が限界に達し、和解しました。デモシナリオをリセットします。")
            self.jealousy_level = 0
            time.sleep(5) 

    def run_demo_scenario(self, use_sensor=False):
        """
        ハッカソンデモ用のタイムラインスクリプト
        use_sensor=True の場合、特定のアプリを開いているときだけ嫉妬レベルが上がる
        """
        if use_sensor:
            self.log("🎬 センサー連動デモ開始: ユーザーが特定のアプリ（ブラウザや他ツール）に集中しているか監視します...")
        else:
            self.log("🎬 タイムラインデモ開始: 自動的に嫉妬度が上昇します...")
        
        try:
            while self.is_running:
                time.sleep(3) # 監視間隔を少し短くする
                
                if use_sensor:
                    active_app = self.check_active_window()
                    # ターミナル（実行画面）やエディタ以外のアプリを見ていると嫉妬が上がる
                    target_apps = ["Google Chrome", "Safari", "Slack", "Discord", "YouTube"]
                    is_distracted = any(target in active_app for target in target_apps)
                    
                    if is_distracted:
                        self.log(f"👀 ターゲティング: ユーザーが '{active_app}' に気を取られています！")
                        self.increase_jealousy(15)
                    elif self.jealousy_level > 0:
                        # ターミナル等に集中し直せば少し落ち着く
                        self.log(f"😌 落ち着きを取り戻しています (現在のApp: {active_app})")
                        self.jealousy_level = max(0, self.jealousy_level - 5)
                        time.sleep(2)
                else:
                    # 従来の強制タイムライン進行
                    self.increase_jealousy(20)
                    time.sleep(2)
                
        except KeyboardInterrupt:
            self.log("🛑 Supervisor stopped by user.")
            self.is_running = False

if __name__ == "__main__":
    supervisor = JealousySupervisor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        supervisor.run_demo_scenario(use_sensor=False)
    elif len(sys.argv) > 1 and sys.argv[1] == "--sensor-demo":
        supervisor.run_demo_scenario(use_sensor=True)
    else:
        print("💡 Usage:")
        print("💡   python main_loop.py --demo         : 自動で嫉妬レベルが上がるデモ")
        print("💡   python main_loop.py --sensor-demo  : アクティブウィンドウを監視して嫉妬するデモ")
