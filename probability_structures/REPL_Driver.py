#########################################################
#                                                       #
#   Query Driver                                        #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

from do_calculus.DoCalculus import do_calculus

from probability_structures.BackdoorController import BackdoorController
from probability_structures.CausalGraph import CausalGraph
from probability_structures.Graph import *
from probability_structures.VariableStructures import *

from utilities.IO_Logger import *
from utilities.ResultCache import *

from utilities.parsing.GetHeadAndBody import get_valid_head_and_body
from utilities.parsing.UserIndexSelection import *

# Union all Variable types with string for functions that can take any of these
CG_Types = str or Variable or Outcome or Intervention


class REPLDriver:
    """
    A "main" class driving most of the I/O
    """

    get_specific_outcome_prompt =  \
        "\nQuery a specific variable and its outcome." + \
        "\n  Format as: <VARIABLE> = <OUTCOME>" + \
        "\n    Example: 'Y = ~y'" + \
        "\n  Query: "

    get_given_data_prompt = \
        "\nEnter the given variables for the query, as a comma-separated list." + \
        "\n  Format: '<VARIABLE_1> = <OUTCOME_1>, <VARIABLE_2> = <OUTCOME_2>'" + \
        "\n  Leave empty to not assert any 'given' data." + \
        "\n    Example: 'X = ~x, Z = z'" + \
        "\n  Query: "

    get_probabilistic_variable_prompt = \
        "\nEnter a specific variable to compute the value of." + \
        "\n    Example: 'X'" + \
        "\n  Query: "

    error_msg_formatting = \
        "The given data is incorrect:\n" + \
        " - Some outcome may not be possible for some variable\n" + \
        " - Some variable may not be defined"

    def __init__(self, parsed_graph_contents: dict):

        # Store the contents of the parsed graph fle
        self.variables = parsed_graph_contents["variables"]     # Maps string name to the Variable object instantiated
        self.outcomes = parsed_graph_contents["outcomes"]       # Maps name/variable to a list of outcome values
        self.tables = parsed_graph_contents["tables"]           # Maps name/variable to corresponding table
        self.functions = parsed_graph_contents["functions"]     # Maps name/variable to corresponding functions
        self.graph = parsed_graph_contents["graph"]             # Graph representing the association structure.

        # Print all the variables out with their reach
        show = access("print_cg_info_on_instantiation") and io.console_enabled
        for variable in self.variables:
            v = self.variables[variable]
            io.write(str(v), "; Reaches:", v.reach, "Order:", v.topological_order, end="", console_override=show)

        # Aesthetic spacing
        io.write(end="", console_override=show)

        # Construct our Causal Graph; we must make a new one if modifying graph
        self.cg = CausalGraph(self.graph.copy(), self.variables, self.outcomes, self.tables, self.functions)

        # "Startup"
        self.running = True

    def shutdown(self):
        self.running = False

    def run(self):
        """
        The main REPL area of the project.
        """

        self.running = True
        while self.running:

            # Start with base options
            menu_options = [
                [self.run_do_calculus, "Apply and test the 3 rules of do_calculus."],
                [self.run_backdoor_controller, "Detect (and control) for \"back-door paths\"."],
                [self.run_joint_distribution_table, "Generate a joint distribution table."],
                [self.run_topological_sort, "See a topological sorting of the graph."],
                [self.shutdown, "Exit / Switch Graph Files"]
            ]

            # We *add* these two options if they are applicable; i.e, no probability stuff if no tables!

            # Compute some variable given that it has a function specified
            if len(self.functions) > 0:
                menu_options.insert(0, [self.run_probabilistic_function_query,
                                        "Compute the value of a variable given some function. Ex: f(X) = 42"
                                        ])

            # Compute some probability variable given that it has tables specified
            if len(self.tables) > 0:
                menu_options.insert(0, [self.run_probability_query,
                                        "Compute a probability. Ex: P(X | Y)"
                                        ])

            # Construct the menu and get the user to select an option
            menu_selection = user_index_selection("Select an option:", menu_options)

            # Call the function corresponding to the selected option
            menu_options[menu_selection][0]()

    # Standard Probability Query

    def run_probability_query(self):
        """
        The user chose to make a query on probabilities: construct a Causal Graph and have it collect data,
        modify the graph as necessary to compute the question, and exit
        """
        try:
            head, body = get_valid_head_and_body(self.get_specific_outcome_prompt, self.get_given_data_prompt, list(self.variables.keys()), self.outcomes)

        except AssertionError as e:
            io.write("Error: " + str(e.args), console_override=True)
            return

        # Happens if just given "X", not "X=x", making the Outcome() crash
        except IndexError:
            io.write("Improperly entered data.", console_override=True)
            return

        # Issue the query to the Causal Graph, allowing it to make any modifications necessary to compute the query
        self.cg.probability_query(head, body)

    # Probabilistic Function Query; f(X)

    def run_probabilistic_function_query(self):
        """
        Setup and execute a query of some variable which is determined by a function rather than probability tables
        """
        try:
            # Get and verify variable is in the graph
            variable = input(self.get_probabilistic_variable_prompt).strip()
            assert variable in self.variables

            # Calculate; results are a (min, max) tuple
            io.open("f(" + variable + ")")
            function_data = self.functions[variable]
            result = self.cg.probability_function_query(*function_data, apply_noise=access("apply_any_noise"))
            store_computation(str(variable), result)
            io.write(variable, "= min: {}, max: {}".format(*result), console_override=True)
            io.close()

        except KeyError:
            io.write("Given variable not resolvable by a probabilistic function.", console_override=True)
        except AssertionError:
            io.write("Variable given not in the graph.", console_override=True)

    # Backdoor Controller

    def run_backdoor_controller(self):
        """
        Create and run a query through a Backdoor Controller
        """
        BackdoorController(self.graph.copy()).run()

    # Generate and present a Joint Distribution Table

    def run_joint_distribution_table(self):
        """
        Create and show a Joint Distribution Table
        """
        self.cg.joint_distribution_table()

    # See a topological sort of the graph

    def run_topological_sort(self):
        """
        Create and show a topological sorting of the graph
        """
        self.cg.topological_sort()

    # See the 3 rules of Do-Calculus applied to some sets

    def run_do_calculus(self):
        """
        Enter a smaller IO stage in which we take 4 sets (X, Y, W, Z) and see which of the 3 do_calculus rules apply.
        """
        do_calculus(self.graph.copy())
