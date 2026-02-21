#!/usr/bin/env python3
# menubar_app.py
# Resident app that displays the jealousy gauge in the menu bar.
# Runs as a separate process and reads game state via a shared JSON file.

import os
import sys
import json
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SHARED_STATE_FILE = os.path.join(BASE_DIR, ".game_state.json")
RECONCILE_FLAG_FILE = os.path.join(BASE_DIR, ".reconcile_request")

try:
    import rumps
except ImportError:
    print("⚠️ rumps not installed. Install with: pip install rumps")
    sys.exit(1)


def read_game_state():
    """Read game state from shared status file"""
    try:
        if os.path.exists(SHARED_STATE_FILE):
            with open(SHARED_STATE_FILE, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return {"jealousy_level": 0, "pets_count": 0, "stage": "calm", "game_phase": "playing"}


class JealousyMenuBarApp(rumps.App):
    """Display jealousy status in the menu bar"""

    STAGE_ICONS = {
        "calm":      "😺",
        "annoyance": "😾",
        "obsession": "🙀",
        "rage":      "😈",
        "max":       "💀",
    }

    STAGE_NAMES = {
        "calm":      "Calm",
        "annoyance": "Annoyed",
        "obsession": "Obsessed",
        "rage":      "Raging",
        "max":       "Critical",
    }

    def __init__(self):
        # Check for icon image path
        self.icon_path = os.path.join(BASE_DIR, "assets", "system_cat_icon.png")
        if not os.path.exists(self.icon_path):
            self.icon_path = None

        super().__init__(
            "Jealousy.sys",
            title=" 0%" if self.icon_path else "😺 0%",
            icon=self.icon_path,
            quit_button=None,
        )

        self.level_item = rumps.MenuItem("Jealousy Level: ░░░░░░░░░░ 0%")
        self.stage_item = rumps.MenuItem("Stage: 😺 Calm")
        self.pets_item = rumps.MenuItem("Pets Count: 0 times")
        self.pet_action_item = rumps.MenuItem("👋 Give attention", callback=self.on_pet)
        self.reconcile_item = rumps.MenuItem("🐟 Make up", callback=self.on_reconcile)
        self.quit_item = rumps.MenuItem("🛑 Quit Game", callback=self.on_quit)

        self.menu = [
            self.pet_action_item,
            None, # separator
            self.level_item,
            self.stage_item,
            self.pets_item,
            None, # separator
            self.reconcile_item,
            None,  # separator
            self.quit_item,
        ]
        
        # Self-assertion on launch
        rumps.notification(
            title="🐈‍⬛ Jealousy.sys",
            subtitle="I'm watching you from here...",
            message="The jealous cat is hiding in your menu bar. Don't even think about cheating.",
            sound=True
        )

    def on_pet(self, _):
        """Give attention to the jealous cat to lower jealousy"""
        state = read_game_state()
        level = state.get("jealousy_level", 0)
        
        # Decrease jealousy level
        import random
        decrease = random.randint(3, 8)
        new_level = max(0, level - decrease)
        state["jealousy_level"] = new_level
        
        # Save state
        try:
            with open(SHARED_STATE_FILE, "w") as f:
                json.dump(state, f)
        except Exception:
            pass
            
        # Reaction
        msgs = [
            "Hmph, not bad.",
            "Stroke me more.",
            "It's not like I'm happy or anything!",
            "...Purr...",
            "I'm much better than that other cat, right?"
        ]
        msg = random.choice(msgs)
        
        rumps.notification(
            title="🐈‍⬛ Jealousy.sys",
            subtitle="Gave attention",
            message=msg,
            sound=False
        )

    def on_reconcile(self, _):
        """User manually requests reconciliation"""
        # Create flag file to notify native_game.py
        try:
            with open(RECONCILE_FLAG_FILE, "w") as f:
                f.write("requested")
            rumps.notification(
                title="🐈‍⬛ Jealousy.sys",
                subtitle="Approaching...",
                message="Attempting to talk to the jealous cat...",
                sound=False
            )
        except Exception as e:
            print(f"Error creating reconcile flag: {e}")

    def on_quit(self, _):
        # Set running flag to false to terminate main game
        try:
            state = read_game_state()
            state["is_running"] = False
            with open(SHARED_STATE_FILE, "w") as f:
                json.dump(state, f)
        except Exception:
            pass
        rumps.quit_application()

    @rumps.timer(1)
    def update_display(self, _):
        """Read game state and update display every 1 second"""
        state = read_game_state()
        if not state.get("is_running", True) or state.get("game_phase") == "ending":
            rumps.quit_application()
            return
            
        level = state.get("jealousy_level", 0)
        stage = state.get("stage", "calm")
        pets = state.get("pets_count", 0)

        emoji_icon = self.STAGE_ICONS.get(stage, "😺")
        name = self.STAGE_NAMES.get(stage, "Unknown")

        # Menu bar title
        if self.icon_path:
            self.title = f" {level}%"
            self.icon = self.icon_path
        else:
            self.title = f"{emoji_icon} {level}%"

        # Menu items
        filled = level // 10
        empty = 10 - filled
        self.level_item.title = f"Jealousy: {'█' * filled}{'░' * empty} {level}%"
        self.stage_item.title = f"Stage: {emoji_icon} {name}"
        self.pets_item.title = f"Pets: {pets} times"


if __name__ == "__main__":
    app = JealousyMenuBarApp()
    app.run()
