from kivy.app import App
from kivy.uix.button import Button

class AtomicApp(App):
    def build(self):
        # כפתור ענק פשוט
        return Button(
            text='HELLO AZRE!\nIf you see this - WE WON.\n(Architecture Fixed)',
            font_size='30sp',
            background_color=(0, 1, 1, 1) # צבע טורקיז
        )

if __name__ == '__main__':
    AtomicApp().run()
