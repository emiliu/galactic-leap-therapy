from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.uix.screenmanager import Screen, ScreenManager, FallOutTransition
from main import MainWidget

Builder.load_string("""
<MenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            orientation: 'horizontal'
            ToggleButton:
                text: 'opp'
                group: 'game'
                state: 'down'
            ToggleButton:
                text: 'flex'
                group: 'game'
                state: 'down'
        Button:
            text: 'start'
            on_press: root.manager.current = 'game'

<SettingsScreen>:
    BoxLayout:
        Button:
            text: 'My settings button'
        Button:
            text: 'Back to menu'
            on_press: root.manager.current = 'menu'

<CustomDropDown>:
    Button:
        id: btn
        text: 'Press'
        on_release: dropdown.open(self)
        size_hint_y: None
        height: '48dp'

    DropDown:
        id: dropdown
        on_parent: dropdown.dismiss()
        on_select: btn.text = '{}'.format(args[1])

        Button:
            text: 'Opposition'
            size_hint_y: None
            height: 44
            on_release: dropdown.select('item1')
        Button:
            text: 'Flexion'
            size_hint_y: None
            height: 44
            on_release: root.select('item2')

<GamePicker>:
    ToggleButton:
        text: 'opp'
        group: 'game'
    ToggleButton:
        text: 'flex'
        group: 'game'
""")

class CustomDropDown(BoxLayout):
    pass

class GamePicker(BoxLayout):
    pass

class MenuScreen(Screen):
    pass

#class SettingsScreen(Screen):
    #pass

class GameScreen(Screen):
    pass

class Menu(Screen):
    def __init__(self):
        super(Menu, self).__init__()
        self.start_button = Button(text='start')
        '''
        dropdown = CustomDropDown()
        mainbutton = Button(text='Hello', size_hint=(None, None), pos_hint={'right':0.5, 'top':1})
        mainbutton.bind(on_release=dropdown.open)
        dropdown.bind(on_select=lambda instance, x: setattr(mainbutton, 'text', x))
        layout = BoxLayout(orientation='vertical')#, padding=[20, 20, 20, 20])
        layout.add_widget(mainbutton)
        #layout.add_widget(dropdown)
        self.add_widget(layout)
        '''
        dropdown = GamePicker()
        self.add_widget(dropdown)
        '''
        for opt in ('opposition', 'flexion'):
            btn = Button(text=opt, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.options.select(btn.text))
            self.options.add_widget(btn)
        self.add_widget(self.options)
        '''
        #self.add_widget(self.start_button)

#sm.add_widget(SettingsScreen(name='settings'))

class TestApp(App):
    def build(self):
        #screen = Screen(name="game")
        #screen.add_widget(MainWidget())
        #sm.add_widget(screen)
        sm = ScreenManager(transition=FallOutTransition())
        sm.add_widget(MenuScreen())
        return sm

if __name__ == '__main__':
    TestApp().run()