#!/usr/bin/env python3
# main_loop.py
# Jealousy.sys - Supervisor エージェントのメインループ
# 時間経過や特定イベントに応じて嫉妬レベルをあがり、各レベルに応じたWorkerスクリプトを実行する

import os
import sys
import time
import subprocess
import random
from datetime import datetime

# 定数：スクリプトへのパス
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, ".agent", "skills", "jealousy-core", "scripts")

CHAOTIC_MOUSE = os.path.join(SCRIPTS_DIR, "chaotic_mouse.swift")
HIDE_WIN = os.path.join(SCRIPTS_DIR, "hide_win.sh")
THREATEN_PROC = os.path.join(SCRIPTS_DIR, "threaten_process.sh")
TYPE_MSG = os.path.join(SCRIPTS_DIR, "type_msg.py")
PLAY_HISS = os.path.join(SCRIPTS_DIR, "play_hiss.sh")
WHISPER = os.path.join(SCRIPTS_DIR, "random_whisper.py")
SENSOR = os.path.join(SCRIPTS_DIR, "active_window_sensor.py")
VISION_SENSOR = os.path.join(SCRIPTS_DIR, "vision_sensor.py")
SET_WALLPAPER = os.path.join(SCRIPTS_DIR, "set_wallpaper.sh")
ROAMING_CAT = os.path.join(SCRIPTS_DIR, "roaming_cat.py")
CAT_TOAST = os.path.join(SCRIPTS_DIR, "cat_toast.py")
RECONCILIATION_IMG = os.path.join(BASE_DIR, ".agent", "skills", "jealousy-core", "assets", "reconciliation.png")
LIVE_RECONCILIATION = os.path.join(SCRIPTS_DIR, "live_reconciliation.py")
GENERATE_WALLPAPER = os.path.join(SCRIPTS_DIR, "generate_wallpaper.py")

