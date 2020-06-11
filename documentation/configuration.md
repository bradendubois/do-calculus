# Configuration File

A breakdown of the settings available in ``config/config.json``.

- **"runRegressionTestsOnLaunch"** = \[true, false\]: Enable/Disable running all regression tests on launch.
- **"outputRegressionResults"** = \["failure", "always", "never"\]: If regression tests are run, control whether or not to print the results. "failure" will only print when an error occurs.
- **"outputRegressionComputation"** = \[true, false\]: Enable/Disable outputting all info in the regression test calculations.
- **"exitIfRegressionFailure"** = \[true, false\]: Control whether to exit the software early if any tests fail. 
- **"graph_file_folder"** = "causal_graphs": The default folder to search for causal graph files.
- **"logAllComputation"** = [true, false\]: Control whether to store a text file of all calculations used in any computations.
- **"loggingLocation"** = "logging": The default folder to store log files of computations to. 
- **"storeAllResolvedCalculations"** = \[true, false\]: Toggle whether to cache any completed computations, to speed up future queries for the same results. 
- **"defaultRegressionRepetition" = 10**: The default number of times to repeat a calculation in regression tests for deterministic output. 
- **"printCausalGraphInfoOnInstantiation"** = \[true, false\]: Whether or not to print out information on the causal graph graph loaded. 