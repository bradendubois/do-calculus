from .config_manager import settings_yml


class Settings:

    cache_computation_results = settings_yml["cache_computation_results"]
    minimize_backdoor_sets = settings_yml["minimize_backdoor_sets"]
    output_levels_of_precision = settings_yml["output_levels_of_precision"]
    regression_levels_of_precision = settings_yml["regression_levels_of_precision"]
    topological_sort_variables = settings_yml["topological_sort_variables"]
