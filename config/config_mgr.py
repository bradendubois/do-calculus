import json

config_file = "config/config.json"

with open(config_file) as f:
    settings = json.load(f)


def access(param: str) -> any:
    if param in settings:
        return settings[param]

# TODO - A function for config settings can let you do command-line flags to override the config file


def run_regression_tests_on_launch():
    return settings["runRegressionTestsOnLaunch"]


def output_regression_computation():
    return settings["outputRegressionComputation"]

