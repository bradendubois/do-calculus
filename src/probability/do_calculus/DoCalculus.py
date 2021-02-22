#########################################################
#                                                       #
#   Do Calculus                                         #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

# A main REPL area allowing the user to give their sets and apply the rules of do-calculus

from src.probability.do_calculus.application.DoCalculusQueryOptions import do_calculus_options
from src.probability.do_calculus.application.QueryListParser import ql_probability
from src.probability.do_calculus.application.QueryStructures import QueryList, Query, QueryBody
from src.probability.do_calculus.ids_ai.IDS_Solver import IDSSolver

from src.probability.structures.Graph import Graph

from src.util.helpers import disjoint

# TODO Deprecated; Incorporate into the new REPL system


########################
#   Do-Calculus REPL   #
########################

def do_calculus_repl(graph: Graph, outcomes: dict, tables: dict):
    """
    Enter a main REPL area allowing the manipulation of do_calculus
    :param graph: An unmodified graph representing our graph space
    :param outcomes: A dictionary mapping a variable to its list of outcomes
    :param tables: A dictionary mapping a variable to its respective conditional probability table
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
    y, x, w, u = set(), set(), set(), set()

    while True:

        # No variables yet
        if current_query is None:

            # We need to validate our input, so just keep trying through Assertions
            while True:

                try:
                    # Relay the prompt to the user
                    io.write(do_calculus_prompt)

                    # Outcomes
                    y = process_set(input("Please enter set Y, which will not be an intervention: "))

                    # Interventions
                    x = process_set(input("Please enter all interventions: "))
                    assert disjoint(y, x), "Sets are not disjoint!"

                    # Observations
                    w = process_set(input("Please enter all observations: "))
                    assert disjoint(y, x, w), "Sets are not disjoint!"

                    # Un-observables
                    u = process_set(input("Please enter all unobservable variables: "))
                    assert disjoint(y, x, w, u), "Sets are not disjoint!"

                    # All variables must be defined in the graph
                    assert all(v in graph.v for v in y | x | w | u), "Not all variables defined in the graph."

                    # Construct a QueryList object (of 1 query, initially)
                    current_query = QueryList([Query(y, QueryBody(x, w))])

                except AssertionError as e:
                    io.write(",".join(str(arg) for arg in e.args))
                    continue

                break

        # Present all options to the user
        io.write("Our query is currently: " + str(current_query))

        # Generate all our possible options
        query_options = do_calculus_options(current_query, graph, u)
        options = [item[0] for item in query_options]

        # Allow the first option to be to input some variable data and see the probability, if any real data is provided
        if len(outcomes) > 0 and len(tables) > 0:
            options.insert(0, "Compute a probability on the current query.")

        # Add a handle to let the IDS Solver take over
        options.append("Let the IDS Solver attempt to find a solution.")

        # Throw an "exit/return" into the options in the REPL and get a selection
        options.append("Exit / Return")
        selection = user_index_selection("All Possible Do-Calculus Applications: ", options)

        # Wants to see a specific query executed
        if options[selection] == "Compute a probability on the current query.":

            try:

                # Get every variable currently used in the query
                all_variables = set().union(*[q.head | q.body.interventions | q.body.observations for q in current_query.queries if isinstance(q, Query)])

                # Filter only the ones we actually need, not simply all we started with
                need_to_know = (y | x | w) & all_variables

                # Ask for an outcome for each variable
                known = dict()
                for variable in need_to_know:
                    result = input("Please enter a valid outcome for " + variable + ": ")
                    assert result in outcomes[variable], "Not a valid outcome for " + variable
                    known[variable] = result

                # Collect all our data needed to compute this query
                data = {
                    "known": known,
                    "graph": graph,
                    "outcomes": outcomes,
                    "tables": tables,
                    "ql": current_query
                }

                # Execute the query
                io.write(str(current_query), "=", ql_probability(**data))

            except AssertionError as e:
                io.write(",".join(str(",".join(str(j)) for j in i) for i in e.args))

        # Exit option
        elif options[selection] == "Exit / Return":
            return

        # AI Takeover
        elif options[selection] == "Let the IDS Solver attempt to find a solution.":

            # Create the solver; create one and insert our current query rather than initialize the solver with
            #   our initial sets
            solver = IDSSolver(graph, set(), set(), set())
            solver.initial_query_list = current_query.copy()
            solver.u = u

            # Try solving
            result = solver.solve()
            if result.success:
                io.write("The AI Solver was able to find a solution.")
                io.write(str(result.result))
                current_query = result.result
            else:
                io.write("The AI Solver was not able to find a solution.")

        # We've gotten our selection, update our sets accordingly and go again
        else:
            current_query = query_options[selection][1]
