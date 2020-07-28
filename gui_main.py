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
from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button


from gui.VariablePage import VariablePage
from util.parsers.GraphLoader import parse_graph_file_data, ConditionalProbabilityTable

kivy.require('1.11.1')

Config.set('graphics', 'resizable', True)

DEFAULT_ACTIVE_BUTTON_COLOR = (0.38, 0.71, 0.86, 1)
DEFAULT_INACTIVE_BUTTON_COLOR = (1, 1, 1, 1)

Config.set('graphics', 'width', '1200')
Config.set('graphics', 'height', '800')
Config.set('graphics', 'minimum_width', '800')
Config.set('graphics', 'minimum_height', '600')

class ProbabilityPage(BoxLayout):

    def __init__(self, graph_data, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Label(text="Probability"))
        # graph_data = kwargs["graph_data"]

    def lose_focus(self):
        pass


class DoCalculusPage(BoxLayout):

    def __init__(self, graph_data, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Label(text="Do-Calculus"))
        # graph_data = kwargs["graph_data"]

    def lose_focus(self):
        pass


class MainWindow(GridLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cols = 2
        self.side_menu = ScrollView(width=100, size_hint=(None, 1), do_scroll_x=False)

        self.active_button = None

        file_menu = GridLayout(cols=1, size_hint=(0.5, 1.0), pos_hint={"center_x": 0.5, "center_y": 0.5})
        file_menu.add_widget(Label(text="Select a Graph File", padding=(0, 0), size_hint_y=None))
        file_menu.orientation = "vertical"

        def load_file(instance: Button):

            self.clear_widgets()

            graph_data = parse_graph_file_data("graphs/full/" + instance.text)

            button_properties = {
                "size": (75, 50),
                "size_hint_y": None,
                "background_color": DEFAULT_INACTIVE_BUTTON_COLOR,
                # "background_normal": ""
            }

            buttons = GridLayout(cols=1, spacing=5, padding=10)

            variable_button = Button(text="Variables", **button_properties)
            variable_button.bind(on_press=partial(
                self.set_active_content,
                variable_button,
                VariablePage(graph_data=graph_data)))

            buttons.add_widget(variable_button)

            probability_button = Button(text="Probabilities", **button_properties)
            probability_button.bind(on_press=partial(
                self.set_active_content,
                probability_button,
                ProbabilityPage(graph_data=graph_data)))
            buttons.add_widget(probability_button)

            do_calculus_button = Button(text="Do-Calculus", **button_properties)
            do_calculus_button.bind(on_press=partial(
                self.set_active_content,
                do_calculus_button,
                DoCalculusPage(graph_data=graph_data)))
            buttons.add_widget(do_calculus_button)

            self.side_menu.add_widget(buttons)
            self.add_widget(self.side_menu)

            main_scroll = ScrollView()
            self.active_area = BoxLayout()
            main_scroll.add_widget(self.active_area)
            self.add_widget(main_scroll)

        layout = GridLayout(cols=1, spacing=5, padding=20)
        scroll = ScrollView(size_hint=(0.5, 1.0), pos_hint={"x": 0.25, "y": 0.10})
        files = sorted(os.listdir("graphs/full"))
        for file in files:
            button = Button(text=file, size_hint_max_y="30")
            button.bind(on_press=load_file)
            layout.add_widget(button)
        scroll.add_widget(layout)
        file_menu.add_widget(scroll)
        self.add_widget(file_menu)

    def set_active_content(self, button, page, *args):

        if self.active_button == button:
            return

        for i in self.active_area.children:
            i.lose_focus()

        if self.active_button is not None:
            self.active_button.background_color = DEFAULT_INACTIVE_BUTTON_COLOR

        button.background_color = DEFAULT_ACTIVE_BUTTON_COLOR
        self.active_button = button

        self.active_area.clear_widgets()
        self.active_area.add_widget(page)


class ProbabilityApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rect = None

    def build(self):
        self.root = root = MainWindow()
        root.bind(size=self._update_rect, pos=self._update_rect)

        with root.canvas.before:
            Color(0.1, 0.1, 0.1, 1)
            self.rect = Rectangle(size=root.size, pos=root.pos)
        return root

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


if __name__ == "__main__":
    ProbabilityApp().run()
