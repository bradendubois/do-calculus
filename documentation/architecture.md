# Architecture

An outline of the design and architecture of the software.

## Main

This is the file to be run directly. Its order of operations are as follows:

- When the software begins, if enabled, the regression suite first runs. Results are returned to Main, which may be output.
- After this, the graph file location specified is read, and listed. The user selects a file, which is loaded into a Causal Graph.
- Finally, the Causal Graph's main IO driver is started.
- The user can interact with the CG until exiting, after which they are prompted to select another file or exit.

## Regression Suite

When run, all the test files in the default test file location are read, and one-by-one, run. Each file is run, and its results are stored; this allows the regression suite to list the outcome of every file, and return a summary "all tests passed" or "some errors found" type of response.

Each test file is run as follows:

- First, a Causal Graph is created from the file.
- Second, every variable with probability tables is evaluated; P(X) must equal 1.0, where this is calculated by Sigma_X P(X); where the probability of each outcome of X is calculated.
- Third, the actual tests listed in the file are finally run.

If any test in a file fails, this returns a failure signal and error message, moving onto the next file.

The code driving the regression suite is located in ``utilities/RegressionTesting``.

## Probability Structures

This is the main section of the code; located in ``probability_structures``, it consists of the code driving Causal Graphs, Conditional Probability Tables, Backdoor Controllers, the IO Logger, custom Exceptions, and the Variable/Outcome/Intervention classes.

### Custom Exceptions

Throughout the entire software, custom exceptions are used to indicate various kinds of failures.

A ProbabilityException is used as a "base" exception, since Exceptions can extend this base, so the following can be done:

```python
try:
    foo()
except ProbabilityException:
    print("Some kind of Probability-related exception was raised!")
except Exception:
    print("Some kind of more general exception occurred.")
```

Allowing one to catch Probability-related exceptions, but still crash/find other errors, and not rely on extremely broad ``except Exception`` clauses.

These are located in ``utilities/ProbabilityExceptions``

### Variables

This is a small class that represents a Variable. It requires a unique *name*, and some list of possible *outcomes*. For example, a variable X may have outcomes x, ~x.

Located in ``probability_structures/VariableStructures``.

### Outcomes

This is a class representing a specific outcome of a variable. For example, one outcome of X may be x, and we can create an Outcome object to represent that the Variable is X, and the *outcome* is x.

Located in ``probability_structures/VariableStructures``.

### Interventions

This is a class representing an "intervention" / do(X). It is functionally equivalent to the Outcome class, except for purposes of do-calculus, we want to identify that this is a *special kind of outcome*.

Located in ``probability_structures/VariableStructures``.

### IO Logger

This is an abstraction of writing the a console / file using the standard "print" or "write" functions. By abstracting the process to all be unified to a single function, "write", we can replace the default printing method, and this will allow us to output to the terminal, while also writing to a file, or only writing to the terminal.

The idea of how it "works" is that we can simply call an instance of the IO Logger (io) to "open" a file, and the process of creating any directories / files is done through the IO Logger. We can "close" the file whenever we want, but we have simply opened it, and any time we "write" a message through the Logger, it can be output to the terminal, while also being written to the file open.

The console can be "disabled", and this is for regression tests; if we don't want to see the steps involved, but still want to *log* it, we can disable the console output section, but continue writing to a file.

All the methods are fairly straightforward, except for ``write``.

The \* operator is used, allowing a comma-separated list of strings to log, with keyword arguments following:

- "join": how to join the strings, which typically would be mirroring the print function.
- "end": Usually it'll default to printing a newline at the end (like print), though we always print a blank line at the start for very readable spacing between messages.
- "x_offset": To track sub-queries in computation processing, it's useful to space the message "over" a bit, where the horizontal displacement represents the "depth" of the query; it makes it clear if we ask "Need A and B", and then a slight indentation is made on "Figuring out A" that they are connected. It works by indenting the first line of text by this amount, and then replacing any newlines in the message with a newline that has been indented an appropriate amount.
- "console_override": This is simply because we can disable almost all console output (computation steps, mostly), but some messages like results *absolutely* should be output to the console. If this flag is true, it will just print it regardless of whether it's "enabled" or not.

Located in ``utilities/IO_Logger``

### Conditional Probability Tables

This represents a specific table for a variable and its parents.

The ``__str__`` method is fairly dense, but the idea is to pack all the information into a numpy table for easier formatting (easily accessing columns, etc.), and then we can do things like padding by measuring the widest item in a column, and adding appropriate spacing to all the other boxes in this column, etc.

The ``probability_lookup`` is the most important; we want to go through, row by row on the table, and if this specific row's set of outcomes matches our given set, we can return this row's probability.

### Backdoor Controller

For the Backdoor Controller, most of it is fairly straightforward; the key to the backdoor detection algorithm is understanding the meaning of a backdoor path, and especially so on "blocking" these paths. You find that a variable might be necessarily in Z, but in putting it there (as in the case of a collider) can still *open* a path; the path-finding must be nuanced enough to understand that something in Z or not in Z changes whether we can go "up" (child to parent), "down" (parent to child), or both.

Generally, however, we want to find all sufficient sets Z. We begin by taking all variables in G, and removing any that could not possibly be in Z. This is easy enough; we cannot have a variable in X or Y in Z. We can not have a variable along a straight-forward path from X to Y in Z either; the use of an incredibly helpful path algorithm provided by Dr. Neufeld is employed here. We take the remaining variables (after removing X, Y, and X->Y) and take the power set; any possible set in this may be a sufficient Z if it blocks all paths.

The backdoor detection algorithm for backdoor paths from X -> Y, with a de-confounder Z take the cross product of X and Y, and sees if a backdoor path exists along any of these. The actual path-finding is as a follows (starting from x, searching for y):

```pseudo
backdoor(x, y, Z, current path, paths, previous movement
    
    if x == y
        we complete a backdoor path
        return all paths so far, plus this path

    if x is not in the path
        if previous movement was down

            if x is in Z, or a descendant of x is in Z
                for every parent of x
                    paths = backdoor(parent, y, current path + x, paths, up)


            if x is not in Z
                for every child of x
                    paths = backdoor(child, y, current path + x, paths, down)

        if previous movement was up
            if x is not in Z
                
                for every parent of x
                    paths = backdoor(parent, y, current path + x, paths, up)
                for every child of x
                    paths = backdoor(child, y, current path + x, paths, up)

    return paths 
```

The idea is that we can always move "up" or "down" through non-controlled variables if we are heading in the same direction. This is consistent with Pearl's definitions, where a path can be blocked along i -> j -> k, if j is in Z. We can also move up, then down, if the variable is not in Z, just as i <- j -> k, where j is *not* in Z. We can also move down, then up, if this variable is in Z, or a child of Z is; i -> j <- k, where j is in Z.

### Causal Graphs

TODO - The Causal Graph is the undoubtedly the largest part of the software, driving standard probability computations (relying on the Backdoor Controller when do-calculus is deployed).

