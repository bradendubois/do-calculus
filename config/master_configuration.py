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

master_config_file = [
    {
        "section": "Regression Tests",
        "description":
            "This section controls the regression testing suite, available to be run at launch, validating " +
            "the software before running.\n\nFor information on *creating* test files for the regression suite, see " +
            "``Regression Tests``.",
        "parameters": [{
            "parameter_title": "Run Regression Tests on Launch",
            "description": "Control whether or not to have the regression suite run on launch.",
            "parameter": "run_regression_tests_on_launch",
            "default_value": True,
            "options": [True, False]
        }, {
            "parameter_title": "Output Regression Results",
            "description":
                "If regression tests are enabled, control whether or not to output the results of the tests. Results " +
                "are of the form (success_boolean, success_message).\n\n``always`` and ``never`` are self-explanatory; " +
                "``failure`` will only print the results if there are errors.",
            "parameter": "output_regression_results",
            "default_value": "failure",
            "options": ["always", "failure", "never"],
        }, {
            "parameter_title": "Exit if Regression Failure",
            "description": "If regression tests are enabled and any test fails, control whether to exit the software " +
                "or launch anyway. Useful if test results are doubtful or features on unfinished.",
            "parameter": "exit_if_regression_failure",
            "default_value": False,
            "options": [True, False]
        }]
    }, {
        "section": "Output Control",
        "description": "Control what information is output; the computational steps of queries or regression tests, " +
                   "on launch, whether to minimize acceptable sets Z in backdoor paths.",
        "parameters": [{
            "parameter_title": "Output Computation Steps",
            "description": "If enabled, each step of a query will be output to the console. This will show the " +
                           "step-by-step application of each rule, and for larger queries, can be quite large.",
            "parameter": "output_computation_steps",
            "default_value": True,
            "options": [True, False]
        }, {
            "parameter_title": "Output Regression Step Computation",
            "description": "If enabled, shows all steps involved in regression tests; similar to the above, output " +
                           "can become very long.",
            "parameter": "output_regression_test_computation",
            "default_value": True,
            "options": [True, False]
        }, {
            "parameter_title": "Print Causal Graph Info on Instantiation",
            "description": "If enabled, when a Causal Graph is loaded from a file, information on each variable in" +
                           "the Causal Graph will be output.",
            "parameter": "print_cg_info_on_instantiation",
            "default_value": True,
            "options": [True, False]
        }, {
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
        "section": "File Directories",
        "description": "Here are directories specified in which to *search for/locate* files.",
        "parameters": [{
            "parameter_title": "Graph File Folder",
            "description": "A specific directory in which multiple graph files can be placed; they will be listed on " +
                           "launch, allowing the user to choose which one to load. For information on graph files, " +
                           "see ``Causal Graph Files``.",
            "parameter": "graph_file_folder",
            "default_value": "causal_graphs",
            "options": "any valid path in the project"
        }, {
            "parameter_title": "Regression Test Directory",
            "description": "A specific directory in which each regression test file can be placed; all test files in " +
                           "this directory will be automatically run if regression tests are enabled. For information " +
                           "on regression test files, see ``Regression Tests``.",
            "parameter": "regression_directory",
            "default_value": "regression_tests/test_files",
            "options": "any valid path in the project"
        }]
    }, {
        "section": "Logging Rules / Directories",
        "description":
            "Here are rules regarding whether or not to log computation queries and/or regression test results, and " +
            "if so, where to log said files.\n\n**Warning**: As a general rule, large causal graphs can result in " +
            "exceptionally large log files, and it is not recommended to log said queries; they will likely be too " +
            "long to be human-readable, a file size too large for stable text file reading, and the process of " +
            "writing all the information to said file will have a noticeable affect on performance.",
        "parameters": [{
            "parameter_title": "Log Computation",
            "description": "If enabled, queries will be logged to a file with a name conforming to the query. The " +
                           "file location is determined by ``logging_directory``.",
            "parameter": "log_computation",
            "default_value": True,
            "options": [True, False]
        }, {
            "parameter_title": "Log All Regression Computation",
            "description": "If enabled, when regression tests are run on launch, all computation involved will be " +
                           "written to a file named by the date and time the test is run. The location of the file " +
                           "will be the directory ``regression_log_subdirectory``, which is itself a subdirectory of " +
                           "``logging_directory``.",
            "parameter": "log_all_regression_computation",
            "default_value": True,
            "options": [True, False]
        }, {
            "parameter_title": "Logging Directory",
            "description": "The directory in which queries or regression tests will be logged, if they are enabled.",
            "parameter": "logging_directory",
            "default_value": "logging",
            "options": "any valid path in the project"
        }, {
            "parameter_title": "Regression Log Subdirectory",
            "description": "The subdirectory of ``logging_directory`` in which regression tests will be logged, if " +
                           "enabled.",
            "parameter": "regression_log_subdirectory",
            "default_value": "regression",
            "options": "any valid path name"
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
            "parameter_title": "Default Regression Test Repetition",
            "description": "In *deterministic* regression tests (see: ``Regression Tests``), " +
                           "this value specifies how many times to repeat a test.",
            "parameter": "default_regression_repetition",
            "default_value": 10,
            "options": "any positive integer"
        }, {
            "parameter_title": "Regression Test Result Precision",
            "description": "In a regression test (see: ``Regression Tests``) where an 'expected " +
                           "value' is provided, this is how many digits of precision the " +
                           "computed value must meet within. Higher requires more accuracy, but " +
                           "also a longer/more detailed hand-computed 'expected result'.",
            "parameter": "regression_levels_of_precision",
            "default_value": 5,
            "options": "any positive integer"
        }, {
            "parameter_title": "Apply Function Noise",
            "description": "In evaluating the value of variable where a function is provided rather than a table " +
                           "(see: ``Causal Graph Files``), this will control whether the 'noise functions' provided " +
                           "will be applied.",
            "parameter": "apply_any_noise",
            "default_value": True,
            "options": [True, False]
        }, {
            "parameter_title": "Recursive Noise Propagation",
            "description": "If ``apply_any_noise`` is enabled, this parameter will control whether any nested " +
                           "evaluation functions will be subject to noise, or just the primary/first function. For " +
                           "example, 'val(C) = val(B) + 1'. If enabled, val(B) is subject to noise. If disabled, " +
                           "only val(C).",
            "parameter": "recursive_noise_propagation",
            "default_value": True,
            "options": [True, False]
        }]
    }
]

