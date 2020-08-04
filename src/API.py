import webview
import os

from python.config.config_manager import access
from python.util.parsers.GraphLoader import parse_graph_file_data

# Maybe this has to change for a build? How to get the path in dev, as well as a build?
PREFIX = "src/python/"


class API:
    """
    A Python API for pywebview, enabling the front-end JS/TS to interact with the Python backend
    """

    def __init__(self):

        # Just parse out and
        self.parsed = None

    def fullscreen(self):
        webview.windows[0].toggle_fullscreen()

    def save_content(self, content):
        filename = webview.windows[0].create_file_dialog(webview.SAVE_DIALOG)
        if not filename:
            return

        with open(filename, 'w') as f:
            f.write(content)

    def ls(self):
        return os.listdir('.')

    def access(self, param):
        return access(param)

    def get_graph_names(self):
        return sorted([f for f in os.listdir(PREFIX + self.access("graph_file_folder")) if f.endswith(".json")])

    def load_file(self, graph_file):
        self.parsed = parse_graph_file_data(graph_file)
        print(graph_file, "loaded.")
        return True