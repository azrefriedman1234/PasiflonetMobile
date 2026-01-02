import os
import sys
import threading
import logging
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.toast import toast
from kivy.utils import platform
from kivy.clock import Clock
from kivy.core.window import Window

# --- Layout לרוחב ---
KV = '''
ScreenManager:
    MainScreen:

<MainScreen>:
    name: 'main'
    MDBoxLayout:
        orientation: 'horizontal'  # פריסה לרוחב
        padding: 10
        spacing: 10
        md_bg_color: 0.05, 0.05, 0.05, 1
        
        # צד ימין - תפריט וכפתורים
        MDBoxLayout:
            orientation: 'vertical'
            size_hint_x: 0.3
            spacing: 20
            
            MDLabel:
                text: "PASIFLONET\\nCONTROL"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0, 1, 1, 1
                font_style: "H6"
                size_hint_y: None
                height: dp(80)

            MDRaisedButton:
                text: "Check FFmpeg"
                size_hint_x: 0.9
                pos_hint: {"center_x": 0.5}
                on_release: app.check_ffmpeg()
            
            MDRaisedButton:
                text: "Clear Logs"
                size_hint_x: 0.9
                pos_hint: {"center_x": 0.5}
                md_bg_color: 0.3, 0.3, 0.3, 1
                on_release: app.clear_logs()

            Widget: # סתם מרווח

        # צד שמאל - לוגים ומסך ראשי
        MDBoxLayout:
            orientation: 'vertical'
            md_bg_color: 0, 0, 0, 1
            radius: [10]
            padding: 10
            
            MDLabel:
                text: "System Logs:"
                theme_text_color: "Secondary"
                size_hint_y: None
                height: dp(30)
                
            ScrollView:
                MDLabel:
                    id: log_label
                    text: "Initializing..."
                    theme_text_color: "Custom"
                    text_color: 0, 1, 0, 1
                    size_hint_y: None
                    height: self.texture_size[1]
                    valign: "top"
'''

class PasiflonetApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Cyan"
        return Builder.load_string(KV)

    def on_start(self):
        # 1. בקשת הרשאות קריטית למניעת קריסה
        self.request_android_permissions()
        self.log("App Started in Landscape Mode")
        self.log(f"Current Directory: {os.getcwd()}")

    def request_android_permissions(self):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            def callback(permission, results):
                if all([res for res in results]):
                    self.log("Permissions Granted! ✅")
                else:
                    self.log("Permissions Denied! ❌ App might crash.")

            request_permissions(
                [Permission.READ_EXTERNAL_STORAGE, 
                 Permission.WRITE_EXTERNAL_STORAGE, 
                 Permission.INTERNET], 
                callback
            )
        else:
            self.log("Not on Android, skipping permissions.")

    def check_ffmpeg(self):
        self.log("Checking for FFmpeg...")
        # נסיון להריץ פקודה פשוטה
        import subprocess
        try:
            # באנדרואיד הפקודה ffmpeg לא תמיד ב-PATH, ננסה ונתפוס שגיאה
            cmd = ["ffmpeg", "-version"]
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = process.communicate()
            
            if process.returncode == 0:
                self.log("FFmpeg found! ✅")
                self.log(str(out)[:100])
            else:
                self.log("FFmpeg command failed (might need full path)")
                self.log(f"Error: {err}")
        except FileNotFoundError:
            self.log("FFmpeg binary NOT found in PATH ❌")
        except Exception as e:
            self.log(f"Error checking FFmpeg: {e}")

    def log(self, text):
        # פונקציה שכותבת למסך כדי שתראה מה קורה
        msg = f"\n> {text}"
        if self.root:
            lbl = self.root.get_screen('main').ids.log_label
            lbl.text += msg
        print(msg)

    def clear_logs(self):
        self.root.get_screen('main').ids.log_label.text = "Logs Cleared."

if __name__ == '__main__':
    try:
        PasiflonetApp().run()
    except Exception as e:
        # תופס קריסות קריטיות
        print(f"CRITICAL ERROR: {e}")
