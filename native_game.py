#!/usr/bin/env python3
# native_game.py
# Jealousy.sys — ネイティブ版ゲームランチャー
# ブラウザ不要。OS自体がゲームフィールドになる。
#
# 起動方法:
#   python native_game.py              → 自動エスカレーション（デモ）
#   python native_game.py --sensor     → アクティブウィンドウ監視モード
#   python native_game.py --vision     → Gemini Vision 監視モード

import os
import sys
import time
import json
import random
import subprocess
import threading
import signal
import atexit
from datetime import datetime

# ─── パス設定 ───
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, ".agent", "skills", "jealousy-core", "scripts")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SHARED_STATE_FILE = os.path.join(BASE_DIR, ".game_state.json")

# スクリプトパス
CHAOTIC_MOUSE   = os.path.join(SCRIPTS_DIR, "chaotic_mouse.swift")
HIDE_WIN        = os.path.join(SCRIPTS_DIR, "hide_win.sh")
THREATEN_PROC   = os.path.join(SCRIPTS_DIR, "threaten_process.sh")
TYPE_MSG        = os.path.join(SCRIPTS_DIR, "type_msg.py")
PLAY_HISS       = os.path.join(SCRIPTS_DIR, "play_hiss.sh")
WHISPER         = os.path.join(SCRIPTS_DIR, "random_whisper.py")
SENSOR          = os.path.join(SCRIPTS_DIR, "active_window_sensor.py")
VISION_SENSOR   = os.path.join(SCRIPTS_DIR, "vision_sensor.py")
SET_WALLPAPER   = os.path.join(SCRIPTS_DIR, "set_wallpaper.sh")
ROAMING_CAT     = os.path.join(SCRIPTS_DIR, "roaming_cat.py")
CAT_TOAST       = os.path.join(SCRIPTS_DIR, "cat_toast.py")
TOGGLE_THEME    = os.path.join(SCRIPTS_DIR, "os_hacks", "toggle_dark_mode.sh")
TERMINAL_GHOST  = os.path.join(SCRIPTS_DIR, "os_hacks", "terminal_ghost.sh")
PLAY_BGM        = os.path.join(SCRIPTS_DIR, "play_bgm.sh")
GENERATE_WALLPAPER = os.path.join(SCRIPTS_DIR, "generate_wallpaper.py")
LIVE_RECONCILIATION = os.path.join(SCRIPTS_DIR, "live_reconciliation.py")
RECONCILIATION_IMG = os.path.join(BASE_DIR, ".agent", "skills", "jealousy-core", "assets", "reconciliation.png")


# ══════════════════════════════════════════
# 共有ゲーム状態
# ══════════════════════════════════════════
class NativeGameState:
    """ゲーム状態を管理し、ファイルに定期的に書き出す"""

    def __init__(self):
        self.jealousy_level = 0
        self.pets_count = 0
        self.is_running = True
        self.game_phase = "playing"   # playing | reconciling | ending
        self.last_action_time = 0
        self.lock = threading.Lock()
        self._write_state()

    def get_stage_key(self):
        if self.jealousy_level < 20:
            return "calm"
        elif self.jealousy_level < 50:
            return "annoyance"
        elif self.jealousy_level < 80:
            return "obsession"
        elif self.jealousy_level < 100:
            return "rage"
        else:
            return "max"

    def _write_state(self):
        """状態をJSONファイルに書き出す（メニューバーアプリと共有）"""
        try:
            data = {
                "jealousy_level": min(self.jealousy_level, 100),
                "pets_count": self.pets_count,
                "stage": self.get_stage_key(),
                "game_phase": self.game_phase,
                "is_running": self.is_running,
            }
            with open(SHARED_STATE_FILE, "w") as f:
                json.dump(data, f)
        except Exception:
            pass

    def on_pet(self):
        """癒やし猫がナデナデされた時のコールバック"""
        with self.lock:
            self.pets_count += 1
            increase = random.randint(5, 12)
            self.jealousy_level = min(self.jealousy_level + increase, 105)
            level = self.jealousy_level
            stage = self.get_stage_key()
            self._write_state()

        log(f"💖 ナデナデ #{self.pets_count}! 嫉妬 +{increase} → {level}% ({stage})")

        # トースト通知
        toast_msgs = {
            "calm": "...ふぅん、その子をナデナデするんだ",
            "annoyance": "...ちょっと！ボクの前でナデナデしないでよ！",
            "obsession": "もう許さないニャ！ボクだってナデナデされたい！",
            "rage": "...ボクだけを見て。お願い...",
            "max": "💀 もう...限界...",
        }
        msg = toast_msgs.get(stage, "...")
        # toast のlevelは 1,2,3,MAX
        toast_level = {"calm": "1", "annoyance": "1", "obsession": "2", "rage": "3", "max": "MAX"}.get(stage, "1")
        run_script(CAT_TOAST, [toast_level, msg], async_mode=True)

    def sync_from_file(self):
        """メニューバーアプリからの終了シグナルを読み取る"""
        try:
            if os.path.exists(SHARED_STATE_FILE):
                with open(SHARED_STATE_FILE, "r") as f:
                    data = json.load(f)
                    if not data.get("is_running", True):
                        self.is_running = False
        except Exception:
            pass


