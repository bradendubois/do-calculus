import threading
import time
import sys
import random
import webview
import os

from util.parsers.GraphLoader import parse_graph_file_data


class API:

    def __init__(self, filename=None):

        self.filename = filename if filename else None
        self.parsed = None

        if self.filename:
            self.load_graph_file(self.filename)

        self.cancel_heavy_stuff_flag = False

    def init(self):
        response = {
            'message': 'Hello from Python {0}'.format(sys.version)
        }

        return response

    def test(self):
        return len(parse_graph_file_data("src/python/graphs/full/causal_graph_5.json")["variables"])

    def load_graph_file(self, full_path: str):
        assert os.path.isfile(full_path), "File not found."
        self.parsed = parse_graph_file_data(full_path)

    def getRandomNumber(self):
        response = {
            'message': 'Here is a random number courtesy of randint: {0}'.format(random.randint(0, 100000000))
        }
        return response

    def doHeavyStuff(self):
        time.sleep(0.1)  # sleep to prevent from the ui thread from freezing for a moment
        now = time.time()
        self.cancel_heavy_stuff_flag = False
        for i in range(0, 1000000):
            _ = i * random.randint(0, 1000)
            if self.cancel_heavy_stuff_flag:
                response = {'message': 'Operation cancelled'}
                break
        else:
            then = time.time()
            response = {
                'message': 'Operation took {0:.1f} seconds on the thread {1}'.format((then - now), threading.current_thread())
            }
        return response

    def cancelHeavyStuff(self):
        time.sleep(0.1)
        self.cancel_heavy_stuff_flag = True

    def sayHelloTo(self, name):
        response = {
            'message': 'Hello {0}!'.format(name)
        }
        return response

    def error(self):
        raise Exception('This is a Python exception')
