import os
import asyncio
import threading
import time
from datetime import datetime

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import StringProperty, ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.toast import toast
from kivy.utils import platform

from telethon import TelegramClient, events

# --- תמיכה בעברית ---
import arabic_reshaper
from bidi.algorithm import get_display

def hebrew(text):
    if not text: return ""
    try:
        return get_display(arabic_reshaper.reshape(text))
    except:
        return text

# --- ממשק המשתמש ---
KV = '''
<FeedItem>:
    orientation: 'vertical'
    size_hint_y: None
    height: dp(280)
    padding: dp(10)
    spacing: dp(10)
    elevation: 2
    radius: [15]
    md_bg_color: 0.15, 0.15, 0.15, 1

    MDBoxLayout:
        orientation: 'horizontal'
        size_hint_y: 0.7
        spacing: dp(10)

        # אזור התמונה (תצוגה מקדימה)
        AsyncImage:
            id: thumb_img
            source: root.image_source
            size_hint_x: 0.4
            allow_stretch: True
            keep_ratio: True
            radius: [10]

        # אזור הטקסט והפרטים
        MDBoxLayout:
            orientation: 'vertical'
            size_hint_x: 0.6
            
            MDLabel:
                text: root.timestamp
                theme_text_color: "Secondary"
                font_style: "Caption"
                size_hint_y: None
                height: dp(20)

            MDLabel:
                id: msg_text
                text: root.message_text
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                font_style: "Body2"
                valign: "top"
    
    # כפתורי פעולה
    MDBoxLayout:
        orientation: 'horizontal'
        size_hint_y: 0.3
        spacing: dp(10)
        
        MDRaisedButton:
            text: "SEND (Background)"
            md_bg_color: 0, 0.8, 0, 1
            on_release: root.send_to_background()

        MDLabel:
            id: status_label
            text: "Ready"
            halign: "center"
            theme_text_color: "Hint"

ScreenManager:
    MainScreen:

<MainScreen>:
    name: 'main'
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 0.05, 0.05, 0.05, 1
        
        MDTopAppBar:
            title: "Pasiflonet Feed"
            right_action_items: [["refresh", lambda x: app.connect_telegram()]]
        
        # אזור הגלילה (הפיד)
        ScrollView:
            MDBoxLayout:
                id: feed_container
                orientation: 'vertical'
                adaptive_height: True
                padding: dp(10)
                spacing: dp(15)
'''

# --- רכיב הודעה בודדת בפיד ---
class FeedItem(MDCard):
    image_source = StringProperty("loading.png") # תמונת ברירת מחדל
    message_text = StringProperty("")
    timestamp = StringProperty("")
    
    def __init__(self, message_obj, client, **kwargs):
        super().__init__(**kwargs)
        self.message_obj = message_obj
        self.client = client
        self.download_thumbnail()

    def download_thumbnail(self):
        # מוריד רק את ה-Thumbnail הקטן (מיידי)
        def _download():
            try:
                if self.message_obj.photo or self.message_obj.video:
                    path = f"thumb_{self.message_obj.id}.jpg"
                    # טריק של טלגרם: הורדת thumbnail בלבד
                    self.client.loop.run_until_complete(
                        self.message_obj.download_media(file=path, thumb=1)
                    )
                    # עדכון ה-UI חייב להיות בחוט הראשי
                    Clock.schedule_once(lambda x: self.update_image(path))
            except Exception as e:
                print(f"Thumb error: {e}")

        threading.Thread(target=_download).start()

    def update_image(self, path):
        self.image_source = path

    def send_to_background(self):
        self.ids.status_label.text = "Processing in Background..."
        self.ids.status_label.text_color = (1, 1, 0, 1) # Yellow
        # שולח למנוע העיבוד
        app = MDApp.get_running_app()
        app.background_worker.add_task(self.message_obj, self)

    def mark_complete(self):
        self.ids.status_label.text = "SENT! ✅"
        self.ids.status_label.text_color = (0, 1, 0, 1) # Green

# --- מנוע עיבוד ברקע ---
class BackgroundWorker:
    def __init__(self, client):
        self.client = client
        self.queue = []
        self.is_running = False

    def add_task(self, message, ui_item):
        self.queue.append({'msg': message, 'ui': ui_item})
        if not self.is_running:
            threading.Thread(target=self.process_queue).start()

    def process_queue(self):
        self.is_running = True
        while self.queue:
            task = self.queue.pop(0)
            message = task['msg']
            ui_item = task['ui']
            
            try:
                # 1. הורדת הקובץ המלא (לוקח זמן)
                full_path = f"full_{message.id}.mp4" # פשטות לדוגמה
                # כאן אמורה להיות ההורדה האמיתית (סימולציה למניעת קריסת רשת כרגע)
                # self.client.download_media(message, full_path)
                time.sleep(2) # סימולציה של הורדה ועיבוד FFmpeg
                
                # 2. עיבוד FFmpeg (כאן יכנס הקוד מהשלב הקודם)
                # run_ffmpeg(full_path...)
                
                # 3. שליחה לערוץ היעד
                # self.client.send_file(...)

                # עדכון UI שהסתיים
                Clock.schedule_once(lambda x: ui_item.mark_complete())
                
            except Exception as e:
                print(f"Background Error: {e}")
        
        self.is_running = False

# --- האפליקציה הראשית ---
class PasiflonetApp(MDApp):
    client = None
    background_worker = None
    
    # פרטי התחברות (תכניס את שלך כאן)
    API_ID = 26569766
    API_HASH = 'YOUR_HASH_HERE'

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Cyan"
        return Builder.load_string(KV)

    def on_start(self):
        self.request_permissions()
        # יצירת קובץ תמונה זמני למקרה שאין
        with open("loading.png", "wb") as f:
            f.write(b"") 

    def request_permissions(self):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE, 
                Permission.WRITE_EXTERNAL_STORAGE, 
                Permission.INTERNET
            ])

    def connect_telegram(self):
        threading.Thread(target=self._start_client).start()

    def _start_client(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        self.client = TelegramClient('pasiflon_session', self.API_ID, self.API_HASH)
        self.client.start() # יבקש טלפון בטרמינל בפעם הראשונה, או קובץ session
        self.background_worker = BackgroundWorker(self.client)

        # האזנה להודעות חדשות
        @self.client.on(events.NewMessage)
        async def handler(event):
            # הוספת הודעה לפיד
            Clock.schedule_once(lambda x: self.add_feed_item(event))

        loop.run_until_complete(self.client.run_until_disconnected())

    def add_feed_item(self, event):
        container = self.root.get_screen('main').ids.feed_container
        
        # יצירת אייטם חדש
        text_preview = event.text[:100] + "..." if event.text else "Media File"
        timestamp = event.date.strftime("%H:%M")
        
        item = FeedItem(
            message_obj=event,
            client=self.client,
            message_text=hebrew(text_preview),
            timestamp=timestamp
        )
        container.add_widget(item, index=0) # מוסיף למעלה (הכי חדש)

if __name__ == '__main__':
    PasiflonetApp().run()