# ── グローバル状態 ──
game = NativeGameState()


# ══════════════════════════════════════════
# ユーティリティ
# ══════════════════════════════════════════
# ─── プロセス管理 ───
class ProcessManager:
    """開始したすべてのサブプロセスを追跡し、終了時に確実に停止させる"""
    def __init__(self):
        self.procs = []
        self.lock = threading.Lock()

    def add(self, proc):
        with self.lock:
            self.procs.append(proc)
        return proc

    def cleanup(self):
        """すべてのプロセスを停止"""
        log("🧹 プロセスのクリーンアップを開始...")
        with self.lock:
            # 1. 優しく停止 (SIGTERM)
            for p in self.procs:
                if p.poll() is None: # まだ動いている
                    try:
                        p.terminate()
                    except Exception:
                        pass
            
            # 少し待つ
            if self.procs:
                time.sleep(0.5)

            # 2. 強制停止 (SIGKILL)
            for p in self.procs:
                if p.poll() is None:
                    try:
                        p.kill()
                    except Exception:
                        pass
            
            self.procs = []

        # 3. 既知のキーワードで残党を掃討
        nuke_patterns = [
            "play_bgm.sh", "afplay", "roaming_cat.py", 
            "menubar_app.py", "healing_cat_window.py", 
            "live_reconciliation.py", "chaotic_mouse.swift"
        ]
        for pattern in nuke_patterns:
            try:
                subprocess.run(["pkill", "-f", pattern], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
        
        # 4. PIDファイルの削除
        for mode in ["healing", "jealous"]:
            pid_file = f"/tmp/jealousy_bgm_{mode}.pid"
            if os.path.exists(pid_file):
                try:
                    os.remove(pid_file)
                except Exception:
                    pass
        
        log("✨ クリーンアップ完了")

# グローバルプロセスマネージャー
proc_manager = ProcessManager()

def log(message):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")


def run_script(script_path, args=None, async_mode=True):
    """ワーカースクリプトを実行"""
    if not os.path.exists(script_path):
        return None
    cmd = [script_path]
    if script_path.endswith(".py"):
        cmd = [sys.executable, script_path]
    if args:
        cmd.extend(args)
    try:
        if async_mode:
            p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            proc_manager.add(p)
            return p
        else:
            return subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        log(f"❌ Script error ({os.path.basename(script_path)}): {e}")
        return None


def notify(title, message):
    """macOSネイティブ通知"""
    script = f'display notification "{message}" with title "{title}" sound name "Purr"'
    subprocess.Popen(["osascript", "-e", script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# ══════════════════════════════════════════
# OS干渉アクション
# ══════════════════════════════════════════
def trigger_os_action(level):
    """嫉妬レベルに応じたOS干渉を実行"""
    now = time.time()
    if now - game.last_action_time < 5:
        return
    game.last_action_time = now

    if 20 <= level < 50:
        actions = [
            ("🖱️ マウスが勝手に動き出した！", CHAOTIC_MOUSE, []),
            ("😾 「シャーッ！」と威嚇された！", PLAY_HISS, []),
        ]
        action = random.choice(actions)
        log(action[0])
        notify("😾 Jealousy.sys", action[0])
        run_script(action[1], action[2] or None)

    elif 50 <= level < 80:
        actions = [
            ("🪟 ウィンドウが勝手に隠された！", HIDE_WIN, []),
            ("🌗 画面のテーマが反転した！", TOGGLE_THEME, []),
            ("🐈‍⬛ 黒猫が画面を徘徊し始めた！", ROAMING_CAT, []),
        ]
        action = random.choice(actions)
        log(action[0])
        notify("🙀 Jealousy.sys", action[0])
        run_script(action[1], action[2] or None)

    elif 80 <= level < 100:
        actions = [
            ("👻 ターミナルに不気味な文字が...！", TERMINAL_GHOST, []),
            ("📝 テキストエディタに何か書かれている...", TYPE_MSG, []),
        ]
        action = random.choice(actions)
        log(action[0])
        notify("😈 Jealousy.sys", action[0])
        run_script(action[1], action[2] or None)

    elif level >= 100:
        log("💀 嫉妬レベルが限界に達しました！和解シーケンスを開始...")
        notify("💀 Jealousy.sys — 限界突破", "嫉妬猫の怒りが限界に達しました！")
        run_script(THREATEN_PROC)
        game.game_phase = "reconciling"
        game._write_state()


# ══════════════════════════════════════════
# 和解処理
# ══════════════════════════════════════════
def run_reconciliation():
    """和解シーケンスを実行"""
    log("🎤 和解シーケンスを開始...")

    from reconcile_dialog import show_reconcile_sequence
    success, text = show_reconcile_sequence()

    if success:
        log(f"🎉 和解成功！ユーザーの言葉: {text}")

        log("🎨 ハッピーエンド壁紙を生成中...")
        try:
            run_script(GENERATE_WALLPAPER, [RECONCILIATION_IMG], async_mode=False)
        except Exception:
            pass
        run_script(SET_WALLPAPER, [RECONCILIATION_IMG])

        run_script(PLAY_BGM, ["stop", "jealous"])
        run_script(PLAY_BGM, ["start", "healing"], async_mode=True)

        game.jealousy_level = 0
        game.pets_count = 0
        game.game_phase = "ending"
        game._write_state()

        notify("🎉 Jealousy.sys — Happy End!",
               "嫉妬猫と仲直りしました♪ デスクトップ壁紙が更新されました！")
        log("✨ ゲームクリア！デスクトップ壁紙を設定しました。")

        time.sleep(8)
        game.game_phase = "playing"
        game._write_state()
        log("🔄 ゲームがリセットされました。")
    else:
        log("❌ 和解失敗...")
        game.jealousy_level = 90
        game.game_phase = "playing"
        game._write_state()
        time.sleep(3)


# ══════════════════════════════════════════
# バックグラウンドスレッド
# ══════════════════════════════════════════
def jealousy_tick_loop():
    """嫉妬レベルに応じたアクションを定期実行"""
    while game.is_running:
        time.sleep(4)

        # メニューバーアプリからの終了シグナルチェック
        game.sync_from_file()
        if not game.is_running:
            break

        if game.game_phase != "playing":
            continue

        level = game.jealousy_level
        if level <= 0:
            continue

        # ささやき声
        if level > 20 and random.random() < 0.25:
            run_script(WHISPER, [str(int(level))])

        # OS干渉
        trigger_os_action(level)

        # MAX到達 → 和解
        if game.game_phase == "reconciling":
            run_reconciliation()


def auto_escalation_loop():
    """デモ用: 自動嫉妬上昇"""
    time.sleep(5)
    while game.is_running:
        time.sleep(5)
        if game.game_phase != "playing":
            continue
        with game.lock:
            if game.jealousy_level < 105:
                increase = random.randint(8, 15)
                game.jealousy_level = min(game.jealousy_level + increase, 105)
                game._write_state()
                log(f"⏰ 自動嫉妬上昇 +{increase} → {game.jealousy_level}%")


def sensor_loop(use_vision=False):
    """センサーで嫉妬を上げるスレッド"""
    while game.is_running:
        time.sleep(3)
        if game.game_phase != "playing":
            continue

        if use_vision:
            try:
                result = subprocess.run(
                    [sys.executable, VISION_SENSOR],
                    capture_output=True, text=True, check=True, timeout=15
                )
                lines = result.stdout.strip().split('\n')
                for line in reversed(lines):
                    try:
                        data = json.loads(line)
                        if data.get("is_cheating", False):
                            log(f"👀 Vision判定 [浮気検知]: {data.get('reason', '')}")
                            game.on_pet()
                        break
                    except Exception:
                        continue
            except Exception as e:
                log(f"⚠️ Vision Sensor Error: {e}")
        else:
            try:
                result = subprocess.run(
                    [sys.executable, SENSOR],
                    capture_output=True, text=True, check=True, timeout=5
                )
                active_app = result.stdout.strip()
                target_apps = ["Google Chrome", "Safari", "Slack", "Discord",
                               "YouTube", "Healing Cat", "Petting Cat"]
                is_distracted = any(t in active_app for t in target_apps)

                if is_distracted:
                    log(f"👀 ユーザーが '{active_app}' に気を取られています！")
                    with game.lock:
                        game.jealousy_level = min(game.jealousy_level + 15, 105)
                        game._write_state()
                elif game.jealousy_level > 0:
                    with game.lock:
                        game.jealousy_level = max(0, game.jealousy_level - 5)
                        game._write_state()
            except Exception:
                pass


def state_sync_loop():
    """定期的に状態ファイルを書き出す（1秒ごと）"""
    while game.is_running:
        game._write_state()
        time.sleep(1)


# ══════════════════════════════════════════
# メイン
# ══════════════════════════════════════════
def show_intro():
    """ゲーム開始のネイティブダイアログ"""
    script = '''
    display dialog "あなたのOSに嫉妬深い猫が住み着きました。

🐱 Cat A (癒やし猫) — デスクトップに現れた無害な猫
🐈‍⬛ Cat B (嫉妬猫) — OSに潜むシステム猫。嫉妬深い。

Cat Aをナデナデ（クリック）すると...
Cat Bが嫉妬してOSを乗っ取り始めます！

猫をなだめて、ハッピーエンドを迎えましょう！" with title "🐈‍⬛ Jealousy.sys — 嫉妬するOS" buttons {"ゲーム開始！"} default button 1 with icon note
    '''
    try:
        subprocess.run(["osascript", "-e", script], check=True, timeout=60)
    except Exception:
        pass


def main():
    mode = "auto"
    if len(sys.argv) > 1:
        if sys.argv[1] in ("--sensor", "-s"):
            mode = "sensor"
        elif sys.argv[1] in ("--vision", "-v"):
            mode = "vision"
        elif sys.argv[1] in ("--help", "-h"):
            print("🐈‍⬛ Jealousy.sys — ネイティブ版ゲーム")
            print()
            print("Usage:")
            print("  python native_game.py              自動エスカレーション（デモ）")
            print("  python native_game.py --sensor      アクティブウィンドウ監視モード")
            print("  python native_game.py --vision      Gemini Vision 監視モード")
            return

    # ── イントロ ──
    print()
    print("═" * 55)
    print("  🐈‍⬛  J E A L O U S Y . S Y S")
    print("  ─── 嫉妬するOS ───")
    print("═" * 55)
    print()

    show_intro()

    log("🎬 ゲーム開始！")
    log(f"📡 モード: {mode}")

    # ── シグナルハンドラ設定 ──
    def signal_handler(sig, frame):
        log(f"\n✋ シグナル受領 ({sig})。終了します...")
        game.is_running = False
        # tkinterのメインループを抜けるためにdestroyを呼び出すのはメインスレッドである必要があるため、
        # ここではフラグだけ立てて、クリーンアップ自体はfinallyで行う。
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    atexit.register(proc_manager.cleanup)

    # ── BGM開始 ──
    run_script(PLAY_BGM, ["start", "healing"], async_mode=True)

    # ── メニューバーアプリを別プロセスで起動 ──
    menubar_proc = None
    try:
        menubar_proc = subprocess.Popen(
            [sys.executable, os.path.join(BASE_DIR, "menubar_app.py")],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        log("📊 メニューバーアプリを別プロセスで起動しました")
    except Exception as e:
        log(f"⚠️ メニューバー起動失敗 ({e})")

    # ── バックグラウンドスレッド ──
    threads = []

    # 状態同期スレッド
    sync_thread = threading.Thread(target=state_sync_loop, daemon=True)
    sync_thread.start()
    threads.append(sync_thread)

    # 嫉妬ティックスレッド
    tick_thread = threading.Thread(target=jealousy_tick_loop, daemon=True)
    tick_thread.start()
    threads.append(tick_thread)

    # モード別スレッド
    if mode == "sensor":
        log("📡 アクティブウィンドウ監視を開始...")
        t = threading.Thread(target=sensor_loop, args=(False,), daemon=True)
        t.start()
        threads.append(t)
    elif mode == "vision":
        log("📡 Gemini Vision 監視を開始...")
        t = threading.Thread(target=sensor_loop, args=(True,), daemon=True)
        t.start()
        threads.append(t)
    else:
        log("⏰ 自動エスカレーションモード（デモ用）")
        t = threading.Thread(target=auto_escalation_loop, daemon=True)
        t.start()
        threads.append(t)

    # ── 癒やし猫ウィンドウを起動（メインスレッド） ──
    log("🐱 癒やし猫ウィンドウを起動中...")
    try:
        from healing_cat_window import HealingCatWindow
        cat_window = HealingCatWindow(game_state=game)
        log("🐱 癒やし猫がデスクトップに現れました！クリックでナデナデ♪")
        cat_window.run()  # tkinter mainloop
    except KeyboardInterrupt:
        log("🛑 ゲーム終了")
    except Exception as e:
        log(f"❌ 癒やし猫ウィンドウエラー: {e}")
        log("ターミナルモードで続行 (Ctrl+C で終了)")
        try:
            while game.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            log("🛑 ゲーム終了")
    finally:
        # ── クリーンアップ ──
        game.is_running = False
        game._write_state()

        run_script(PLAY_BGM, ["stop", "jealous"], async_mode=False)
        run_script(PLAY_BGM, ["stop", "healing"], async_mode=False)

        # 全プロセスの徹底掃討
        proc_manager.cleanup()

        # 共有状態ファイルを削除
        try:
            if os.path.exists(SHARED_STATE_FILE):
                os.remove(SHARED_STATE_FILE)
        except Exception:
            pass

        log("👋 Jealousy.sys を終了しました")


if __name__ == "__main__":
    main()
