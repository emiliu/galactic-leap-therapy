from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition

import sys
import numpy as np

from flexion import MainWidget as FlexWidget
from opposition import MainWidget as OppWidget
from graphics import ProgressRect

from info import DashScreen, HelpScreen

# from common.core import g_terminate_funcs
from common.gfxutil import CLabelRect


class MenuScreen(Screen):
    def __init__(self, switch_screen_callback):
        super(MenuScreen, self).__init__()

        self.switch_screen = switch_screen_callback

        self.bg = Rectangle(source="images/splash.png", size=Window.size)
        self.window_size = Window.size
        self.canvas.add(self.bg)

        self.score = CLabelRect(pos=(self.window_size[0] / 4, self.window_size[1]))

        self.opposition = 0
        self.flexion = 0

        # label_layout = AnchorLayout(size_hint=(1,1))
        text = "Progress Today \n"
        text += "Opposition: %d/50 \n" % self.opposition
        text += "Flexion: %d/50 \n" % self.flexion
        self.score.set_text(text)
        # self.score.label.text += "[color=ffffff] Flexion Complete: %d\n [/color]" % self.flexion
        # self.canvas.add(self.score)

        self.opp_progress = ProgressRect((0, 0), (0, 0), Color(0.6, 0.1, 0.4))
        self.opp_progress.set_total(50)
        self.opp_label = CLabelRect(pos=(0, 0), text="Opposition")
        self.canvas.add(self.opp_progress)
        self.canvas.add(self.opp_label)

        self.flex_progress = ProgressRect((0, 0), (0, 0), Color(0.1, 0.4, 0.6))
        self.flex_progress.set_total(50)
        self.flex_label = CLabelRect(pos=(0, 0), text="Flexion")
        self.canvas.add(self.flex_progress)
        self.canvas.add(self.flex_label)

        aspect = Window.width / Window.height
        self.opp_btn = Button(background_normal="images/buttons/opposition.png",
                              background_down="images/buttons/opposition_pressed.png",
                              size_hint=(0.294 / aspect, 0.1),
                              pos_hint={"center_x": 0.35, "center_y": 0.2})
        self.flex_btn = Button(background_normal="images/buttons/flexion.png",
                               background_down="images/buttons/flexion_pressed.png",
                               size_hint=(0.24 / aspect, 0.1),
                               pos_hint={"center_x": 0.65, "center_y": 0.2})
        self.dash_btn = Button(background_normal="images/buttons/dash.png",
                               background_down="images/buttons/dash_pressed.png",
                               size_hint=(0.414 / aspect, 0.1),
                               pos_hint={"center_x": 0.5, "center_y": 0.93})

        self.opp_btn.bind(on_release=lambda btn: self.switch_screen("help", "opp"))
        self.flex_btn.bind(on_release=lambda btn: self.switch_screen("help", "flex"))
        self.dash_btn.bind(on_release=lambda btn: self.switch_screen("dash"))

        self.add_widget(self.opp_btn)
        self.add_widget(self.flex_btn)
        self.add_widget(self.dash_btn)

        Clock.schedule_interval(self.scale_bg, 0)

    def update_score(self, game, score):
        if game == "opp":
            self.opposition += score
            self.opp_progress.on_update(score)
        if game == "flex":
            self.flexion += score
            self.flex_progress.on_update(score)

        text = "Progress Today \n"
        text += "Opposition: %d /50 \n" % self.opposition
        text += "Flexion: %d /50 \n" % self.flexion
        self.score.set_text(text)

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
            self.dash_btn.size_hint = (0.414 / aspect, 0.1)

            self.opp_progress.set_size(
                (0 * Window.width, 0.93 * Window.height),
                (0.25 * Window.width, 0.98 * Window.height),
            )
            self.opp_label.set_pos((0.3 * Window.width, 0.955 * Window.height))
            self.flex_progress.set_size(
                (1 * Window.width, 0.93 * Window.height),
                (0.75 * Window.width, 0.98 * Window.height),
            )
            self.flex_label.set_pos((0.71 * Window.width, 0.955 * Window.height))


class GameScreen(Screen):
    def __init__(self, switch_screen_callback):
        super(GameScreen, self).__init__()

        self.switch_screen = switch_screen_callback
        self.game_widget = None
        self.type = None

        aspect = Window.width / Window.height

        self.exit_btn = Button(background_normal="images/buttons/exit.png",
                               background_down="images/buttons/exit_pressed.png",
                               size_hint=(0.169 / aspect, 0.1),
                               pos_hint={"x": 0.05, "y": 0.05})
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

        self.switch_screen("menu")
        self.remove_widget(self.game_widget)
        self.game_widget = None


class MainApp(App):
    def __init__(self):
        super().__init__()

        self.sm = ScreenManager(transition=FadeTransition())
        self.menu_screen = MenuScreen(self.switch_screen)
        self.game_screen = GameScreen(self.switch_screen)
        self.help_screen = HelpScreen(self.switch_screen)
        self.dash_screen = DashScreen(self.switch_screen)

    def build(self):
        self.sm.add_widget(self.menu_screen)
        return self.sm

    def switch_screen(self, switch_to, game_type=None):
        if switch_to == "game":
            assert game_type is not None, "game_type cannot be None"
            self.game_screen.init_game(game_type)
            self.sm.switch_to(self.game_screen)

        elif switch_to == "menu":
            # gets the score from opp or flex
            if self.game_screen.game_widget:
                score = self.game_screen.game_widget.get_score()
                print("new score", score)
                self.menu_screen.update_score(self.game_screen.type, score)

            self.sm.switch_to(self.menu_screen)

        elif switch_to == "help":
            self.help_screen.set_game(game_type)
            self.sm.switch_to(self.help_screen)

        elif switch_to == "dash":
            self.dash_screen.update_size()
            self.sm.switch_to(self.dash_screen)


if __name__ == "__main__":
    # automatic fullscreen crashes the program for Emily (Linux)
    # but seems to work for everyone else
    # will maybe try to debug this later
    Window.fullscreen = "auto"
    if len(sys.argv) > 1 and sys.argv[1] == "nofullscreen":
        Window.fullscreen = False

    # run the app
    MainApp().run()
