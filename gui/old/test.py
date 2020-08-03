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

from kivy.config import Config
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.app import App
from kivy.graphics import Color, Rectangle
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button

kivy.require('1.11.1')


class ScrollWindow(ScrollView):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.size_hint = (1, None)
        self.size = (Window.width, Window.height)

        layout = GridLayout(cols=1, spacing=10, size_hint_y=None)
        # Make sure the height is such that there is something to scroll.
        layout.bind(minimum_height=layout.setter('height'))
        for i in range(100):
            btn = Button(text=str(i), size_hint_y=None, height=40)
            layout.add_widget(btn)

        self.add_widget(layout)


class MainWindow(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_widget(ScrollWindow())
        self.add_widget(ScrollWindow())



class TestApp(App):

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
    TestApp().run()
