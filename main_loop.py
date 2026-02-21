#!/usr/bin/env python3
# main_loop.py
# Jealousy.sys - Main Loop for Supervisor Agent
# Increases jealousy level based on time or specific events and runs worker scripts for each level.

import os
import sys
import time
import subprocess
import random
from datetime import datetime

# Constants: Paths to scripts
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

# New Cat Interaction Scripts
FOLLOW_MOUSE_CAT = os.path.join(SCRIPTS_DIR, "follow_mouse_cat.py")
CAT_POUNCE = os.path.join(SCRIPTS_DIR, "cat_pounce.swift")
CAT_SCRATCH = os.path.join(SCRIPTS_DIR, "cat_scratch.py")
JEALOUS_BROWSER = os.path.join(SCRIPTS_DIR, "jealous_browser_hijack.py")

# Scripts for OS Hacks
TOGGLE_THEME = os.path.join(SCRIPTS_DIR, "os_hacks", "toggle_dark_mode.sh")
TERMINAL_GHOST = os.path.join(SCRIPTS_DIR, "os_hacks", "terminal_ghost.sh")
PLAY_BGM = os.path.join(SCRIPTS_DIR, "play_bgm.sh")

# Wrapper function for process execution
def run_worker(script_path, args=None, async_mode=False):
    if not os.path.exists(script_path):
        print(f"❌ [Error] Script not found: {script_path}")
        return

    cmd = [script_path]
    
    # Determine execution method based on extension
    if script_path.endswith(".py"):
        cmd = [sys.executable, script_path] 
    
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
        self.log("Jealousy.sys Supervisor started. Waiting for target (Cat A)...")

    def check_active_window(self):
        """Get the name of the currently active window using a sensor"""
        try:
            result = subprocess.run([sys.executable, SENSOR], capture_output=True, text=True, check=True)
            return result.stdout.strip()
        except Exception:
            return "Unknown"

    def check_vision_sensor(self):
        """Determine if a cat is on screen using the Vision API sensor"""
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
        self.log(f"😡 Jealousy level up: {self.jealousy_level}/100")
        self.check_thresholds()

    def check_thresholds(self):
        """Trigger actions based on the current jealousy level"""
        
        # Level 1: Annoyance
        if 20 <= self.jealousy_level < 50:
            self.log("⚡ [Level 1: Annoyance] - Mouse shakes, cat starts following")
            run_worker(CAT_TOAST, ["1", "Look at me, meow..."], async_mode=True)
            run_worker(PLAY_BGM, ["start", "jealous"], async_mode=True)
            run_worker(FOLLOW_MOUSE_CAT, async_mode=True)
            run_worker(CHAOTIC_MOUSE, async_mode=True)
            run_worker(PLAY_HISS, async_mode=True)
            
        # Level 2: Obsession
        elif 50 <= self.jealousy_level < 80:
            self.log("⚡ [Level 2: Obsession] - Hiding windows, scratch marks, mouse hijacking")
            run_worker(CAT_TOAST, ["2", "I'll leave my marks, meow!"], async_mode=True)
            run_worker(CAT_SCRATCH, async_mode=True)
            run_worker(CAT_POUNCE, async_mode=True)
            run_worker(HIDE_WIN)
            run_worker(TOGGLE_THEME, async_mode=True)
            run_worker(ROAMING_CAT, async_mode=True)
            
            # 20% chance to hijack the browser
            if random.random() < 0.2:
                self.log("😼 [Obsession] - Hijacking browser for investigation...")
                run_worker(JEALOUS_BROWSER, async_mode=True)
            
        # Level 3: Rage
        elif 80 <= self.jealousy_level < 100:
            self.log("⚡ [Level 3: Rage] - Typing messages and eerie terminal ghosting")
            run_worker(CAT_TOAST, ["3", "I can't take this anymore, meow... talk to me!"], async_mode=True)
            run_worker(TYPE_MSG, ["Look only at me... please..."], async_mode=True)
            run_worker(TERMINAL_GHOST, async_mode=True)
            
        # MAX (Hackathon Demo)
        elif self.jealousy_level >= 100:
            self.log("⚡ [MAX: Danger] - Displaying threat dialog")
            run_worker(CAT_TOAST, ["MAX", "I'm at my limit, meow... it's all over"], async_mode=True)
            run_worker(THREATEN_PROC)
            
            # For demo: trigger reconciliation when MAX is reached
            time.sleep(3)
            self.log("🎤 [Reconciliation] - Starting voice chat (via Live API) and waiting for soothing words...")
            
            # Synchronous execution via subprocess to check for success
            try:
                result = subprocess.run([sys.executable, LIVE_RECONCILIATION], check=True)
                reconciled = True
            except subprocess.CalledProcessError:
                reconciled = False
                
            if reconciled:
                self.log("🎨 Dynamically generating Happy Ending wallpaper via Generative AI...")
                subprocess.run([sys.executable, GENERATE_WALLPAPER, RECONCILIATION_IMG])
                
                self.log("✨ [Reconciliation] - Setting reconciled image to desktop.")
                run_worker(SET_WALLPAPER, [RECONCILIATION_IMG])
                
                self.log("🛑 Jealousy peaked and successfully reconciled. Resetting demo scenario.")
                self.jealousy_level = 0
                run_worker(PLAY_BGM, ["stop", "jealous"])
                run_worker(PLAY_BGM, ["start", "healing"], async_mode=True)
                time.sleep(5) 
            else:
                self.log("❌ Reconciliation failed... jealousy level remains high.")
                self.jealousy_level = 90
                time.sleep(5) 

    def run_demo_scenario(self, use_sensor=False, use_vision=False):
        """
        Timeline script for hackathon demo
        """
        if use_vision:
            self.log("🎬 Starting Vision-linked demo: Monitoring user via screen capture and Gemini API...")
        elif use_sensor:
            self.log("🎬 Starting sensor-linked demo: Monitoring active app focus...")
        elif self.jealousy_level == 0:
            run_worker(PLAY_BGM, ["start", "healing"], async_mode=True)
            self.log("🎬 Starting timeline demo: Jealousy level increases automatically...")
        
        try:
            while self.is_running:
                time.sleep(3) 
                
                if use_vision:
                    is_cheating, reason = self.check_vision_sensor()
                    if is_cheating:
                        self.log(f"👀 Vision Detection [Cheat detected]: {reason}")
                        self.increase_jealousy(15)
                    elif self.jealousy_level > 0:
                        self.log("😌 Vision Detection [Peaceful]: No other targets detected.")
                        self.jealousy_level = max(0, self.jealousy_level - 5)
                        time.sleep(2)
                
                # Occasionally whisper when jealousy is high
                if self.jealousy_level > 10 and random.random() < 0.3:
                    run_worker(WHISPER, [str(int(self.jealousy_level))], async_mode=True)
                
                elif use_sensor:
                    active_app = self.check_active_window()
                    target_apps = ["Google Chrome", "Safari", "Slack", "Discord", "YouTube", "Healing Cat Interface", "Petting Cat"]
                    is_distracted = any(target in active_app for target in target_apps)
                    
                    if is_distracted:
                        self.log(f"👀 Targeting: User is distracted by '{active_app}'!")
                        self.increase_jealousy(15)
                    elif self.jealousy_level > 0:
                        self.log(f"😌 Regaining composure (Current App: {active_app})")
                        self.jealousy_level = max(0, self.jealousy_level - 5)
                        time.sleep(2)
                else:
                    self.increase_jealousy(20)
                    time.sleep(2)
                
        except KeyboardInterrupt:
            self.log("🛑 Supervisor stopped by user.")
            self.is_running = False
        finally:
            self.log("🧹 Cleaning up...")
            run_worker(PLAY_BGM, ["stop", "jealous"])
            run_worker(PLAY_BGM, ["stop", "healing"])
            try:
                subprocess.run(["pkill", "-f", "afplay"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.run(["pkill", "-f", "roaming_cat.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                subprocess.run(["pkill", "-f", "follow_mouse_cat.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
            self.log("✨ Cleanup complete")

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
        print("💡   python main_loop.py --demo         : Auto-escalation demo")
        print("💡   python main_loop.py --sensor-demo  : Monitor active window demo")
        print("💡   python main_loop.py --vision-demo  : Monitor screen with Gemini Vision demo")
