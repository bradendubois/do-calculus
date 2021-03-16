#########################################################
#                                                       #
#   Shpitser                                            #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

from src.probability.shpitser.identification.IDAlgorithm import ID
from src.probability.shpitser.identification.IDProcessing import parse_shpitser
from src.probability.shpitser.latent.LatentProjection import latent_projection
from src.probability.shpitser.structures.Distribution import Distribution

from src.probability.structures.CausalGraph import CausalGraph

# TODO Deprecated; Incorporate into the new REPL system

########################
#     Shpitser REPL    #
########################


def shpitser_repl(cg: CausalGraph):
    """
    Enter a main REPL area allowing the application of Shpitser
    :param cg: The CausalGraph for the loaded model
    """

    comma_prompt = "\nPlease enter as a comma-separated list of values."
    example = "Ex: 'B, Xi, T'\nInput: "
    sub = "\n  " + comma_prompt + "\n" + "  " + example

    y_prompt = "Please enter the head, Y:" + sub
    x_prompt = "Please enter the interventions, X:" + sub
    u_prompt = "Please enter all unobservable variables, U:" + sub

    identification = None
    known = dict()

    while True:

        try:

            if identification:
                print("\nCurrent expression:", identification)
                print()

            options = ["Query a distribution with Shpitser & Pearl"]
            if identification:
                options.append("Process current expression")
            options.append("Return")

            selection = user_index_selection("Select an Option:", options)

            if selection == 0:
                known.clear()
                identification = None

                y = input(y_prompt).split(",")
                x = input(x_prompt).split(",")
                u = input(u_prompt).split(",")

                y = [v.strip() for v in y if v]
                x = [v.strip() for v in x if v]
                u = [v.strip() for v in u if v]

                for v in y:
                    assert v in cg.outcomes

                for v in x:
                    assert v in cg.outcomes

                for v in u:
                    assert v in cg.outcomes

                u = set(u)

                y = set(y)
                x = set(x)
                p = Distribution(cg.tables)
                g = latent_projection(cg.graph, u)

                print(cg.graph, g)

                identification = ID(set(y), set(x), p, g)

            elif options[selection] == "Return":
                return

            else:
                result = parse_shpitser(identification, cg, known)
                print("\nResult:", result)
                identification = None

        except AssertionError:
            print("Error: Some variable is not defined in the graph.")
