from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen

import numpy as np

class HelpScreen(Screen):
    def __init__(self, switch_screen_callback):
        super(HelpScreen, self).__init__()

        self.switch_screen = switch_screen_callback
        self.game_type = None

        self.bg = Rectangle(source="images/purplehole.jpg", size=Window.size)
        self.canvas.add(self.bg)

        aspect = Window.width / Window.height
        self.play_btn = Button(background_normal="images/buttons/play.png",
                               background_down="images/buttons/play_pressed.png",
                               size_hint=(0.184 / aspect, 0.1),
                               pos_hint={"center_x": 0.5, "center_y": 0.15})
        self.back_btn = Button(background_normal="images/buttons/back.png",
                               background_down="images/buttons/back_pressed.png",
                               size_hint=(0.208 / aspect, 0.1),
                               pos_hint={"x": 0.05, "y": 0.05})
        self.back_btn.bind(on_release=lambda btn: self.switch_screen("menu"))
        self.add_widget(self.back_btn)

        self.title = Label(pos_hint={"center_x" : 0.5, "center_y" : 0.9})
        self.text = Label(pos_hint={"center_x" : 0.5, "center_y" : 0.5})
        self.add_widget(self.title)
        self.add_widget(self.text)

        self.texts = {
            "main" : """
This application is a series of games to make
hand rehabilitation exercises more effective,
fun, and musical!

These games help with both finger opposition
and wrist flexion exercises.

Enter your goals and track your progress
using the dashboard!
""",
            "opp" : """
Each finger corresponds to a rocket ship.

Your palm should be facing down toward the sensor.

Touch your thumb to the correct finger when
an asteroid reaches the rocket!

This exercise helps you practice finger opposition.
""",
            "flex" : """
Make your hand flat and turn your hand left and
right to control the spaceship and keep it on the path.

This exercise helps you practice wrist flexion.
"""
        }

        self.titles = {
            "main" : "About",
            "opp" : "Opposition",
            "flex" : "Flexion"
        }

        self.play_fn = None

    def set_game(self, game_type):
        if game_type is None:
            if self.play_btn in self.children:
                self.remove_widget(self.play_btn)
            self.title.text = self.titles["main"]
            self.text.text = self.texts["main"]

        else:
            if self.play_btn not in self.children:
                self.add_widget(self.play_btn)
            self.play_btn.unbind(on_release=self.play_fn)
            self.play_fn = lambda btn: self.switch_screen("game", game_type)
            self.play_btn.bind(on_release=self.play_fn)
            self.title.text = self.titles[game_type]
            self.text.text = self.texts[game_type]

        aspect = Window.width / Window.height
        self.play_btn.size_hint = (0.184 / aspect, 0.1)
        self.back_btn.size_hint = (0.208 / aspect, 0.1)

        self.title.font_size = Window.height / 10
        self.text.font_size = Window.height / 20

        self.bg.size = Window.size

class DashScreen(Screen):
    def __init__(self, switch_screen_callback):
        super(DashScreen, self).__init__()

        self.switch_screen = switch_screen_callback

        self.rect = Rectangle(pos=(0, 0), size=Window.size)
        self.bg = Rectangle(source="images/dashboard.png", size=Window.size)
        self.canvas.add(Color(1, 1, 1, 1))
        self.canvas.add(self.rect)
        self.canvas.add(self.bg)

        aspect = Window.width / Window.height
        self.back_btn = Button(background_normal="images/buttons/back.png",
                               background_down="images/buttons/back_pressed.png",
                               size_hint=(0.208 / aspect * 0.75, 0.1 * 0.75),
                               pos_hint={"x": 0.03, "y": 0.05})
        self.about_btn = Button(background_normal="images/buttons/about.png",
                                background_down="images/buttons/about_pressed.png",
                                size_hint=(0.255 / aspect * 0.75, 0.1 * 0.75),
                                pos_hint={"right": 0.97, "y": 0.05})
        self.back_btn.bind(on_release=lambda btn: self.switch_screen("menu"))
        self.about_btn.bind(on_release=lambda btn: self.switch_screen("help"))
        self.add_widget(self.back_btn)
        self.add_widget(self.about_btn)

    def update_size(self):
        aspect = Window.width / Window.height
        self.back_btn.size_hint = (0.208 / aspect * 0.75, 0.1 * 0.75)
        self.about_btn.size_hint = (0.255 / aspect * 0.75, 0.1 * 0.75)

        ASPECT = 1902 / 1358
        width = min(Window.width, Window.height * ASPECT) * 0.9
        height = width / ASPECT * 0.9
        bg_size = np.array([width, height])
        bg_pos = (np.array([Window.width, Window.height]) - bg_size) / 2
        self.bg.pos = bg_pos
        self.bg.size = bg_size
        self.rect.size = Window.size