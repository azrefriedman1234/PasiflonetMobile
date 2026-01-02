import asyncio
import threading
from kivy.lang import Builder
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from kivymd.toast import toast
from kivy.metrics import dp
from telethon import TelegramClient, events
from deep_translator import GoogleTranslator
import arabic_reshaper
from bidi.algorithm import get_display

def hebrew(text):
    if not text: return ""
    try:
        return get_display(arabic_reshaper.reshape(text))
    except:
        return text

KV = '''
ScreenManager:
    LoginScreen:
    MainScreen:
    DetailScreen:

<LoginScreen>:
    name: 'login'
    MDBoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 20
        md_bg_color: 0.05, 0.05, 0.05, 1
        MDLabel:
            text: "PASIFLONET PY"
            halign: "center"
            theme_text_color: "Custom"
            text_color: 0, 1, 1, 1
            font_style: "H4"
        MDTextField:
            id: phone
            hint_text: "Phone Number"
            mode: "rectangle"
        MDRaisedButton:
            text: "LOGIN"
            pos_hint: {"center_x": 0.5}
            on_release: app.send_code()

<MainScreen>:
    name: 'main'
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 0, 0, 0, 1
        MDTopAppBar:
            title: "Feed"
        MDBoxLayout:
            id: table_box

<DetailScreen>:
    name: 'detail'
    MDLabel:
        text: "Details"
        halign: "center"
'''

class PasiflonetApp(MDApp):
    API_ID = 26569766
    API_HASH = 'YOUR_HASH_HERE' # תזכור לשים את ההאש שלך
    client = None

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Cyan"
        return Builder.load_string(KV)
    
    def send_code(self):
        toast("Connecting...")
        # LITE VERSION LOGIC HERE
        self.root.current = 'main'

if __name__ == '__main__':
    PasiflonetApp().run()
