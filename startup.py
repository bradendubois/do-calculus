import webview

from API import API

api = API()
window = webview.create_window('API example', "gui/content/index.html", js_api=api)
webview.start(debug=True)
