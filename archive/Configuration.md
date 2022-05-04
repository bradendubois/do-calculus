Settings for the project are stored in ``config.yml`` in the same directory as the Python file that imports ``Do``.
- **Note**: This file will be created if it does not exist, when the project is run.

## Output Control

Control what information is output; the computational steps of queries or regression tests, on launch, whether to minimize acceptable sets Z in backdoor paths.

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

#### Regression Test Result Precision

In a regression test (see: ``Regression Tests``) where an 'expected value' is provided, this is how many digits of precision the computed value must meet within. Higher requires more accuracy, but also a longer/more detailed hand-computed 'expected result'.

| Setting Name | Options | Default Value |
|:-:|:-:|:-:|
| ``regression_levels_of_precision`` | any positive integer | 5 |

