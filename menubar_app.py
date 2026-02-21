#!/usr/bin/env python3
# menubar_app.py
# メニューバーに嫉妬ゲージを表示する常駐アプリ
# 別プロセスとして起動し、共有状態ファイル経由でゲーム状態を読み取る

import os
import sys
import json
import time

SHARED_STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".game_state.json")

try:
    import rumps
except ImportError:
    print("⚠️ rumps not installed. Install with: pip install rumps")
    sys.exit(1)


def read_game_state():
    """共有状態ファイルからゲーム状態を読み取る"""
    try:
        if os.path.exists(SHARED_STATE_FILE):
            with open(SHARED_STATE_FILE, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return {"jealousy_level": 0, "pets_count": 0, "stage": "calm", "game_phase": "playing"}


class JealousyMenuBarApp(rumps.App):
    """メニューバーに嫉妬ステータスを表示"""

    STAGE_ICONS = {
        "calm":      "😺",
        "annoyance": "😾",
        "obsession": "🙀",
        "rage":      "😈",
        "max":       "💀",
    }

    STAGE_NAMES = {
        "calm":      "平穏",
        "annoyance": "イライラ",
        "obsession": "執着",
        "rage":      "暴走",
        "max":       "限界突破",
    }

    def __init__(self):
        super().__init__(
            "Jealousy.sys",
            title="😺 0%",
            quit_button=None,
        )

        self.level_item = rumps.MenuItem("嫉妬レベル: ░░░░░░░░░░ 0%")
        self.stage_item = rumps.MenuItem("ステージ: 😺 平穏")
        self.pets_item = rumps.MenuItem("ナデナデ回数: 0 回")
        self.quit_item = rumps.MenuItem("🛑 ゲーム終了", callback=self.on_quit)

        self.menu = [
            self.level_item,
            self.stage_item,
            self.pets_item,
            None,  # separator
            self.quit_item,
        ]

    def on_quit(self, _):
        # 終了シグナルを書き込み
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
        """1秒ごとにゲーム状態を読み取って表示を更新"""
        state = read_game_state()
        level = state.get("jealousy_level", 0)
        stage = state.get("stage", "calm")
        pets = state.get("pets_count", 0)

        icon = self.STAGE_ICONS.get(stage, "😺")
        name = self.STAGE_NAMES.get(stage, "不明")

        # メニューバータイトル
        self.title = f"{icon} {level}%"

        # メニュー項目
        filled = level // 10
        empty = 10 - filled
        self.level_item.title = f"嫉妬レベル: {'█' * filled}{'░' * empty} {level}%"
        self.stage_item.title = f"ステージ: {icon} {name}"
        self.pets_item.title = f"ナデナデ回数: {pets} 回"


if __name__ == "__main__":
    app = JealousyMenuBarApp()
    app.run()
