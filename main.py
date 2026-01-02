import os
import threading
import asyncio
from datetime import datetime

# UI Imports
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.toast import toast
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.utils import platform

# Logic Imports
from telethon import TelegramClient, events
import arabic_reshaper
from bidi.algorithm import get_display

# --- UI Layout ---
KV = '''
<FeedItem>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(260)
    padding: dp(8)
    spacing: dp(8)
    elevation: 2
    radius: [12]
    md_bg_color: 0.15, 0.15, 0.15, 1
    
    # חלק עליון: תמונה וטקסט
    MDBoxLayout:
        spacing: dp(10)
        size_hint_y: 0.7
        
        AsyncImage:
            source: root.image_path
            size_hint_x: 0.35
            allow_stretch: True
            keep_ratio: True
            radius: [8]
        
        MDBoxLayout:
            orientation: 'vertical'
            size_hint_x: 0.65
            
            MDLabel:
                text: root.time_str
                theme_text_color: "Secondary"
                font_style: "Caption"
                size_hint_y: None
                height: dp(20)

            MDLabel:
                text: root.text_content
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                font_style: "Body2"
                valign: "top"
                text_size: self.width, None
                shorten: True
                shorten_from: 'right'

    # חלק תחתון: כפתורים
    MDBoxLayout:
        size_hint_y: 0.3
        spacing: dp(10)
        
        MDRaisedButton:
            text: "Details / Edit"
            on_release: app.open_details(root)
            
        MDRaisedButton:
            text: "Quick Send"
            md_bg_color: 0, 0.7, 0, 1
            on_release: root.send_background()
            
        MDLabel:
            id: status
            text: ""
            theme_text_color: "Hint"
            halign: "center"

ScreenManager:
    LoginScreen:
    MainScreen:

<LoginScreen>:
    name: 'login'
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 0.1, 0.1, 0.1, 1
        padding: dp(40)
        spacing: dp(20)
        
        MDLabel:
            text: "PASIFLONET LOGIN"
            halign: "center"
            font_style: "H4"
            theme_text_color: "Custom"
            text_color: 0, 1, 1, 1
            
        MDTextField:
            id: phone_input
            hint_text: "Phone Number (+972...)"
            mode: "rectangle"
            
        MDRaisedButton:
            text: "Connect / Send Code"
            pos_hint: {"center_x": 0.5}
            on_release: app.start_login()
            
        MDTextField:
            id: code_input
            hint_text: "Code"
            mode: "rectangle"
            disabled: True
            
        MDRaisedButton:
            id: verify_btn
            text: "Verify Code"
            disabled: True
            pos_hint: {"center_x": 0.5}
            on_release: app.verify_code()

<MainScreen>:
    name: 'main'
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 0, 0, 0, 1
        
        MDTopAppBar:
            title: "Pasiflonet Feed"
            right_action_items: [["refresh", lambda x: app.refresh()]]
            
        ScrollView:
            MDBoxLayout:
                id: feed_container
                orientation: 'vertical'
                adaptive_height: True
                padding: dp(10)
                spacing: dp(15)
'''

class FeedItem(MDCard):
    text_content = StringProperty("Loading...")
    time_str = StringProperty("--:--")
    image_path = StringProperty("loading.png")
    
    def __init__(self, message, client, **kwargs):
        super().__init__(**kwargs)
        self.message = message
        self.client = client
        self.msg_id = message.id
        
        # התחלת הורדת תמונה ממוזערת ברקע
        threading.Thread(target=self.load_thumbnail).start()

    def load_thumbnail(self):
        try:
            if self.message.photo or self.message.video:
                # מוריד רק את ה-Thumbnail הקטן (מהיר מאוד)
                path = self.client.loop.run_until_complete(
                    self.message.download_media(file=f"thumb_{self.msg_id}", thumb=1)
                )
                if path:
                    Clock.schedule_once(lambda x: setattr(self, 'image_path', path))
        except Exception as e:
            print(f"Thumb error: {e}")

    def send_background(self):
        self.ids.status.text = "Queued..."
        # כאן תהיה הלוגיקה של הוספה לתור העיבוד
        app = MDApp.get_running_app()
        app.background_worker.add_task(self)

    def mark_done(self):
        self.ids.status.text = "SENT! ✅"

