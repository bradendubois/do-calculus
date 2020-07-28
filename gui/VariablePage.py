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
from util.parsers.GraphLoader import parse_graph_file_data, ConditionalProbabilityTable

kivy.require('1.11.1')

Config.set('graphics', 'resizable', True)

DEFAULT_ACTIVE_BUTTON_COLOR = (0.38, 0.71, 0.86, 1)
DEFAULT_INACTIVE_BUTTON_COLOR = (1, 1, 1, 1)

HEADER_CHECKER_1 = (0.43, 0.76, 0.91, 0.5)
HEADER_CHECKER_2 = (0.38, 0.71, 0.86, 0.5)

CHECKER_1 = (0.4, 0.4, 0.4, 1)
CHECKER_2 = (0.3, 0.3, 0.3, 1)


class CustomLabel(Label):

    def __init__(self, c_col, **kwargs):
        super().__init__(**kwargs)
        self.c_col = c_col

    def on_pos(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*self.c_col)
            Rectangle(pos=self.pos, size=self.size)


class GUIConditionalProbabilityTable(GridLayout):

    def __init__(self, table: ConditionalProbabilityTable, **kwargs):
        super().__init__(**kwargs)

        l_kwargs = {"size_hint": (None, None), "size": (75, 20), "padding": (5, 5)}

        self.cols = 2 + len(table.given)
        self.rows = 1 + len(table.table_rows)
        self.background_color = (1, 1, 1, 1)

        header = [table.variable.name, *[str(i) for i in table.given], "P"]
        rows = [[row[0].outcome, *[i.outcome for i in row[1]], str(row[2])] for row in table.table_rows]

        H_CUR = HEADER_CHECKER_1
        for r in range(len(header)):
            self.add_widget(CustomLabel(text=header[r], c_col=H_CUR, **l_kwargs))
            H_CUR = HEADER_CHECKER_2 if H_CUR == HEADER_CHECKER_1 else HEADER_CHECKER_1

        C_START = CHECKER_1
        for row in rows:
            C_CUR = C_START
            C_START = CHECKER_2 if C_START == CHECKER_1 else CHECKER_1
            for idx in range(len(row)):
                self.add_widget(CustomLabel(text=row[idx], c_col=C_CUR, **l_kwargs))
                C_CUR = CHECKER_2 if C_CUR == CHECKER_1 else CHECKER_1


class VariablePage(GridLayout):

    def __init__(self, graph_data, **kwargs):
        super().__init__(**kwargs)

        l_kwargs = {"size_hint_y": None, "height": 30, "size_hint_max_x": 100}

        v = graph_data["variables"]

        self.cols = 2
        self.rows = 2

        self.padding = 30
        self.spacing = 20

        self.active_button = None

        label_kwargs = {
            "size_hint_y": 0.1,
            "size_hint_max_y": 80,
            "font_size": 30,
            "halign": "left",
            "valign": "top",
            "padding": (0, 0)
        }

        variables = Label(text="Variables", **label_kwargs)
        table = Label(text="Table:", **label_kwargs)
        variables.bind(size=variables.setter('text_size'))
        table.bind(size=table.setter('text_size'))

        self.add_widget(variables)
        self.add_widget(table)

        # Create a grid to store all the variable content in
        self.v_grid = GridLayout(rows=len(v)+1, cols=4)
        for _ in ["Variable", "Outcomes", "Parents", "Children"]:
            self.v_grid.add_widget(Label(text=_, **l_kwargs))

        for key in graph_data["variables"]:
            if key not in graph_data["tables"]:
                continue

            k_button = Button(text=key, **l_kwargs)
            k_button.bind(on_press=partial(self.set_shown_table, k_button, graph_data["tables"][key]))

            o_label = Label(text=", ".join(i for i in v[key].outcomes), **l_kwargs)
            p_label = Label(text=", ".join(i for i in v[key].parents), **l_kwargs)
            c_label = Label(text=", ".join(i for i in v if key in v[i].parents), **l_kwargs)

            for b in [k_button, o_label, p_label, c_label]:
                self.v_grid.add_widget(b)

        self.add_widget(self.v_grid)

        self.table_panel = BoxLayout()
        self.add_widget(self.table_panel)

        self.height = self.minimum_height

    def set_shown_table(self, button, table, *args):
        self.table_panel.clear_widgets()
        self.table_panel.add_widget(GUIConditionalProbabilityTable(table))
        if self.active_button is not None:
            self.active_button.background_color = DEFAULT_INACTIVE_BUTTON_COLOR
        button.background_color = DEFAULT_ACTIVE_BUTTON_COLOR
        self.active_button = button

    def lose_focus(self):
        self.table_panel.clear_widgets()
        self.active_button.background_color = DEFAULT_INACTIVE_BUTTON_COLOR

