from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen

class HelpScreen(Screen):
    def __init__(self, switch_screen_callback):
        super(HelpScreen, self).__init__()

        self.switch_screen = switch_screen_callback
        self.game_type = None

        aspect = Window.width / Window.height
        self.play_btn = Button(background_normal="images/buttons/play.png",
                               background_down="images/buttons/play_pressed.png",
                               size_hint=(0.184 / aspect, 0.1),
                               pos_hint={"center_x": 0.5, "center_y": 0.2})
        self.back_btn = Button(background_normal="images/buttons/back.png",
                               background_down="images/buttons/back_pressed.png",
                               size_hint=(0.208 / aspect, 0.1),
                               pos_hint={"x": 0.05, "y": 0.05})
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

        aspect = Window.width / Window.height
        self.play_btn.size_hint = (0.184 / aspect, 0.1)
        self.back_btn.size_hint = (0.208 / aspect, 0.1)

class DashScreen(Screen):
    def __init__(self, switch_screen_callback):
        super(DashScreen, self).__init__()

        self.switch_screen = switch_screen_callback

        aspect = Window.width / Window.height
        self.back_btn = Button(background_normal="images/buttons/back.png",
                               background_down="images/buttons/back_pressed.png",
                               size_hint=(0.208 / aspect, 0.1),
                               pos_hint={"x": 0.05, "y": 0.05})
        self.about_btn = Button(background_normal="images/buttons/about.png",
                                background_down="images/buttons/about_pressed.png",
                                size_hint=(0.255 / aspect, 0.1),
                                pos_hint={"right": 0.95, "y": 0.05})
        self.back_btn.bind(on_release=lambda btn: self.switch_screen("menu"))
        self.about_btn.bind(on_release=lambda btn: self.switch_screen("help"))
        self.add_widget(self.back_btn)
        self.add_widget(self.about_btn)

    def update_size(self):
        aspect = Window.width / Window.height
        self.back_btn.size_hint = (0.208 / aspect, 0.1)
        self.about_btn.size_hint = (0.255 / aspect, 0.1)