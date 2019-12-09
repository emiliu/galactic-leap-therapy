from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen

class HelpScreen(Screen):
    def __init__(self, switch_screen_callback):
        super(HelpScreen, self).__init__()

        self.switch_screen = switch_screen_callback
        self.game_type = None

        aspect = 1
        self.play_btn = Button(text="",
                               background_normal="images/buttons/play.png",
                               background_down="images/buttons/play_pressed.png",
                               size_hint=(0.24 / aspect, 0.1),
                               pos_hint={"center_x": 0.65, "center_y": 0.2})
        self.back_btn = Button(text="",
                               background_normal="images/buttons/back.png",
                               background_down="images/buttons/back_pressed.png",
                               size_hint=(0.24 / aspect, 0.1),
                               pos=(10, 10))
        self.back_btn.bind(on_release=lambda btn: self.switch_screen("menu"))
        self.add_widget(self.back_btn)
        self.text = None
        self.texts = {}
        self.play_fn = None

    def set_game(self, game_type):
        if game_type is None:
            if self.play_btn in self.children:
                self.remove_widget(self.play_btn)

        else:
            if self.play_btn not in self.children:
                self.add_widget(self.play_btn)
            self.play_btn.unbind(on_release=self.play_fn)
            self.play_fn = lambda btn: self.switch_screen("game", game_type)
            self.play_btn.bind(on_release=self.play_fn)

class InfoScreen(Screen):
    def __init__(self, switch_screen_callback):
        pass