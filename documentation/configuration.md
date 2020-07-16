# Configuration File Settings

## Regression Tests

This section controls the regression testing suite, available to be run at launch, validating the software before running.

For information on *creating* test files for the regression suite, see ``Regression Tests``.

#### Run Regression Tests on Launch

Control whether or not to have the regression suite run on launch.

| Setting Name | Options | Default Value |
|:-:|:-:|:-:|
| ``run_regression_tests_on_launch`` | [True, False] | True |

#### Output Regression Results

If regression tests are enabled, control whether or not to output the results of the tests. Results are of the form (success_boolean, success_message).

``always`` and ``never`` are self-explanatory; ``failure`` will only print the results if there are errors.

| Setting Name | Options | Default Value |
|:-:|:-:|:-:|
| ``output_regression_results`` | ['always', 'failure', 'never'] | always |

#### Exit if Regression Failure

If regression tests are enabled and any test fails, control whether to exit the software or launch anyway. Useful if test results are doubtful or features on unfinished.

| Setting Name | Options | Default Value |
|:-:|:-:|:-:|
| ``exit_if_regression_failure`` | [True, False] | False |

## Output Control

Control what information is output; the computational steps of queries or regression tests, on launch, whether to minimize acceptable sets Z in backdoor paths.

#### Output Computation Steps

If enabled, each step of a query will be output to the console. This will show the step-by-step application of each rule, and for larger queries, can be quite large.

| Setting Name | Options | Default Value |
|:-:|:-:|:-:|
| ``output_computation_steps`` | [True, False] | False |

#### Output Regression Step Computation

If enabled, shows all steps involved in regression tests; similar to the above, output can become very long.

| Setting Name | Options | Default Value |
|:-:|:-:|:-:|
| ``output_regression_test_computation`` | [True, False] | False |

#### Print Causal Graph Info on Instantiation

If enabled, when a Causal Graph is loaded from a file, information on each variable inthe Causal Graph will be output.

| Setting Name | Options | Default Value |
|:-:|:-:|:-:|
| ``print_cg_info_on_instantiation`` | [True, False] | True |

#### Output Levels of Precision

How many digits of precision to output a result to.

| Setting Name | Options | Default Value |
|:-:|:-:|:-:|
| ``output_levels_of_precision`` | any positive integer | 5 |

#### Minimize Backdoor Sets

If enabled, when sets X and Y are given, and all feasible sets Z to ensure causal independence are created, only minimal sets will be shown.

| Setting Name | Options | Default Value |
|:-:|:-:|:-:|
| ``minimize_backdoor_sets`` | [True, False] | True |

#### Choosing Z Set in do-calculus

In the do-calculus of p(Y | do(X)), multiple possible sets Z may serve as a deconfounding set; control how the set Z is chosen. Either ``ask`` the user to select one, or choose one at ``random``, or run the query multiple times, using every possible set, ensuring only one answer is ever computed. The last option is useful in debugging.

| Setting Name | Options | Default Value |
|:-:|:-:|:-:|
| ``z_selection_preference`` | ['ask', 'random', 'all'] | all |

## File Directories

Here are directories specified in which to *search for/locate* files.

#### Graph File Folder

A specific directory in which multiple graph files can be placed; they will be listed on launch, allowing the user to choose which one to load. For information on graph files, see ``Causal Graph Files``.

| Setting Name | Options | Default Value |
|:-:|:-:|:-:|
| ``graph_file_folder`` | any valid path in the project | causal_graphs |

#### Regression Test Directory

A specific directory in which each regression test file can be placed; all test files in this directory will be automatically run if regression tests are enabled. For information on regression test files, see ``Regression Tests``.

| Setting Name | Options | Default Value |
|:-:|:-:|:-:|
| ``regression_directory`` | any valid path in the project | regression_tests/test_files |

## Logging Rules / Directories

Here are rules regarding whether or not to log computation queries and/or regression test results, and if so, where to log said files.

**Warning**: As a general rule, large causal graphs can result in exceptionally large log files, and it is not recommended to log said queries; they will likely be too long to be human-readable, a file size too large for stable text file reading, and the process of writing all the information to said file will have a noticeable affect on performance.

#### Log Computation

If enabled, queries will be logged to a file with a name conforming to the query. The file location is determined by ``logging_directory``.

| Setting Name | Options | Default Value |
|:-:|:-:|:-:|
| ``log_computation`` | [True, False] | True |

#### Log All Regression Computation

If enabled, when regression tests are run on launch, all computation involved will be written to a file named by the date and time the test is run. The location of the file will be the directory ``regression_log_subdirectory``, which is itself a subdirectory of ``logging_directory``.

| Setting Name | Options | Default Value |
|:-:|:-:|:-:|
| ``log_all_regression_computation`` | [True, False] | False |

#### Logging Directory

The directory in which queries or regression tests will be logged, if they are enabled.

| Setting Name | Options | Default Value |
|:-:|:-:|:-:|
| ``logging_directory`` | any valid path in the project | logs |

#### Regression Log Subdirectory

The subdirectory of ``logging_directory`` in which regression tests will be logged, if enabled.

| Setting Name | Options | Default Value |
|:-:|:-:|:-:|
| ``regression_log_subdirectory`` | any valid path name | regression |

#### Update from Github on Launch

If enabled, the project will attempt to pull from Github, and effectively update itself, on launch - it probably won't even need to be restarted if there is an update.

| Setting Name | Options | Default Value |
|:-:|:-:|:-:|
| ``github_pull_on_launch`` | [True, False] | False |

## Accuracy / Formatting / Precision Rules

Regards settings on the accuracy/settings of regression tests, computation caching, and noisein function evaluations.

#### Cache Computation Results

If enabled, any time a specific query is computed, its results will be cached; if the same query is required in any subsequent queries, its cached result will be reused instead of computing the same result from scratch. This can yield a large performance increase in larger causal graphs.

| Setting Name | Options | Default Value |
|:-:|:-:|:-:|
| ``cache_computation_results`` | [True, False] | True |

#### Topological Sort Variables

If enabled, to avoid Bayes rule as much as possible, the head and body of queries can be topologically sorted.

| Setting Name | Options | Default Value |
|:-:|:-:|:-:|
| ``topological_sort_variables`` | [True, False] | True |

#### Default Regression Test Repetition

In *deterministic* regression tests (see: ``Regression Tests``), this value specifies how many times to repeat a test.

| Setting Name | Options | Default Value |
|:-:|:-:|:-:|
| ``default_regression_repetition`` | any positive integer | 10 |

#### Regression Test Result Precision

In a regression test (see: ``Regression Tests``) where an 'expected value' is provided, this is how many digits of precision the computed value must meet within. Higher requires more accuracy, but also a longer/more detailed hand-computed 'expected result'.

| Setting Name | Options | Default Value |
|:-:|:-:|:-:|
| ``regression_levels_of_precision`` | any positive integer | 5 |

#### Apply Function Noise

In evaluating the value of variable where a function is provided rather than a table (see: ``Causal Graph Files``), this will control whether the 'noise functions' provided will be applied.

| Setting Name | Options | Default Value |
|:-:|:-:|:-:|
| ``apply_any_noise`` | [True, False] | True |

#### Recursive Noise Propagation

If ``apply_any_noise`` is enabled, this parameter will control whether any nested evaluation functions will be subject to noise, or just the primary/first function. For example, 'val(C) = val(B) + 1'. If enabled, val(B) is subject to noise. If disabled, only val(C).

| Setting Name | Options | Default Value |
|:-:|:-:|:-:|
| ``recursive_noise_propagation`` | [True, False] | True |

