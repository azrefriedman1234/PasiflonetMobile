import os
import shutil
import threading
import asyncio
import json
from datetime import datetime

from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.filemanager import MDFileManager
from kivymd.toast import toast
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.utils import platform

from telethon import TelegramClient, events
import arabic_reshaper
from bidi.algorithm import get_display

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
                shorten: True
                shorten_from: 'right'

    MDBoxLayout:
        size_hint_y: 0.3
        spacing: dp(10)
        MDRaisedButton:
            text: "Send"
            md_bg_color: 0, 0.7, 0, 1
            on_release: root.send_background()
        MDLabel:
            id: status
            text: ""
            theme_text_color: "Hint"
            halign: "center"

ScreenManager:
    SettingsScreen:
    LoginScreen:
    MainScreen:

<SettingsScreen>:
    name: 'settings'
    MDBoxLayout:
        orientation: 'horizontal'
        md_bg_color: 0.05, 0.05, 0.05, 1
        
        MDBoxLayout:
            orientation: 'vertical'
            padding: dp(20)
            spacing: dp(15)
            size_hint_x: 0.6
            
            MDLabel:
                text: "SYSTEM CONFIG"
                font_style: "H5"
                theme_text_color: "Custom"
                text_color: 0, 1, 1, 1
                size_hint_y: None
                height: dp(40)

            MDTextField:
                id: api_id
                hint_text: "API ID"
                mode: "rectangle"
                input_filter: "int"
                
            MDTextField:
                id: api_hash
                hint_text: "API Hash"
                mode: "rectangle"

            MDTextField:
                id: channel
                hint_text: "Target Channel (@name)"
                mode: "rectangle"

            MDRaisedButton:
                text: "Select Watermark"
                on_release: app.file_manager_open()
                md_bg_color: 0.3, 0.3, 0.3, 1
                size_hint_x: 1
            
            MDRaisedButton:
                text: "SAVE SETTINGS"
                md_bg_color: 0, 0.8, 0.8, 1
                size_hint_x: 1
                on_release: app.save_settings()

        MDBoxLayout:
            orientation: 'vertical'
            size_hint_x: 0.4
            padding: dp(20)
            MDLabel:
                text: "Preview"
                halign: "center"
            AsyncImage:
                id: preview_img
                source: "loading.png"
                allow_stretch: True
                keep_ratio: True

<LoginScreen>:
    name: 'login'
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 0.1, 0.1, 0.1, 1
        padding: dp(50)
        spacing: dp(20)
        MDLabel:
            text: "TELEGRAM LOGIN"
            halign: "center"
            font_style: "H4"
            theme_text_color: "Custom"
            text_color: 0, 1, 1, 1
        MDTextField:
            id: phone_input
            hint_text: "Phone (+972...)"
            mode: "rectangle"
        MDRaisedButton:
            text: "Get Code"
            pos_hint: {"center_x": 0.5}
            on_release: app.start_login()
        MDTextField:
            id: code_input
            hint_text: "Code"
            mode: "rectangle"
            disabled: True
        MDRaisedButton:
            id: verify_btn
            text: "Login"
            disabled: True
            pos_hint: {"center_x": 0.5}
            md_bg_color: 0, 1, 0, 1
            on_release: app.verify_code()

<MainScreen>:
    name: 'main'
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 0, 0, 0, 1
        MDTopAppBar:
            title: "Pasiflonet Feed"
            right_action_items: [["cog", lambda x: app.open_settings()]]
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
        threading.Thread(target=self.load_thumbnail).start()

    def load_thumbnail(self):
        try:
            if self.message.photo or self.message.video:
                path = self.client.loop.run_until_complete(
                    self.message.download_media(file=f"thumb_{self.msg_id}", thumb=1)
                )
                if path: Clock.schedule_once(lambda x: setattr(self, 'image_path', path))
        except: pass

    def send_background(self):
        self.ids.status.text = "Sending..."