# 新しい OS Hacks 用のスクリプトパス
TOGGLE_THEME = os.path.join(SCRIPTS_DIR, "os_hacks", "toggle_dark_mode.sh")
TERMINAL_GHOST = os.path.join(SCRIPTS_DIR, "os_hacks", "terminal_ghost.sh")
PLAY_BGM = os.path.join(SCRIPTS_DIR, "play_bgm.sh")

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

    def check_vision_sensor(self):
        """Vision APIセンサーを使って画面上に癒やし系猫がいるか判定し、結果を返す"""
        try:
            result = subprocess.run([sys.executable, VISION_SENSOR], capture_output=True, text=True, check=True)
            output = result.stdout.strip()
            if output:
                import json
                lines = output.split('\n')
                for line in reversed(lines):
                    try:
                        data = json.loads(line)
                        return data.get("is_cheating", False), data.get("reason", "")
                    except json.JSONDecodeError:
                        continue
            return False, "No valid JSON output from vision sensor."
        except Exception as e:
            self.log(f"⚠️ Vision Sensor Error: {e}")
            return False, str(e)

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
            run_worker(CAT_TOAST, ["1", "マウスを揺らしてやるニャ..."], async_mode=True)
            run_worker(PLAY_BGM, ["start", "jealous"], async_mode=True)
            run_worker(CHAOTIC_MOUSE, async_mode=True)
            run_worker(PLAY_HISS, async_mode=True)
            
        # Level 2: Obsession
        elif 50 <= self.jealousy_level < 80:
            self.log("⚡ [Level 2: Obsession] - ウィンドウを不意に隠し、テーマ色反転、画面を徘徊する猫を召喚する")
            run_worker(CAT_TOAST, ["2", "お前のウィンドウ、隠してやったニャ"], async_mode=True)
            run_worker(HIDE_WIN)
            run_worker(TOGGLE_THEME, async_mode=True)
            run_worker(ROAMING_CAT, async_mode=True)
            
        # Level 3: Rage
        elif 80 <= self.jealousy_level < 100:
            self.log("⚡ [Level 3: Rage] - メッセージタイピングと並行して、裏で不気味なターミナルを立ち上げる")
            run_worker(CAT_TOAST, ["3", "もう我慢できないニャ...直接話す"], async_mode=True)
            run_worker(TYPE_MSG, ["ボクだけを見て... お願いだから..."], async_mode=True)
            run_worker(TERMINAL_GHOST, async_mode=True)
            
        # MAX (Hackathon Demo)
        elif self.jealousy_level >= 100:
            self.log("⚡ [MAX: Danger] - 脅迫ダイアログを表示")
            run_worker(CAT_TOAST, ["MAX", "限界ニャ...全てを終わらせる"], async_mode=True)
            run_worker(THREATEN_PROC)
            
            # デモ用：MAXに達したら和解イベントを発生させる
            time.sleep(3)
            self.log("🎤 [Reconciliation] - 音声対話 (Live API経由) を開始し、なだめを待機します...")
            
            # subprocessで同期実行し、和解できたかチェック
            try:
                result = subprocess.run([sys.executable, LIVE_RECONCILIATION], check=True)
                reconciled = True
            except subprocess.CalledProcessError:
                reconciled = False
                
            if reconciled:
                self.log("🎨 生成AIで二匹のハッピーエンド壁紙を動的生成しています...")
                # 壁紙生成スクリプトを実行し、画像を上書きする
                subprocess.run([sys.executable, GENERATE_WALLPAPER, RECONCILIATION_IMG])
                
                self.log("✨ [Reconciliation] - 仲直りの画像をデスクトップに設定します。")
                run_worker(SET_WALLPAPER, [RECONCILIATION_IMG])
                
                self.log("🛑 嫉妬が限界に達し、無事に和解しました。デモシナリオをリセットします。")
                self.jealousy_level = 0
                run_worker(PLAY_BGM, ["stop", "jealous"]) # 嫉妬BGM停止
                run_worker(PLAY_BGM, ["start", "healing"], async_mode=True) # ヒーリングBGM再開
                time.sleep(5) 
            else:
                self.log("❌ 和解失敗...嫉妬レベルは下がりません。再試行を待ちます。")
                self.jealousy_level = 90
                time.sleep(5) 

    def run_demo_scenario(self, use_sensor=False, use_vision=False):
        """
        ハッカソンデモ用のタイムラインスクリプト
        """
        if use_vision:
            self.log("🎬 Visionセンサー連動デモ開始: 画面キャプチャとGemini APIでユーザーを監視します...")
        elif use_sensor:
            self.log("🎬 センサー連動デモ開始: ユーザーが特定のアプリ（ブラウザや他ツール）に集中しているか監視します...")
        elif self.jealousy_level == 0:
            run_worker(PLAY_BGM, ["start", "healing"], async_mode=True)
            self.log("🎬 タイムラインデモ開始: 自動的に嫉妬度が上昇します...")
        
        try:
            while self.is_running:
                time.sleep(3) # 監視間隔を少し短くする
                
                if use_vision:
                    is_cheating, reason = self.check_vision_sensor()
                    if is_cheating:
                        self.log(f"👀 Vision判定 [浮気検知]: {reason}")
                        self.increase_jealousy(15)
                    elif self.jealousy_level > 0:
                        self.log("😌 Vision判定 [平和]: 猫（他のターゲット）は見ていないようです")
                        self.jealousy_level = max(0, self.jealousy_level - 5)
                        time.sleep(2)
                
                # 嫉妬度が高い場合、たまにささやき声（音声）を出す
                if self.jealousy_level > 10 and random.random() < 0.3:
                    run_worker(WHISPER, [str(int(self.jealousy_level))], async_mode=True)
                
                elif use_sensor:
                    active_app = self.check_active_window()
                    # ターミナル（実行画面）やエディタ以外のアプリを見ていると嫉妬が上がる
                    target_apps = ["Google Chrome", "Safari", "Slack", "Discord", "YouTube", "Healing Cat Interface", "Petting Cat"]
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
        supervisor.run_demo_scenario(use_sensor=False, use_vision=False)
    elif len(sys.argv) > 1 and sys.argv[1] == "--sensor-demo":
        supervisor.run_demo_scenario(use_sensor=True, use_vision=False)
    elif len(sys.argv) > 1 and sys.argv[1] == "--vision-demo":
        supervisor.run_demo_scenario(use_sensor=False, use_vision=True)
    else:
        print("💡 Usage:")
        print("💡   python main_loop.py --demo         : 自動で嫉妬レベルが上がるデモ")
        print("💡   python main_loop.py --sensor-demo  : アクティブウィンドウを監視して嫉妬するデモ")
        print("💡   python main_loop.py --vision-demo  : 画面キャプチャとGemini Vision APIで猫への浮気を監視するデモ")
