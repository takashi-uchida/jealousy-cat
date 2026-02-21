#!/usr/bin/env python3
# native_game.py
# Jealousy.sys — Native Game Launcher
# No browser required. The OS itself becomes the game field.
#
# Usage:
#   python native_game.py              → Auto-escalation (Demo)
#   python native_game.py --sensor     → Active window monitoring mode
#   python native_game.py --vision     → Gemini Vision monitoring mode

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

# ─── Path Settings ───
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, ".agent", "skills", "jealousy-core", "scripts")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SHARED_STATE_FILE = os.path.join(BASE_DIR, ".game_state.json")
RECONCILE_FLAG_FILE = os.path.join(BASE_DIR, ".reconcile_request")

# Script Paths
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
JEALOUS_BROWSER = os.path.join(SCRIPTS_DIR, "jealous_browser_hijack.py")
RECONCILIATION_IMG = os.path.join(BASE_DIR, ".agent", "skills", "jealousy-core", "assets", "reconciliation.png")
OVERLAY_EFFECTS = os.path.join(SCRIPTS_DIR, "overlay_effects.py")
SYSTEM_CAT_ICON = os.path.join(BASE_DIR, "assets", "system_cat_icon.png")


# ══════════════════════════════════════════
# Shared Game State
# ══════════════════════════════════════════
class NativeGameState:
    """Manages the game state and periodically writes it to a file"""

    def __init__(self):
        self.jealousy_level = 0
        self.pets_count = 0
        self.is_running = True
        self.game_phase = "playing"   # playing | reconciling | ending
        self.last_action_time = 0
        self.current_stage = "calm"
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
        """Write state to a JSON file (Shared with the Menu Bar App)"""
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

    def on_pet(self, action="petting"):
        """Callback when the Healing Cat is petted or 'cheating' is detected"""
        with self.lock:
            self.pets_count += 1
            increase = random.randint(5, 12) if action == "petting" else random.randint(4, 9)
            self.jealousy_level = min(self.jealousy_level + increase, 105)
            level = self.jealousy_level
            new_stage = self.get_stage_key()
            
            stage_changed = (new_stage != self.current_stage)
            self.current_stage = new_stage
            
            self._write_state()

        if action == "looking":
            log(f"👀 Cheating (looking) detected! Jealousy +{increase} → {level}% ({new_stage})")
            if random.random() < 0.1: # Limit to 10% chance for performance/annoyance
                run_script(OVERLAY_EFFECTS, ["popup", str(SYSTEM_CAT_ICON), "Cheating Detected", "Don't look at other cats, meow!", "default"], async_mode=True)
                subprocess.Popen(["say", "-v", "Samantha", "Don't look!"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            log(f"💖 Petting #{self.pets_count}! Jealousy +{increase} → {level}% ({new_stage})")
            if random.random() < 0.1: # Limit to 10% chance
                run_script(OVERLAY_EFFECTS, ["popup", str(SYSTEM_CAT_ICON), "Cheating Detected", "Don't pet other cats, meow!", "default"], async_mode=True)
                subprocess.Popen(["say", "-v", "Samantha", "Don't pet her!"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Show popup on screen (When stage changes)
        if stage_changed:
            titles = {
                "annoyance": "⚠️ Jealousy: Annoyed",
                "obsession": "⚠️ Jealousy: Obsessed",
                "rage":      "🚨 Jealousy: Raging",
                "max":       "💀 Jealousy: Over the Edge"
            }
            msgs = {
                "annoyance": "Have you forgotten about me?",
                "obsession": "Hey, that's enough already...",
                "rage":      "I won't forgive you... never...",
                "max":       "It's... all over now..."
            }
            title = str(titles.get(new_stage, "Jealousy Level Up"))
            msg = str(msgs.get(new_stage, f"Jealousy level reached {level}%"))
            
            run_script(OVERLAY_EFFECTS, ["popup", str(SYSTEM_CAT_ICON), title, msg, "default"], async_mode=True)
        
        elif random.random() < 0.2: 
            run_script(OVERLAY_EFFECTS, ["popup", str(SYSTEM_CAT_ICON), "Jealousy UP!", f"Jealousy: {level}% (+{increase})", "default"], async_mode=True)

        # Toast notifications (As backup, low frequency)
        if random.random() < 0.15:
            toast_msgs = {
                "calm": "...Hmph, so you're petting that thing.",
                "annoyance": "...Hey! Don't cheat right in front of me!",
                "obsession": "I won't forgive you, meow! I want pets too!",
                "rage": "...Look only at me. Please...",
                "max": "💀 I'm at my limit...",
            }
            t_msg = str(toast_msgs.get(new_stage, "..."))
            t_level = str({"calm": "1", "annoyance": "1", "obsession": "2", "rage": "3", "max": "MAX"}.get(new_stage, "1"))
            run_script(CAT_TOAST, [t_level, t_msg], async_mode=True)

    def sync_from_file(self):
        """Read termination signal from Menu Bar App"""
        try:
            if os.path.exists(SHARED_STATE_FILE):
                with open(SHARED_STATE_FILE, "r") as f:
                    data = json.load(f)
                    if not data.get("is_running", True):
                        self.is_running = False
        except Exception:
            pass


# ── Global State ──
game = NativeGameState()


# ══════════════════════════════════════════
# Utilities
# ══════════════════════════════════════════
class ProcessManager:
    """Tracks all started subprocesses and ensures they are stopped upon exit"""
    def __init__(self):
        self.procs = []
        self.lock = threading.Lock()

    def add(self, proc):
        with self.lock:
            self.procs.append(proc)
        return proc

    def cleanup(self):
        """Stop all processes"""
        log("Sweep: Starting process cleanup...")
        with self.lock:
            # 1. Graceful stop (SIGTERM)
            for p in self.procs:
                if p.poll() is None:
                    try:
                        p.terminate()
                    except Exception:
                        pass
            
            time.sleep(0.5)

            # 2. Force stop (SIGKILL)
            for p in self.procs:
                if p.poll() is None:
                    try:
                        p.kill()
                    except Exception:
                        pass
            
            self.procs = []

        # 3. Clean up remnants by known keywords
        nuke_patterns = [
            "play_bgm.sh", "afplay", "roaming_cat.py", 
            "menubar_app.py", "healing_cat_window.py", 
            "live_reconciliation.py", "chaotic_mouse.swift",
            "overlay_effects.py", "reconcile_gui.py",
            "active_window_sensor.py", "vision_sensor.py",
            "jealous_browser_hijack.py"
        ]
        for pattern in nuke_patterns:
            try:
                subprocess.run(["pkill", "-9", "-f", pattern], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
        
        # 4. Delete PID files
        for mode in ["healing", "jealous"]:
            pid_file = f"/tmp/jealousy_bgm_{mode}.pid"
            if os.path.exists(pid_file):
                try:
                    with open(pid_file, "r") as f:
                        pid = f.read().strip()
                        if pid.isdigit():
                            subprocess.run(["kill", "-9", pid], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    os.remove(pid_file)
                except Exception:
                    pass
        
        log("✨ Cleanup complete")

# Global Process Manager
proc_manager = ProcessManager()

def log(message):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")


def run_script(script_path, args=None, async_mode=True):
    """Execute worker script"""
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
    """Native macOS notification"""
    script = f'display notification "{message}" with title "{title}" sound name "Purr"'
    subprocess.Popen(["osascript", "-e", script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# ══════════════════════════════════════════
# OS Interference Actions
# ══════════════════════════════════════════
def trigger_os_action(level):
    """Perform OS interference based on jealousy level"""
    now = time.time()
    if now - game.last_action_time < 5:
        return
    game.last_action_time = now

    if 20 <= level < 50:
        actions = [
            ("🖱️ The mouse started moving on its own!", CHAOTIC_MOUSE, []),
            ("😾 Hiss! You've been threatened!", PLAY_HISS, []),
        ]
        action = random.choice(actions)
        log(action[0])
        run_script(OVERLAY_EFFECTS, ["popup", SYSTEM_CAT_ICON, "Jealousy Event", action[0], "default"], async_mode=True)
        run_script(action[1], action[2] or None)

    elif 50 <= level < 80:
        actions = [
            ("🪟 A window was hidden unexpectedly!", HIDE_WIN, []),
            ("🌗 The screen theme was inverted!", TOGGLE_THEME, []),
            ("🐈‍⬛ A black cat started roaming the screen!", ROAMING_CAT, []),
            ("😼 A browser search for cheating owners has begun!", JEALOUS_BROWSER, []),
        ]
        action = random.choice(actions)
        log(action[0])
        run_script(OVERLAY_EFFECTS, ["popup", SYSTEM_CAT_ICON, "Severe Jealousy", action[0], "default"], async_mode=True)
        run_script(action[1], action[2] or None)

    elif 80 <= level < 100:
        actions = [
            ("👻 Eerie characters appeared in the terminal...!", TERMINAL_GHOST, []),
            ("📝 Something is being typed in the text editor...", TYPE_MSG, []),
        ]
        action = random.choice(actions)
        log(action[0])
        run_script(OVERLAY_EFFECTS, ["popup", SYSTEM_CAT_ICON, "DANGER", action[0], "default"], async_mode=True)
        run_script(action[1], action[2] or None)

    elif level >= 100:
        log("💀 Jealousy level at max! Starting reconciliation sequence...")
        run_script(OVERLAY_EFFECTS, ["popup", SYSTEM_CAT_ICON, "CRITICAL ERROR", "The jealous cat's rage has peaked!", "default"], async_mode=True)
        run_script(THREATEN_PROC)
        game.game_phase = "reconciling"
        game._write_state()


# ══════════════════════════════════════════
# Reconciliation Handling
# ══════════════════════════════════════════
def run_reconciliation():
    """Execute reconciliation sequence"""
    log("🎤 Starting reconciliation sequence...")

    from reconcile_dialog import show_reconcile_sequence
    success, text = show_reconcile_sequence()

    if success:
        log(f"🎉 Reconciliation successful! User said: {text}")

        # Immediately hide cats
        game.jealousy_level = 0
        game.pets_count = 0
        game.game_phase = "ending"
        game._write_state()

        # Kill any active interference scripts immediately
        for script in ["roaming_cat.py", "follow_mouse_cat.py", "chaotic_mouse.swift"]:
            try:
                subprocess.run(["pkill", "-9", "-f", script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass

        log("🎨 Generating Happy Ending wallpaper...")
        try:
            run_script(GENERATE_WALLPAPER, [RECONCILIATION_IMG], async_mode=False)
        except Exception:
            pass
        run_script(SET_WALLPAPER, [RECONCILIATION_IMG])

        run_script(PLAY_BGM, ["stop", "jealous"])
        run_script(PLAY_BGM, ["start", "healing"], async_mode=True)

        run_script(OVERLAY_EFFECTS, ["popup", str(SYSTEM_CAT_ICON), "🎉 Happy End", "You've reconciled with the jealous cat!\nThe desktop wallpaper has been updated.", "default"], async_mode=True)
        notify("🎉 Jealousy.sys — Happy End!", "Reconciled with the jealous cat! Desktop updated.")

        log("✨ Game Clear! Desktop wallpaper set.")

        time.sleep(8)
        log("👋 Enjoy your new desktop. Exiting game...")
        game.is_running = False
        game._write_state()
    else:
        log("❌ Reconciliation failed...")
        game.jealousy_level = 90
        game.game_phase = "playing"
        game._write_state()
        time.sleep(3)


# ══════════════════════════════════════════
# Background Threads
# ══════════════════════════════════════════
def jealousy_tick_loop():
    """Periodically execute actions based on jealousy level"""
    while game.is_running:
        time.sleep(4)

        game.sync_from_file()
        if not game.is_running:
            break

        if game.game_phase == "reconciling":
            run_reconciliation()
            continue

        if game.game_phase != "playing":
            continue

        level = game.jealousy_level
        if level <= 0:
            continue

        # Whisper
        if level > 20 and random.random() < 0.25:
            run_script(WHISPER, [str(int(level))])

        # OS Interference
        trigger_os_action(level)


def auto_escalation_loop():
    """Demo: Auto-escalate jealousy"""
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
                log(f"⏰ Auto-escalation +{increase} → {game.jealousy_level}%")


def sensor_loop(use_vision=False):
    """Thread to increase jealousy via sensors"""
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
                            log(f"👀 Vision Detection [Cheat Detected]: {data.get('reason', '')}")
                            action = data.get("action", "looking")
                            game.on_pet(action=action)
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
                    log(f"👀 User distracted by '{active_app}'!")
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
    """Periodically write status file (Every 1 second)"""
    while game.is_running:
        game._write_state()
        
        # Check for manual reconciliation request
        if os.path.exists(RECONCILE_FLAG_FILE):
            try:
                os.remove(RECONCILE_FLAG_FILE)
            except Exception:
                pass
            with game.lock:
                if game.game_phase == "playing":
                    game.game_phase = "reconciling"
                    log("🐟 Received reconciliation request from Menu Bar!")

        time.sleep(1)


# ══════════════════════════════════════════
# Main
# ══════════════════════════════════════════
def show_intro():
    """Game start native dialog"""
    script = '''
    display dialog "A jealous cat has taken up residence in your OS.

🐱 Cat A (Healing Cat) — A harmless cat that appeared on your desktop.
🐈‍⬛ Cat B (Jealous Cat) — Lurking and monitoring from your Menu Bar (top-right).

Petting Cat A (by clicking/hovering)...
...will make Cat B jealous, and it will start taking over your OS!

Appease the cat and reach the Happy Ending!
(Hint: If jealousy hits the limit, a sincere apology might be your only way out.)" with title "🐈‍⬛ Jealousy.sys — The Jealous OS" buttons {"Start Game!"} default button 1 with icon note
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
            print("🐈‍⬛ Jealousy.sys — Native Edition")
            print()
            print("Usage:")
            print("  python native_game.py               Auto-escalation (Demo)")
            print("  python native_game.py --sensor      Active window monitoring mode")
            print("  python native_game.py --vision      Gemini Vision monitoring mode")
            return

    # ── Intro ──
    print()
    print("═" * 55)
    print("  🐈‍⬛  J E A L O U S Y . S Y S")
    print("  ─── The Jealous OS ───")
    print("═" * 55)
    print()

    show_intro()

    # ── Dependencies & Env Check ──
    try:
        from PIL import Image, ImageTk
    except ImportError:
        log("❌ Error: Pillow is not installed. Run 'pip install Pillow'.")
        sys.exit(1)

    if not os.environ.get("GEMINI_API_KEY"):
        log("⚠️ Warning: GEMINI_API_KEY is not set. Features like browser hijacking will not work.")
        notify("⚠️ Jealousy.sys", "Some features are limited as the API key is missing.")

    log("🎬 Game Start!")
    log(f"📡 Mode: {mode}")

    # ── Signal Handlers ──
    def signal_handler(sig, frame):
        log(f"\n✋ Signal received ({sig}). Exiting...")
        game.is_running = False
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    atexit.register(proc_manager.cleanup)

    # ── Start BGM ──
    run_script(PLAY_BGM, ["start", "healing"], async_mode=True)

    # ── Launch Menu Bar App in a separate process ──
    menubar_proc = None
    try:
        menubar_proc = subprocess.Popen(
            [sys.executable, os.path.join(BASE_DIR, "menubar_app.py")],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        log("📊 Started Menu Bar App in a separate process")
    except Exception as e:
        log(f"⚠️ Failed to start Menu Bar ({e})")

    # ── Background Threads ──
    threads = []

    # Sync thread
    sync_thread = threading.Thread(target=state_sync_loop, daemon=True)
    sync_thread.start()
    threads.append(sync_thread)

    # Tick thread
    tick_thread = threading.Thread(target=jealousy_tick_loop, daemon=True)
    tick_thread.start()
    threads.append(tick_thread)

    # Mode-specific threads
    if mode == "sensor":
        log("📡 Starting active window monitoring...")
        t = threading.Thread(target=sensor_loop, args=(False,), daemon=True)
        t.start()
        threads.append(t)
    elif mode == "vision":
        log("📡 Starting Gemini Vision monitoring...")
        t = threading.Thread(target=sensor_loop, args=(True,), daemon=True)
        t.start()
        threads.append(t)
    else:
        log("⏰ Auto-escalation mode (Demo)")
        t = threading.Thread(target=auto_escalation_loop, daemon=True)
        t.start()
        threads.append(t)

    # ── Launch Healing Cat Window (Main Thread) ──
    log("🐱 Launching Healing Cat window...")
    try:
        from healing_cat_window import HealingCatWindow
        cat_window = HealingCatWindow(game_state=game)
        log("🐱 The Healing Cat has appeared on your desktop! Click/Hover to pet♪")
        
        def check_running():
            if not game.is_running:
                cat_window.root.destroy()
                return
            cat_window.root.after(500, check_running)
        
        cat_window.root.after(500, check_running)
        cat_window.run()  # tkinter mainloop

    except KeyboardInterrupt:
        log("🛑 Game ended (KeyboardInterrupt)")
    except Exception as e:
        log(f"❌ Healing Cat window error: {e}")
    finally:
        # ── Cleanup ──
        log("🛑 Running termination process...")
        game.is_running = False
        game._write_state()

        run_script(PLAY_BGM, ["stop", "jealous"], async_mode=False)
        run_script(PLAY_BGM, ["stop", "healing"], async_mode=False)

        proc_manager.cleanup()

        try:
            if os.path.exists(SHARED_STATE_FILE):
                os.remove(SHARED_STATE_FILE)
        except Exception:
            pass
        
        log("👋 Jealousy.sys closed.")
        os._exit(0)


if __name__ == "__main__":
    main()
