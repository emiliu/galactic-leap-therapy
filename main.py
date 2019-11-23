from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
from kivy.uix.togglebutton import ToggleButton

from flexion import MainWidget as FlexWidget
from opposition import MainWidget as OppWidget

#from common.core import g_terminate_funcs


class MenuScreen(Screen):
    def __init__(self):
        super(MenuScreen, self).__init__()

        toggle_layout = BoxLayout(orientation='horizontal', size_hint=(0.5, 0.1), pos_hint={'center_x':0.5, 'center_y':0.7})
        self.opp_btn = ToggleButton(text='opp', group='game_choice', state='down')
        self.flex_btn = ToggleButton(text='flex', group='game_choice')

        start_btn = Button(text='start', size_hint=(0.2, 0.1), pos_hint={'center_x': 0.5, 'center_y': 0.4})
        start_btn.bind(on_release=self.change_screen)

        toggle_layout.add_widget(self.opp_btn)
        toggle_layout.add_widget(self.flex_btn)
        self.add_widget(toggle_layout)
        self.add_widget(start_btn)

    def change_screen(self, btn):
        if self.opp_btn.state == 'down':
            game = 'opp'
        else:
            game = 'flex'
        game_screen.init_game(game)
        sm.switch_to(game_screen)

class GameScreen(Screen):
    def __init__(self):
        super(GameScreen, self).__init__()

        self.game_widget = None

        self.exit_btn = Button(text='exit', size_hint=(0.1, 0.1), pos=(0, 0))
        self.exit_btn.bind(on_release=self.exit_game)
        self.add_widget(self.exit_btn, index=0)

    def init_game(self, game):
        if game == 'opp':
            self.game_widget = OppWidget()
        elif game == 'flex':
            self.game_widget = FlexWidget()
        else:
            raise Exception('No such game')
        self.add_widget(self.game_widget, index=2)

    def exit_game(self, btn):
        # not the recommended way of unscheduling
        # but we don't have a reference to the scheduled object
        Clock.unschedule(self.game_widget._update)

        # termination functions used by BaseWidget
        # the only notable thing seems to be closing the audio stream
        # keeping this here in case we decide that's necessary
        #for t in g_terminate_funcs:
            #t()

        self.remove_widget(self.game_widget)
        sm.switch_to(menu_screen)

sm = ScreenManager(transition=FadeTransition())
menu_screen = MenuScreen()
game_screen = GameScreen()

class MainApp(App):
    def build(self):
        sm.add_widget(MenuScreen())
        return sm

if __name__ == '__main__':
    # automatic fullscreen crashes the program for Emily (Linux)
    # but seems to work for everyone else
    # will maybe try to debug this later
    Window.fullscreen = 'auto'
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'nofullscreen':
        Window.fullscreen = False
    MainApp().run()