# Configuration File

A breakdown of the settings available in ``config/config.json``.

- **"run_regression_tests_on_launch"** = \[true, false\]: Enable/Disable running all regression tests on launch.
- **"output_regression_results"** = \["failure", "always", "never"\]: If regression tests are run, control whether or not to print the results. "failure" will only print when an error occurs.
- **"output_computation_steps"** = \[true, false\]: Enable/Disable outputting all info in the regression test calculations.
- **"exit_if_regression_failure"** = \[true, false\]: Control whether to exit the software early if any tests fail. 
- **"graph_file_folder"** = "causal_graphs": The default folder to search for causal graph files.
- **"log_computation"** = \[true, false\]: Control whether to store a text file of all calculations used in any computations.
- **"logging_directory"** = "logging": The default folder to store log files of computations to. 
- **"cache_computation_results"** = \[true, false\]: Toggle whether to cache any completed computations, to speed up future queries for the same results. 
- **"default_regression_repetition" = 10**: The default number of times to repeat a calculation in regression tests for deterministic output. 
- **"print_cg_info_on_instantiation"** = \[true, false\]: Whether or not to print out information on the causal graph graph loaded. 
- **"regression_directory"** = "regression_tests/test_files": The location of regression test files to run.
- **"regression_levels_of_precision"** = 5: The number of digits of precision calculated and expected results must meet within.
- **"output_levels_of_precision:** = 5: The number of digits of precision calculated results will be output to.
