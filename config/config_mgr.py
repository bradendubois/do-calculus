import json

config_file = "config/config.json"

with open(config_file) as f:
    settings = json.load(f)


def access(param: str) -> any:
    if param in settings:
        return settings[param]
