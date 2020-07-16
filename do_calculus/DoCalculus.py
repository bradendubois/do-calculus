#########################################################
#                                                       #
#   Do Calculus                                         #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# A main REPL area allowing the user to give their sets and apply the rules of do-calculus

from do_calculus.application.DoCalculusQueryOptions import do_calculus_options
from do_calculus.ids_ai.IDS_Solver import IDSSolver

from probability_structures.Graph import Graph

from utilities.IO_Logger import io
from utilities.helpers.CallableItemWrapper import CallableItemWrapper
from utilities.helpers.DisjointSets import disjoint
from utilities.parsing.UserIndexSelection import user_index_selection


########################
#   Do-Calculus REPL   #
########################

def do_calculus(graph: Graph):
    """
    Enter a main REPL area allowing the manipulation of do_calculus
    :param graph: An unmodified graph representing our graph space
    """

    def process_set(string: str) -> set:
        return set([item.strip() for item in string.split(",")] if string.strip() != "" else [])

    do_calculus_rules = "Rule 1: P(y | do(x), z, w) = P(y | do(x), w) if (Y _||_ Z | X, W) in G(-X)\n" \
                        "Rule 2: P(y | do(x), do(z), w) = P(y | do(x), z, w) if (Y _||_ Z | X, W) in G(-X, Z_)\n" \
                        "Rule 3: P(y | do(x), do(z), w) = P(y | do(x), w) if (Y _||_ Z | X, W) in G(-X, -Z(W))"

    do_calculus_prompt = "To test the 3 rules of do_calculus, we manipulate 4 sets of variables: X, Y, Z, and W.\n" \
                         "In these rules, X and Z may be interventions. The rules are:\n\n" + \
                         do_calculus_rules + \
                         "\n\nPlease enter each, one at a time (when prompted), as a comma-separated list.\n" \
                         "Also, note that any of X, Z, or W may be left empty.\n"

    # We will hold a set of all variables y, x, w and manipulate it through user input
    y = None
    x = None
    w = None

    while True:

        # No variables yet
        if y is None or x is None or w is None:

            # We need to validate our input, so just keep trying through Assertions
            while True:
                try:
                    all_sets = []
                    io.write(do_calculus_prompt, console_override=True)

                    y = process_set(input("Please enter set Y, which will not be an intervention: "))
                    all_sets.append(y)

                    x = process_set(input("Please enter all interventions: "))
                    all_sets.append(x)
                    assert disjoint(x, y), "Sets are not disjoint!"

                    w = process_set(input("Please enter all observations: "))
                    all_sets.append(w)
                    assert disjoint(w, x, y), "Sets are not disjoint!"

                except AssertionError:
                    continue

                break

        # Present all options to the user
        # current_query = query_str(y, x, w)
        # io.write("Our query is currently: " + current_query, console_override=True)

        # Generate all our possible options
        options = do_calculus_options(graph.copy(), y, x, w)

        # Add a handle to let the IDS Solver take over
        options.append([CallableItemWrapper(), "Let the IDS Solver attempt to find a solution."])

        # Throw an "exit/return" into the options in the REPL and get a selection
        options.append([CallableItemWrapper(), "Exit / Return"])
        selection = user_index_selection("All Possible Do-Calculus Applications: ", options)

        # Exit option
        if selection == len(options)-1:
            return
        
        # AI Takeover
        elif selection == len(options)-2:
            
            solver = IDSSolver(graph, y, x, w)
            result = solver.solve()
            if result.success:
                io.write("The AI Solver was able to find a solution.", console_override=True)
                y, x, w = result.result
            else:
                io.write("The AI Solver was not able to find a solution.", console_override=True)

        # We've gotten our selection, update our sets accordingly and go again
        else:
            y, x, w = options[selection][0].result
