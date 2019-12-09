from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Rectangle
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition

import sys
import numpy as np

from flexion import MainWidget as FlexWidget
from opposition import MainWidget as OppWidget

# from common.core import g_terminate_funcs
from common.gfxutil import CLabelRect


class MenuScreen(Screen):
    def __init__(self, switch_screen_callback):
        super(MenuScreen, self).__init__()

        self.switch_screen = switch_screen_callback

        self.bg = Rectangle(source="images/splash.png", size=Window.size)
        self.window_size = (0, 0)
        self.canvas.add(self.bg)

        self.score = CLabelRect(pos=(self.window_size[0] / 4, self.window_size[1]))

        self.opposition = 0
        self.flexion = 0

        # label_layout = AnchorLayout(size_hint=(1,1))
        text = "Opposition: %d\n" % self.opposition
        text += "Flexion Complete: %d\n" % self.flexion
        self.score.set_text(text)
        # self.score.label.text += "[color=ffffff] Flexion Complete: %d\n [/color]" % self.flexion

        self.canvas.add(self.score)

        aspect = Window.width / Window.height
        self.opp_btn = Button(text="",
                              background_normal="images/buttons/opposition.png",
                              background_down="images/buttons/opposition_pressed.png",
                              size_hint=(0.294 / aspect, 0.1),
                              pos_hint={"center_x": 0.35, "center_y": 0.2})
        self.flex_btn = Button(text="",
                               background_normal="images/buttons/flexion.png",
                               background_down="images/buttons/flexion_pressed.png",
                               size_hint=(0.24 / aspect, 0.1),
                               pos_hint={"center_x": 0.65, "center_y": 0.2})

        self.opp_btn.bind(on_release=lambda btn: self.switch_screen("game", "opp"))
        self.flex_btn.bind(on_release=lambda btn: self.switch_screen("game", "flex"))

        self.add_widget(self.opp_btn)
        self.add_widget(self.flex_btn)

        Clock.schedule_interval(self.scale_bg, 0)

    def scale_bg(self, *args):
        # resize background
        if Window.size != self.window_size:
            self.window_size = Window.size
            ASPECT = 16 / 9
            width = min(Window.width, Window.height * ASPECT)
            height = width / ASPECT
            bg_size = np.array([width, height])
            bg_pos = (np.array([Window.width, Window.height]) - bg_size) / 2
            self.bg.pos = bg_pos
            self.bg.size = bg_size

            aspect = Window.width / Window.height
            self.opp_btn.size_hint = (0.294 / aspect, 0.1)
            self.flex_btn.size_hint = (0.24 / aspect, 0.1)


class GameScreen(Screen):
    def __init__(self, switch_screen_callback):
        super(GameScreen, self).__init__()

        self.opposition = 0

        self.switch_screen = switch_screen_callback
        self.game_widget = None
        self.type = None

        aspect = Window.width / Window.height

        self.exit_btn = Button(text="", pos=(10, 10),
                               background_normal="images/buttons/exit.png",
                               background_down="images/buttons/exit_pressed.png",
                               size_hint=(0.169 / aspect, 0.1))
        self.exit_btn.bind(on_release=self.exit_game)
        self.add_widget(self.exit_btn, index=0)

    def init_game(self, game):
        if game == "opp":
            self.game_widget = OppWidget()
        elif game == "flex":
            self.game_widget = FlexWidget()
        else:
            raise Exception("No such game")
        aspect = Window.width / Window.height
        self.exit_btn.size_hint = (0.169 / aspect, 0.1)
        self.add_widget(self.game_widget, index=2)
        self.type = game

    def exit_game(self, btn):
        # not the recommended way of unscheduling
        # but we don't have a reference to the scheduled object
        Clock.unschedule(self.game_widget._update)

        # termination functions used by BaseWidget
        # the only notable thing seems to be closing the audio stream
        # keeping this here in case we decide that's necessary
        # for t in g_terminate_funcs:
        # t()

        if self.type == "opp":
            self.opposition += self.game_widget.opp
            print("new score", self.opposition)

        self.remove_widget(self.game_widget)
        self.switch_screen("menu")


class MainApp(App):
    def __init__(self):
        super().__init__()

        self.sm = ScreenManager(transition=FadeTransition())
        self.menu_screen = MenuScreen(self.switch_screen)
        self.game_screen = GameScreen(self.switch_screen)

    def build(self):
        self.sm.add_widget(self.menu_screen)
        return self.sm

    def switch_screen(self, switch_to, game_type=None):
        if switch_to == "game":
            assert game_type is not None, "game_type cannot be None"
            self.game_screen.init_game(game_type)
            self.sm.switch_to(self.game_screen)

        if switch_to == "menu":
            self.sm.switch_to(self.menu_screen)


if __name__ == "__main__":
    # automatic fullscreen crashes the program for Emily (Linux)
    # but seems to work for everyone else
    # will maybe try to debug this later
    Window.fullscreen = "auto"
    if len(sys.argv) > 1 and sys.argv[1] == "nofullscreen":
        Window.fullscreen = False

    # run the app
    MainApp().run()
