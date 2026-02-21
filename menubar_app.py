#!/usr/bin/env python3
# menubar_app.py
# メニューバーに嫉妬ゲージを表示する常駐アプリ
# 別プロセスとして起動し、共有状態ファイル経由でゲーム状態を読み取る

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
        # アイコン画像のパスを確認
        self.icon_path = os.path.join(BASE_DIR, "assets", "system_cat_icon.png")
        if not os.path.exists(self.icon_path):
            self.icon_path = None

        super().__init__(
            "Jealousy.sys",
            title=" 0%" if self.icon_path else "😺 0%",
            icon=self.icon_path,
            quit_button=None,
        )

        self.level_item = rumps.MenuItem("嫉妬レベル: ░░░░░░░░░░ 0%")
        self.stage_item = rumps.MenuItem("ステージ: 😺 平穏")
        self.pets_item = rumps.MenuItem("ナデナデ回数: 0 回")
        self.pet_action_item = rumps.MenuItem("👋 ナデナデする", callback=self.on_pet)
        self.reconcile_item = rumps.MenuItem("🐟 仲直りする", callback=self.on_reconcile)
        self.quit_item = rumps.MenuItem("🛑 ゲーム終了", callback=self.on_quit)

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
        
        # 起動時に自己主張する
        rumps.notification(
            title="🐈‍⬛ Jealousy.sys",
            subtitle="ここから見てるよ...",
            message="嫉妬猫はメニューバーに潜んでいます。浮気したら許さないからね。",
            sound=True
        )

    def on_pet(self, _):
        """嫉妬猫をナデナデする"""
        state = read_game_state()
        level = state.get("jealousy_level", 0)
        
        # 嫉妬レベルを下げる（機嫌をとる）
        import random
        decrease = random.randint(3, 8)
        new_level = max(0, level - decrease)
        state["jealousy_level"] = new_level
        
        # 状態保存
        try:
            with open(SHARED_STATE_FILE, "w") as f:
                json.dump(state, f)
        except Exception:
            pass
            
        # 反応
        msgs = [
            "ふん、悪くないわね。",
            "もっと撫でなさいよ。",
            "別に嬉しくないんだからね！",
            "...ゴロゴロ...",
            "浮気相手よりボクの方がいいでしょ？"
        ]
        msg = random.choice(msgs)
        
        rumps.notification(
            title="🐈‍⬛ Jealousy.sys",
            subtitle="ナデナデしました",
            message=msg,
            sound=False
        )

    def on_reconcile(self, _):
        """ユーザーが手動で和解を求めた場合"""
        # フラグファイルを作成して native_game.py に通知
        try:
            with open(RECONCILE_FLAG_FILE, "w") as f:
                f.write("requested")
            rumps.notification(
                title="🐈‍⬛ Jealousy.sys",
                subtitle="アプローチ中...",
                message="嫉妬猫に話しかけてみます...",
                sound=False
            )
        except Exception as e:
            print(f"Error creating reconcile flag: {e}")

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

        emoji_icon = self.STAGE_ICONS.get(stage, "😺")
        name = self.STAGE_NAMES.get(stage, "不明")

        # メニューバータイトル
        if self.icon_path:
            self.title = f" {level}%"
            # アイコンも更新したいが、rumpsでは画像を動的に変えるのは少し面倒。
            # 一旦静的なアイコンを維持しつつ、もし画像がなければ絵文字を使う。
            self.icon = self.icon_path
        else:
            self.title = f"{emoji_icon} {level}%"

        # メニュー項目
        filled = level // 10
        empty = 10 - filled
        self.level_item.title = f"嫉妬レベル: {'█' * filled}{'░' * empty} {level}%"
        self.stage_item.title = f"ステージ: {emoji_icon} {name}"
        self.pets_item.title = f"ナデナデ回数: {pets} 回"


if __name__ == "__main__":
    app = JealousyMenuBarApp()
    app.run()
