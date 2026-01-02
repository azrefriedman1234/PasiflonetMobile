from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton

KV = '''
ScreenManager:
    MainScreen:

<MainScreen>:
    name: 'main'
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 0.1, 0.1, 0.1, 1
        padding: 20
        spacing: 20
        
        MDLabel:
            text: "Pasiflonet Diagnostics"
            halign: "center"
            theme_text_color: "Custom"
            text_color: 0, 1, 1, 1
            font_style: "H4"
            
        MDLabel:
            text: "If you see this, the App Core is WORKING!"
            halign: "center"
            theme_text_color: "Custom"
            text_color: 0, 1, 0, 1
            
        MDRaisedButton:
            text: "Click Me"
            pos_hint: {"center_x": 0.5}
            on_release: app.check_system()
'''

class PasiflonetApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Cyan"
        return Builder.load_string(KV)

    def check_system(self):
        # בדיקה פשוטה שהלוגיקה עובדת
        import platform
        sys_info = f"System: {platform.system()} {platform.release()}"
        print(sys_info)
        # שינוי טקסט הכותרת כדי להוכיח שהאפליקציה חיה
        self.root.get_screen('main').children[0].children[2].text = "SYSTEM OK ✅"

if __name__ == '__main__':
    PasiflonetApp().run()