class BackgroundWorker:
    def __init__(self):
        self.queue = []
        self.running = False
        
    def add_task(self, item):
        self.queue.append(item)
        if not self.running:
            threading.Thread(target=self.run).start()
            
    def run(self):
        self.running = True
        while self.queue:
            item = self.queue.pop(0)
            Clock.schedule_once(lambda x: setattr(item.ids.status, 'text', "Processing..."))
            
            # סימולציה של עיבוד (כאן יהיה FFmpeg בהמשך)
            import time
            time.sleep(2) 
            
            Clock.schedule_once(lambda x: item.mark_done())
        self.running = False

class PasiflonetApp(MDApp):
    client = None
    phone_hash = None
    background_worker = BackgroundWorker()
    
    API_ID = 26569766
    API_HASH = 'YOUR_HASH_HERE'

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Cyan"
        return Builder.load_string(KV)

    def on_start(self):
        self.request_perms()
        # יצירת קובץ דמי לתמונה
        if not os.path.exists("loading.png"):
            with open("loading.png", "wb") as f: f.write(b"")

    def request_perms(self):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE, 
                Permission.WRITE_EXTERNAL_STORAGE, 
                Permission.INTERNET
            ])

    # --- לוגיקת התחברות ---
    def start_login(self):
        phone = self.root.get_screen('login').ids.phone_input.text
        if not phone: return
        
        self.client = TelegramClient('pasiflon_session', self.API_ID, self.API_HASH)
        
        def _connect():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.client.loop = loop
            loop.run_until_complete(self.client.connect())
            
            if loop.run_until_complete(self.client.is_user_authorized()):
                Clock.schedule_once(lambda x: self.switch_to_main())
                loop.run_until_complete(self.listen())
            else:
                res = loop.run_until_complete(self.client.send_code_request(phone))
                self.phone_hash = res.phone_code_hash
                Clock.schedule_once(lambda x: self.enable_code_input())
                
        threading.Thread(target=_connect).start()

    def enable_code_input(self):
        screen = self.root.get_screen('login')
        screen.ids.code_input.disabled = False
        screen.ids.verify_btn.disabled = False
        toast("Code Sent!")

    def verify_code(self):
        code = self.root.get_screen('login').ids.code_input.text
        phone = self.root.get_screen('login').ids.phone_input.text
        
        def _verify():
            try:
                loop = self.client.loop
                loop.run_until_complete(self.client.sign_in(phone, code, phone_code_hash=self.phone_hash))
                Clock.schedule_once(lambda x: self.switch_to_main())
                loop.run_until_complete(self.listen())
            except Exception as e:
                toast(f"Login Error: {e}")
                
        threading.Thread(target=_verify).start()

    def switch_to_main(self):
        self.root.current = 'main'

    # --- האזנה להודעות ---
    async def listen(self):
        @self.client.on(events.NewMessage)
        async def handler(event):
            Clock.schedule_once(lambda x: self.add_to_feed(event))
        await self.client.run_until_disconnected()

    def add_to_feed(self, event):
        container = self.root.get_screen('main').ids.feed_container
        
        # סידור טקסט בעברית
        raw_text = event.text if event.text else "Media File"
        fixed_text = get_display(arabic_reshaper.reshape(raw_text))
        time_str = event.date.strftime("%H:%M")
        
        item = FeedItem(event, self.client, text_content=fixed_text, time_str=time_str)
        container.add_widget(item, index=0)

    def open_details(self, item):
        toast("Opening Details...") 
        # בהמשך נוסיף את המעבר לחלון עריכה

if __name__ == '__main__':
    PasiflonetApp().run()
