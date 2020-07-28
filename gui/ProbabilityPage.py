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
from kivy.uix.stacklayout import StackLayout
from kivy.uix.dropdown import DropDown

from probability_structures.BackdoorController import BackdoorController
from probability_structures.VariableStructures import Outcome
from util.parsers.GraphLoader import parse_graph_file_data, ConditionalProbabilityTable, Intervention

Config.set('graphics', 'resizable', True)

DEFAULT_ACTIVE_BUTTON_COLOR = (0.38, 0.71, 0.86, 1)
DEFAULT_INACTIVE_BUTTON_COLOR = (1, 1, 1, 1)

HEADER_CHECKER_1 = (0.43, 0.76, 0.91, 0.5)
HEADER_CHECKER_2 = (0.38, 0.71, 0.86, 0.5)

CHECKER_1 = (0.4, 0.4, 0.4, 1)
CHECKER_2 = (0.3, 0.3, 0.3, 1)


class PHeader(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Label(text="Compute a Probability.", text_size="20"))
        self.reset = Button(text="Reset")


class ProbabilityPage(StackLayout):

    def __init__(self, graph_data, **kwargs):
        super().__init__(**kwargs)

        self.variables = graph_data["variables"]

        # Copy the graph
        self.g = graph_data["graph"].copy()
        self.g.reset_disabled()

        # Take a BackdoorController to verify variables that can be added/removed
        self.bc = BackdoorController(self.g.copy())

        l_kwargs = {"size_hint_y": None, "height": 30, "size_hint_max_x": 100}

        self.orientation = "lr-tb"
        self.padding = 30
        self.spacing = 5

        v = graph_data["variables"]

        # The components of the working query the user adjusts
        self.head = set()
        self.body = set()

        # Sets of variables in each component for the path-finding
        self.head_vars = set()
        self.inter_vars = set()
        self.observ_vars = set()

        label_kwargs = {
            "size_hint_y": 0.1,
            "size_hint_max_y": 80,
            "font_size": 30,
            "halign": "left",
            "valign": "top",
            "padding": (0, 0)
        }

        r_props = {
            "size_hint_max_x": 30,
            "size_hint_max_y": 30
        }

        # Add header
        self.add_widget(Label(text="Compute a Probability.", font_size=20, size_hint=(1.0, None)))

        # Add explanatory line along with reset button
        self.help_row = BoxLayout(orientation="horizontal", size_hint=(1.0, None))
        help_msg = "Enter data to the query, such as outcomes, interventions/treatments, as well as observed data."
        self.help_row.add_widget(Label(text=help_msg))
        button = Button(text="Reset Query", **r_props)
        button.bind(on_press=self.reset)
        self.help_row.add_widget(button)
        self.add_widget(self.help_row)

        d_args = {
            # "size_hint_y": None
        }

        a = {
            "orientation": "horizontal",
            "size_hint": (0.3, None),
            "height": 300,
        }

        b_args = {
            "text": "add",
            "height": 40,
            "size_hint_y": None
        }

        # Outcomes
        self.o_box = BoxLayout(**a)
        self.outcome_drop_down_button = Button(**b_args)
        self.o_box.add_widget(Label(text="Outcomes:", **label_kwargs))
        self.o_box.add_widget(self.outcome_drop_down_button)
        self.outcome_drop = DropDown()
        self.outcome_drop_down_button.bind(on_release=self.outcome_drop.open)

        # Interventions
        self.i_box = BoxLayout(**a)
        self.interventions_drop_down_button = Button(**b_args)
        self.i_box.add_widget(Label(text="Interventions:", **label_kwargs))
        self.i_box.add_widget(self.interventions_drop_down_button)
        self.intervention_drop = DropDown()
        self.interventions_drop_down_button.bind(on_release=self.intervention_drop.open)

        # Observations
        self.ob_box = BoxLayout(**a)
        self.observations_drop_down_button = Button(**b_args)
        self.ob_box.add_widget(Label(text="Observations:", **label_kwargs))
        self.ob_box.add_widget(self.observations_drop_down_button)
        self.observations_drop = DropDown()
        self.observations_drop_down_button.bind(on_release=self.observations_drop.open)

        self.add_widget(self.o_box)
        self.add_widget(self.i_box)
        self.add_widget(self.ob_box)

        # Update what can appear in each respective drop-down box
        self.update_drop_downs()

    def update_drop_downs(self):

        errors = []
        b_args = {
            "height": 40,
            "size_hint_y": None
        }

        # Empty all
        for s in [self.outcome_drop, self.intervention_drop, self.observations_drop]:
            s.clear_widgets()

        for v in self.g.v - (self.head_vars | self.inter_vars | self.observ_vars):

            # Outcomes
            h_subsets = self.bc.get_all_z_subsets(self.inter_vars, self.head_vars | {v})
            if len(h_subsets) > 0:
                for outcome in self.variables[v].outcomes:
                    button = Button(text="{} = {}".format(v, outcome), **b_args)
                    button.bind(on_release=lambda btn: self.add_var(btn, "outcome"))
                    self.outcome_drop.add_widget(button)
            else:
                errors.append("Cannot insert Y as an outcome given out current 'do's.")

            # Intervention
            t_subsets = self.bc.get_all_z_subsets(self.inter_vars | {v}, self.head_vars)

            if len(t_subsets) > 0:
                if v == "X4":
                    for s in t_subsets:
                        print(str(self.inter_vars), str({v}), str(self.inter_vars | {v}), str(s), not (self.inter_vars | {v}).issubset(s))
                for outcome in self.variables[v].outcomes:
                    button = Button(text="{} = {}".format(v, outcome), **b_args)
                    button.bind(on_release=lambda btn: self.add_var(btn, "intervention"))
                    self.intervention_drop.add_widget(button)
            else:
                errors.append("Cannot insert Y as an intervention given out current 'do's.")

            # Observation
            if any(v not in subset for subset in h_subsets):
                for outcome in self.variables[v].outcomes:
                    button = Button(text="{} = {}".format(v, outcome), **b_args)
                    button.bind(on_release=lambda btn: self.add_var(btn, "observation"))
                    self.observations_drop.add_widget(button)
            else:
                errors.append("Cannot insert Y as an observation given out current 'do's.")

        print("Done")

    def add_var(self, button: Button, s: str):

        name, value = (s.strip() for s in button.text.split("="))

        if s == "outcome":
            self.head_vars.add(name)
            self.head.add(Outcome(name, value))
        elif s == "intervention":
            self.inter_vars.add(name)
            self.body.add(Intervention(name, value))
        elif s == "observation":
            self.observ_vars.add(name)
            self.body.add(Outcome(name, value))
        else:
            print("Unknown s value {s}")

        self.update_drop_downs()

    def lose_focus(self):
        pass
        # self.active_button.background_color = DEFAULT_INACTIVE_BUTTON_COLOR

    def reset(self, *args):
        self.head_vars.clear()
        self.inter_vars.clear()
        self.observ_vars.clear()
        self.update_drop_downs()
