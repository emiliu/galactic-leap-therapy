from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
from kivy.uix.togglebutton import ToggleButton
from opposition import MainWidget as OppWidget
#import sys
#sys.path.append('..')
#from unit3.class3.pset3 import MainWidget3 as OppWidget
#from pset7 import MainWidget as OppWidget
#from common.core import g_terminate_funcs


class MenuScreen(Screen):
    def __init__(self):
        super(MenuScreen, self).__init__()
        main_layout = BoxLayout(orientation='vertical')

        toggle_layout = BoxLayout(orientation='horizontal')
        self.opp_btn = ToggleButton(text='opp', group='game_choice', state='down')
        self.flex_btn = ToggleButton(text='flex', group='game_choice')

        start_btn = Button(text='start')
        #start_btn = Button(text='Hello', size_hint=(None, None), pos_hint={'right':0.5, 'top':1})
        start_btn.bind(on_release=self.change_screen)

        toggle_layout.add_widget(self.opp_btn)
        toggle_layout.add_widget(self.flex_btn)
        main_layout.add_widget(toggle_layout)
        main_layout.add_widget(start_btn)

        self.add_widget(main_layout)

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

        self.exit_btn = Button(text='exit', size_hint=(0.1, 0.1), pos_hint={'left':0, 'bottom':0})
        self.exit_btn.bind(on_release=self.exit_game)
        self.add_widget(self.exit_btn, index=2)

    def init_game(self, game):
        assert(game == 'opp')
        self.game_widget = OppWidget()
        self.add_widget(self.game_widget)

    def exit_game(self, btn):
        Clock.unschedule(self.game_widget._update)
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
    MainApp().run()