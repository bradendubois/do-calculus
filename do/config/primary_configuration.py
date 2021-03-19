#########################################################
#                                                       #
#   Master Configuration File                           #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# This is the master file of all settings that go into a configuration file, and all documentation on configuration
#   files is will be generated from this.

primary_config_file = [
    {
        "section": "Output Control",
        "description": "Control what information is output; the computational steps of queries or regression tests, " +
                   "on launch, whether to minimize acceptable sets Z in backdoor paths.",
        "parameters": [{
            "parameter_title": "Output Levels of Precision",
            "description": "How many digits of precision to output a result to.",
            "parameter": "output_levels_of_precision",
            "default_value": 5,
            "options": "any positive integer"
        }, {
            "parameter_title": "Minimize Backdoor Sets",
            "description": "If enabled, when sets X and Y are given, and all feasible sets Z to ensure causal " +
                           "independence are created, only minimal sets will be shown.",
            "parameter": "minimize_backdoor_sets",
            "default_value": True,
            "options": [True, False]
        }]
    }, {
        "section": "Accuracy / Formatting / Precision Rules",
        "description": "Regards settings on the accuracy/settings of regression tests, computation caching, and noise" +
                       "in function evaluations.",
        "parameters": [{
            "parameter_title": "Cache Computation Results",
            "description": "If enabled, any time a specific query is computed, its results will be cached; if the " +
                           "same query is required in any subsequent queries, its cached result will be reused " +
                           "instead of computing the same result from scratch. This can yield a large performance " +
                           "increase in larger causal graphs.",
            "parameter": "cache_computation_results",
            "default_value": True,
            "options": [True, False]
        }, {
            "parameter_title": "Topological Sort Variables",
            "description": "If enabled, to avoid Bayes rule as much as possible, the head and body of queries can be " +
                           "topologically sorted.",
            "parameter": "topological_sort_variables",
            "default_value": True,
            "options": [True, False]
        }, {
            "parameter_title": "Regression Test Result Precision",
            "description": "In a regression test (see: ``Regression Tests``) where an 'expected " +
                           "value' is provided, this is how many digits of precision the " +
                           "computed value must meet within. Higher requires more accuracy, but " +
                           "also a longer/more detailed hand-computed 'expected result'.",
            "parameter": "regression_levels_of_precision",
            "default_value": 5,
            "options": "any positive integer"
        }]
    }
]
