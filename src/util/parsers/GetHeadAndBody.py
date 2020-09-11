#########################################################
#                                                       #
#   Get Head and Body                                   #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################


from probability_structures.VariableStructures import *

error_msg_formatting = \
        "The given data is incorrect:\n" + \
        " - Some outcome may not be possible for some variable\n" + \
        " - Some variable may not be defined"


def get_valid_head_and_body(head_prompt: str, body_prompt: str, variables: list, outcomes: dict) -> (list, list):
    """
    Get the head and body for a probability query, validating any input data
    :param head_prompt: The prompt to present when getting the Head list
    :param body_prompt: The prompt to present when getting the Body lst
    :param variables: The list of variables in the graph
    :param outcomes: The mapping of variable name to a list of valid outcomes
    :return a tuple (head, body)
    """

    # Need an outcome to query, not necessarily any given data though
    head_preprocessed = input(head_prompt)
    assert head_preprocessed != "", "No query being made; the head should not be empty."
    head = parse_outcomes_and_interventions(head_preprocessed)
    for out in head:  # Ensure there are no adjustments in the head
        assert not isinstance(out, Intervention), "Don't put adjustments in the head."

    # Get optional "given" data and process it
    body = []
    body_preprocessed = input(body_prompt)
    if body_preprocessed != "":
        body = parse_outcomes_and_interventions(body_preprocessed)

    # Validate the queried variable and any given
    for out in head + body:
        # Ensure variable is defined, outcome is possible for that variable, and it's formatted right.
        assert out.name in variables and out.outcome in outcomes[out.name], error_msg_formatting

    return head, body
