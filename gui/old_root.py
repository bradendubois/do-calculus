import kivy

from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem, TabbedPanelHeader
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from functools import partial
import os
from kivy.config import Config
from kivy.clock import Clock
from kivy.core.window import Window
kivy.require('1.11.1')

Config.set('graphics', 'resizable', True)

Window.clearcolor = (1, 1, 1, 1)


class MainWindowHeader(TabbedPanelHeader):

    def __init__(self, **kwargs):
        super(MainWindowHeader, self).__init__(**kwargs)
        self.content = None
        self.size_hint_x = None
        self.width = 75

    def on_press(self):
        if self.content is None:
            window = Window()
            window.tab = self
            self.content = window
        self.text = "Opened"


class Window(FloatLayout):

    def __init__(self, **kwargs):
        super(Window, self).__init__(**kwargs)

        self.background_color = (1, 1, 1, 1)

        menu = GridLayout(cols=1, size_hint=(0.5, 1.0), pos_hint={"center_x": 0.5, "center_y": 0.5})
        menu.add_widget(Label(text="Select a Graph File", padding=(0, 0), size_hint_y=None))
        menu.orientation = "vertical"

        def load_file(instance: Button):
            self.file = instance.text
            self.remove_widget(menu)
            self.tab.text = instance.text

            main = BoxLayout(orientation="horizontal",
                             size_hint=(1.0, 1.0),
                             pos_hint={"center_x": 0.5, "center_y": 0.5},
                             )

            main.add_widget(Label(text="Working: {}".format(instance.text)))
            # self.add_widget(main)

        layout = GridLayout(cols=1, spacing=5)

        scroll = ScrollView(size_hint=(0.5, 1.0), pos_hint={"x": 0.25, "y": 0.10})
        files = sorted(os.listdir("graphs/full"))
        for file in files:
            button = Button(text=file, size_hint_max_y="30")
            button.bind(on_press=load_file)
            layout.add_widget(button)
        scroll.add_widget(layout)
        menu.add_widget(scroll)

        self.add_widget(menu)


class MainWindow(TabbedPanel):

    def __init__(self, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        self.do_default_tab = False
        self.sessions = 0
        self.add_tabbed_panel_header(None)
        self.background_color = (1, 1, 1, 1)  # 50% translucent red
        # self.border = [0, 0, 0, 0]
        # background_image = 'path/to/background/image'

    def add_tabbed_panel_header(self, button):

        if button is None or button.content is None:
            self.sessions += 1
            header = MainWindowHeader()
            header.text = "+"
            header.bind(on_press=self.add_tabbed_panel_header)
            self.add_widget(header)


class ProbabilityApp(App):

    def build(self):

        return MainWindow()


if __name__ == "__main__":
    ProbabilityApp().run()
