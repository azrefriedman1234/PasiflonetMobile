import os
import sys
import logging
import threading
import asyncio
from datetime import datetime

# Kivy Imports
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.clock import Clock
from kivy.utils import platform
from kivymd.uix.card import MDCard
from kivy.properties import StringProperty

# Logic Imports
from telethon import TelegramClient, events
import arabic_reshaper
from bidi.algorithm import get_display

# --- UI Layout ---
KV = '''
<FeedItem>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(200)
    padding: dp(10)
    spacing: dp(5)
    elevation: 1
    radius: [10]
    md_bg_color: 0.2, 0.2, 0.2, 1
    
    MDBoxLayout:
        spacing: dp(10)
        AsyncImage:
            source: root.image_source
            size_hint_x: 0.3
            allow_stretch: True
            keep_ratio: True
        
        MDLabel:
            text: root.text_content
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
            font_style: "Body2"
            size_hint_x: 0.7
            valign: "top"

ScreenManager:
    MainScreen:

<MainScreen>:
    name: 'main'
    MDBoxLayout:
        orientation: 'horizontal'
        
        # תפריט צד (30%)
        MDBoxLayout:
            orientation: 'vertical'
            size_hint_x: 0.3
            md_bg_color: 0.1, 0.1, 0.1, 1
            padding: dp(10)
            spacing: dp(10)
            
            MDLabel:
                text: "STATUS"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0, 1, 1, 1
                font_style: "H6"
                size_hint_y: None
                height: dp(50)

            MDRaisedButton:
                text: "1. Connect Telegram"
                on_release: app.start_telegram()
                size_hint_x: 1

            MDRaisedButton:
                text: "2. Test FFmpeg"
                on_release: app.test_ffmpeg()
                size_hint_x: 1
                md_bg_color: 0.4, 0.4, 0.4, 1

            ScrollView:
                MDLabel:
                    id: logs
                    text: "System Ready..."
                    font_size: '10sp'
                    theme_text_color: "Custom"
                    text_color: 0, 1, 0, 1
                    size_hint_y: None
                    height: self.texture_size[1]

        # אזור הפיד (70%)
        MDBoxLayout:
            orientation: 'vertical'
            md_bg_color: 0, 0, 0, 1
            padding: dp(5)
            
            MDTopAppBar:
                title: "Pasiflonet Feed"
                id: toolbar
            
            ScrollView:
                MDBoxLayout:
                    id: feed_box
                    orientation: 'vertical'
                    adaptive_height: True
                    spacing: dp(10)
'''

class FeedItem(MDCard):
    image_source = StringProperty("loading.png")
    text_content = StringProperty("")

class PasiflonetApp(MDApp):
    client = None
    
    # --- הגדרות משתמש ---
    API_ID = 26569766
    API_HASH = 'YOUR_HASH_HERE'

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Cyan"
        return Builder.load_string(KV)

    def log(self, msg):
        # כותב למסך כדי שתראה שגיאות
        timestamp = datetime.now().strftime("%H:%M:%S")
        final_msg = f"[{timestamp}] {msg}\n"
        print(final_msg)
        if self.root:
            lbl = self.root.get_screen('main').ids.logs
            lbl.text += final_msg

    def get_safe_path(self, filename):
        # --- התיקון הקריטי לקריסות ---
        # באנדרואיד חייבים להשתמש בתיקייה פרטית לכתיבה
        if platform == 'android':
            base = self.user_data_dir
        else:
            base = os.getcwd()
        
        full_path = os.path.join(base, filename)
        return full_path

    def on_start(self):
        # לא מריצים שום דבר כבד בהתחלה!
        self.request_perms()
        
        # יצירת תמונת דמי במיקום בטוח
        safe_img = self.get_safe_path("loading.png")
        if not os.path.exists(safe_img):
            try:
                with open(safe_img, "wb") as f:
                    f.write(b"") # קובץ ריק רק שלא יקרוס
            except Exception as e:
                self.log(f"Error creating img: {e}")

    def request_perms(self):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE, 
                Permission.WRITE_EXTERNAL_STORAGE, 
                Permission.INTERNET
            ])

    def start_telegram(self):
        self.log("Starting Telegram connection...")
        threading.Thread(target=self._connect_thread).start()

    def _connect_thread(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # שימוש בקובץ session במיקום בטוח
            session_path = self.get_safe_path('pasiflon_session')
            self.log(f"Session path: {session_path}")
            
            self.client = TelegramClient(session_path, self.API_ID, self.API_HASH)
            
            # בדיקת התחברות
            self.client.connect()
            if not self.client.is_user_authorized():
                self.log("ERROR: Need to login via terminal first or add Login UI")
                # בהמשך נוסיף את ה-UI של ההתחברות חזרה, כרגע בודקים יציבות
            else:
                self.log("Connected Successfully! ✅")
                self.client.start()
                
                @self.client.on(events.NewMessage)
                async def handler(event):
                    text = event.text[:50] if event.text else "Media"
                    Clock.schedule_once(lambda x: self.add_item(text))
                
                self.log("Listening for messages...")
                loop.run_until_complete(self.client.run_until_disconnected())
                
        except Exception as e:
            self.log(f"Telegram Crash: {e}")

    def add_item(self, text):
        try:
            reshaped = get_display(arabic_reshaper.reshape(text))
            item = FeedItem()
            item.text_content = reshaped
            item.image_source = self.get_safe_path("loading.png")
            
            grid = self.root.get_screen('main').ids.feed_box
            grid.add_widget(item, index=0)
        except Exception as e:
            self.log(f"UI Error: {e}")

    def test_ffmpeg(self):
        import subprocess
        try:
            cmd = ["ffmpeg", "-version"]
            out = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            self.log("FFmpeg OK! ✅")
        except Exception as e:
            self.log(f"FFmpeg Error: {e}")

if __name__ == '__main__':
    try:
        PasiflonetApp().run()
    except Exception as e:
        print(f"CRITICAL: {e}")
