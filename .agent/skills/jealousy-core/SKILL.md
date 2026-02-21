---
name: jealousy-os-actions
description: "When the user focuses on another target (e.g., Cat A), this skill performs actions by controlling macOS to express jealousy and grab attention."
---

# Jealousy OS Actions

## 🎯 Purpose
Monitors the user's audio and screen behavior and autonomously performs OS-level interference based on the jealousy level (0-100).

## 🛠 Provided Scripts (Worker API)
While this skill is active, the following scripts can be executed via `run_command` to perform physical interference:
- `scripts/chaotic_mouse.swift`: Shakes the mouse slightly (expression of frustration).
- `scripts/cat_pounce.swift`: Pounces on the mouse cursor and drags it (invitation to play/interference).
- `scripts/follow_mouse_cat.py`: Displays a cat image that follows the mouse cursor.
- `scripts/cat_scratch.py`: Displays scratch marks on the screen (flash effect).
- `scripts/hide_win.sh`: Hides the application the user is currently viewing.
- `scripts/type_msg.py`: Opens TextEdit and types a message directly (e.g., `"Look at me..."`).
- `scripts/threaten_process.sh`: Opens Activity Monitor and hints at a force-quit.

## 📝 Execution Logic (Supervisor Demo Scenario)
Currently, `main_loop.py` is provided as a demo scenario for hackathons.

1. **Timeline Control:**
   - Running `python main_loop.py --demo` automatically increases the jealousy level and calls each script progressively.
2. **Manual Intervention by Agent (Agent Action):**
   - While interacting with the user (judge) in chat, if the AI agent determines that "jealousy is high," it can trigger surprises directly by running scripts like `type_msg.py "Even though I'm right here..."`.
3. **Reconciliation:**
   - If the user apologizes to you (the system) with words like "I like you the most" or "I'm sorry," the jealousy level resets and reconciliation occurs (currently functions as a manual or chat-based production).


## ⚠️ Constraints
- Do not delete the user's actual data files (.doc, .pdf, .py, etc.).
- Interference should remain within the bounds of "cute unreasonableness."
