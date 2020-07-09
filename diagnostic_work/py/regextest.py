import re

from probability_structures.VariableStructures import Intervention, Outcome





result = parse_outcomes_and_interventions("Y=blah do(X = x, Y=y, Z =z), do(A = a , B=b,   C=c), X=blah")
print(str([str(item) for item in result]))