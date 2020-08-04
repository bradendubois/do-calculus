import os
import threading
import webview

from time import time

from API import API


def get_entrypoint():
    def exists(path):
        return os.path.exists(os.path.join(os.path.dirname(__file__), path))

    if exists('../gui/index.html'):             # unfrozen development
        return '../gui/index.html'

    if exists('../Resources/gui/index.html'):   # frozen py2app
        return '../Resources/gui/index.html'

    if exists('./gui/index.html'):
        return './gui/index.html'

    raise Exception('No index.html found')


def set_interval(interval):
    def decorator(function):
        def wrapper(*args, **kwargs):
            stopped = threading.Event()

            def loop():     # executed in another thread
                while not stopped.wait(interval):   # until stopped
                    function(*args, **kwargs)

            t = threading.Thread(target=loop)
            t.daemon = True     # stop if the program exits
            t.start()
            return stopped
        return wrapper
    return decorator


entry = get_entrypoint()


@set_interval(1)
def update_ticker():
    if len(webview.windows) > 0:
        webview.windows[0].evaluate_js('window.pywebview.state.setTicker("%d")' % time())


if __name__ == '__main__':
    api = API()
    window = webview.create_window('pywebview-react boilerplate', entry, js_api=api)
    webview.start(debug=True)
