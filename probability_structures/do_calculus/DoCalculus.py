#########################################################
#                                                       #
#   Do Calculus                                         #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# A main REPL area allowing the user to give their sets and apply the rules of do-calculus

from probability_structures.do_calculus.application.DoCalculusQueryOptions import do_calculus_options
from probability_structures.do_calculus.application.QueryStructures import QueryList, Query, QueryBody
from probability_structures.do_calculus.ids_ai.IDS_Solver import IDSSolver

from probability_structures.Graph import Graph

from utilities.IO_Logger import io
from utilities.helpers.CallableItemWrapper import CallableItemWrapper
from utilities.helpers.DisjointSets import disjoint
from utilities.parsing.UserIndexSelection import user_index_selection


########################
#   Do-Calculus REPL   #
########################

def do_calculus_repl(graph: Graph):
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

    # Y, X, and W will be manipulated through a QueryList object of Queries
    current_query = None

    while True:

        # No variables yet
        if current_query is None:

            # We need to validate our input, so just keep trying through Assertions
            while True:

                try:
                    # Relay the prompt to the user
                    io.write(do_calculus_prompt, console_override=True)

                    # Outcomes
                    y = process_set(input("Please enter set Y, which will not be an intervention: "))

                    # Interventions
                    x = process_set(input("Please enter all interventions: "))
                    assert disjoint(x, y), "Sets are not disjoint!"

                    # Observations
                    w = process_set(input("Please enter all observations: "))
                    assert disjoint(w, x, y), "Sets are not disjoint!"

                    # All variables must be defined in the graph
                    assert all(v in graph.v for v in y | x | w), "Not all variables defined in the graph."

                    # Construct a QueryList object (of 1 query, initially)
                    current_query = QueryList([Query(y, QueryBody(x, w))])

                except AssertionError as e:
                    io.write(",".join(str(arg) for arg in e.args))
                    continue

                break

        # Present all options to the user
        io.write("Our query is currently: " + str(current_query), console_override=True)

        # Generate all our possible options
        query_options = do_calculus_options(current_query, graph)
        options = [item[0] for item in query_options]

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

            # Create the solver; create one and insert our current query rather than initialize the solver with
            #   our initial sets
            solver = IDSSolver(graph, set(), set(), set())
            solver.initial_query_list = current_query.copy()

            # Try solving
            result = solver.solve()
            if result.success:
                io.write("The AI Solver was able to find a solution.", console_override=True)
                io.write(str(result.result))
                current_query = result.result
            else:
                io.write("The AI Solver was not able to find a solution.", console_override=True)

        # We've gotten our selection, update our sets accordingly and go again
        else:
            current_query = query_options[selection][1]
