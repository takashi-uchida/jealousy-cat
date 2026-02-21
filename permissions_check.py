import sys
import time

def check_accessibility():
    try:
        import ApplicationServices
    except ImportError:
        print("❌ ApplicationServices module not found. Are you sure pyobjc is installed?")
        return False

    trusted = ApplicationServices.AXIsProcessTrusted()
    if trusted:
        print("✅ Accessibility (アクセシビリティ) permissions are GRANTED.")
        return True
    else:
        print("❌ Accessibility (アクセシビリティ) permissions are NOT GRANTED.")
        print("   Please grant Accessibility permissions to your Terminal or IDE in:")
        print("   System Settings -> Privacy & Security -> Accessibility")
        print("   (システム設定 -> プライバシーとセキュリティ -> アクセシビリティ)")
        
        # Optionally, we can prompt the OS to show the dialog
        options = {ApplicationServices.kAXTrustedCheckOptionPrompt: True}
        ApplicationServices.AXIsProcessTrustedWithOptions(options)
        return False

def check_screen_recording():
    # There's no perfect API for this without creating a window, but trying to capture the screen
    # will trigger the prompt if not granted on macOS.
    try:
        import Quartz.CoreGraphics as CG
        # Try to capture the screen to trigger the dialog
        image = CG.CGWindowListCreateImage(
            CG.CGRectInfinite, 
            CG.kCGWindowListOptionOnScreenOnly, 
            CG.kCGNullWindowID, 
            CG.kCGWindowImageDefault
        )
        if image is None:
            print("❌ Screen Recording (画面収録) permissions might NOT be GRANTED.")
            print("   Please grant Screen Recording permissions in System Settings -> Privacy & Security -> Screen Recording")
            return False
        else:
            print("✅ Screen Recording (画面収録) permissions appear to be GRANTED (or will be prompted).")
            return True
    except Exception as e:
        print(f"⚠️ Error checking screen recording: {e}")
        return False

if __name__ == "__main__":
    print("--- 🍎 macOS Permission Check ---")
    
    acc_granted = check_accessibility()
    
    # Wait a bit before checking screen recording to avoid overlapping dialogs
    time.sleep(1)
    
    scr_granted = check_screen_recording()
    
    print("---------------------------------")
    if acc_granted and scr_granted:
        print("🎉 All necessary macOS permissions are granted. You are ready to run Jealousy.sys!")
        sys.exit(0)
    else:
        print("⚠️ Please grant the necessary permissions before running the Jealousy.sys agents.")
        sys.exit(1)