class PasiflonetApp(MDApp):
    client = None
    phone_hash = None
    config_data = {}
    manager_open = False
    
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Cyan"
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
            preview=True,
        )
        return Builder.load_string(KV)

    def on_start(self):
        # יצירת קובץ דמי למניעת קריסות תמונה
        if not os.path.exists("loading.png"):
            with open("loading.png", "wb") as f: f.write(b"")
            
        self.request_perms()
        self.load_config()

    def request_perms(self):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            from android.runnable import run_on_ui_thread
            from jnius import autoclass
            
            # בדיקת גרסת אנדרואיד
            Build = autoclass("android.os.Build")
            VERSION = autoclass("android.os.Build$VERSION")
            
            perms = [Permission.INTERNET, Permission.ACCESS_NETWORK_STATE]
            
            if VERSION.SDK_INT >= 33:
                # אנדרואיד 13+ דורש הרשאות מדיה ספציפיות
                perms.extend([
                    Permission.READ_MEDIA_IMAGES,
                    Permission.READ_MEDIA_VIDEO,
                    Permission.READ_MEDIA_AUDIO
                ])
            else:
                # אנדרואיד ישן יותר
                perms.extend([
                    Permission.READ_EXTERNAL_STORAGE,
                    Permission.WRITE_EXTERNAL_STORAGE
                ])
                
            request_permissions(perms)

    def get_config_path(self):
        if platform == 'android':
            return os.path.join(self.user_data_dir, 'settings.json')
        return 'settings.json'

    def load_config(self):
        try:
            path = self.get_config_path()
            if os.path.exists(path):
                with open(path, 'r') as f:
                    self.config_data = json.load(f)
                if self.config_data.get('api_id'):
                    self.root.current = 'login'
                    return
        except Exception as e:
            toast(f"Config Error: {e}")
        self.root.current = 'settings'

    def save_settings(self):
        try:
            screen = self.root.get_screen('settings')
            self.config_data = {
                'api_id': int(screen.ids.api_id.text or 0),
                'api_hash': screen.ids.api_hash.text,
                'channel': screen.ids.channel.text
            }
            with open(self.get_config_path(), 'w') as f:
                json.dump(self.config_data, f)
            toast("Saved!")
            self.root.current = 'login'
        except Exception as e:
            toast(f"Save Failed: {e}")

    def file_manager_open(self):
        try:
            path = "/storage/emulated/0/" if platform == 'android' else "/"
            self.file_manager.show(path)
            self.manager_open = True
        except Exception as e:
            toast(f"Manager Error: {e}")

    def select_path(self, path):
        self.exit_manager()
        try:
            dest = os.path.join(self.user_data_dir if platform == 'android' else '.', 'watermark.png')
            shutil.copyfile(path, dest)
            self.root.get_screen('settings').ids.preview_img.source = dest
            toast("Watermark Loaded!")
        except Exception as e:
            toast(f"Copy Error: {e}")

    def exit_manager(self, *args):
        self.manager_open = False
        self.file_manager.close()

    def open_settings(self):
        self.root.current = 'settings'

    # --- Telegram Logic ---
    def start_login(self):
        api_id = self.config_data.get('api_id')
        api_hash = self.config_data.get('api_hash')
        phone = self.root.get_screen('login').ids.phone_input.text
        
        if not api_id: 
            toast("No Settings Found")
            return

        session = os.path.join(self.user_data_dir if platform == 'android' else '.', 'session')
        self.client = TelegramClient(session, api_id, api_hash)
        
        def _connect():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.client.loop = loop
            try:
                loop.run_until_complete(self.client.connect())
                if loop.run_until_complete(self.client.is_user_authorized()):
                    Clock.schedule_once(lambda x: self.switch_main())
                    loop.run_until_complete(self.listen())
                else:
                    res = loop.run_until_complete(self.client.send_code_request(phone))
                    self.phone_hash = res.phone_code_hash
                    Clock.schedule_once(lambda x: self.enable_verify())
            except Exception as e:
                toast(f"Conn Error: {e}")
        threading.Thread(target=_connect).start()

    def enable_verify(self):
        self.root.get_screen('login').ids.code_input.disabled = False
        self.root.get_screen('login').ids.verify_btn.disabled = False

    def verify_code(self):
        code = self.root.get_screen('login').ids.code_input.text
        phone = self.root.get_screen('login').ids.phone_input.text
        def _verify():
            try:
                self.client.loop.run_until_complete(
                    self.client.sign_in(phone, code, phone_code_hash=self.phone_hash)
                )
                Clock.schedule_once(lambda x: self.switch_main())
                self.client.loop.run_until_complete(self.listen())
            except Exception as e:
                toast(f"Login Error: {e}")
        threading.Thread(target=_verify).start()

    def switch_main(self):
        self.root.current = 'main'

    async def listen(self):
        @self.client.on(events.NewMessage)
        async def handler(event):
            Clock.schedule_once(lambda x: self.add_item(event))
        await self.client.run_until_disconnected()

    def add_item(self, event):
        text = get_display(arabic_reshaper.reshape(event.text or "Media"))
        time = event.date.strftime("%H:%M")
        item = FeedItem(event, self.client, text_content=text, time_str=time)
        self.root.get_screen('main').ids.feed_container.add_widget(item, index=0)

if __name__ == '__main__':
    PasiflonetApp().run()
