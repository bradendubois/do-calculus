from itertools import product

from do.identification.Identification import Identification, simplify_expression
from do.identification.LatentGraph import LatentGraph
from do.identification.PExpression import PExpression, TemplateExpression


def parse_graph_string(graph_string: str) -> LatentGraph:

    from re import split

    arrows = ["<->", "<-", "->"]

    splits = graph_string.strip().split(".")[:-1]
    print(splits)

    e = set()
    v = set()
    e_b = set()

    for item in splits:

        # This would be an item like "X." or "X,Y". in which the vertices exist, but don't have any edges.
        if not any(arrow in item for arrow in arrows):
            v.update(item.split(","))

        parse = split(f'({"|".join(arrows)})', item)

        for i in range(1, len(parse), 2):

            # Left and Right are comma-separated lists of values, arrow being the "->" -style arrow joining them.
            left, arrow, right = parse[i-1].split(","), parse[i], parse[i+1].split(",")

            # Add all vertices into V
            v.update(left)
            v.update(right)

            for s, t in product(left, right):

                if arrow == "<-":
                    e.add((t, s))

                elif arrow == "->":
                    e.add((s, t))

                elif arrow == "<->":
                    e_b.add((s, t))

                else:
                    print("Invalid Arrow Type:", arrow)

    return LatentGraph(v, e, e_b)


#########################################
# graph 1
#########################################

g_1 = LatentGraph({'C', 'S', 'M'}, {('M', 'S'), ('S', 'C'), ('M', 'C')}, set())
g_1_string = "M->S.S,M->C."

g1_q1 = ({'C'}, {'S'})
g1_q2 = ({'C'}, {'M'})
g1_q3 = ({'C'}, {'S', 'M'})

g1_a1 = "C | S = <sum {M} [C|M,S] [M] >"
g1_a2 = "C | M = <sum {S} [C|M,S] [S|M] >"
g1_a3 = "C | S, M = [C|M,S]"

g1_queries = [g1_q1, g1_q2, g1_q3]
g1_answers = [g1_a1, g1_a2, g1_a3]



#########################################
# queries - graph 2
#########################################

g_2 = LatentGraph({'A', 'B', 'C', 'D'}, {('A', 'B'), ('A', 'C'), ('B', 'D'), ('C', 'D')}, set())
g_2_string = "A->B,C.B,C->D."

g2_q1 = ({'D'}, {'A'})
g2_q2 = ({'D'}, {'B'})
g2_q3 = ({'D'}, {'C'})
g2_q4 = ({'D'}, {'B', 'C'})

g2_a1 = "D | A = <sum {C, B} [D|A,B,C] [C|A] [B|A] >"
g2_a2 = "D | B = <sum {C, A} [C|A] [A] [D|A,B,C] >"
g2_a3 = "D | C = <sum {A, B} [D|A,B,C] [B|A] [A] >"
g2_a4 = "D | C, B = [D|A,B,C]"

g2_queries = [g2_q1, g2_q2, g2_q3, g2_q4]
g2_answers = [g2_a1, g2_a2, g2_a3, g2_a4]

#########################################
# queries - graph 3
#########################################

g_3 = LatentGraph({'B', 'C', 'D'}, {('B', 'D'), ('C', 'D')}, {('B', 'C')})
g_3_string = "B<->C.B,C->D."

g3_q1 = ({'D'}, {'B'})
g3_q2 = ({'D'}, {'C'})
g3_q3 = ({'D'}, {'B', 'C'})

g3_a1 = "D | B = <sum {C} [C] [D|B,C] >"
g3_a2 = "D | C = <sum {B} [D|B,C] [B] >"
g3_a3 = "D | C, B = [D|B,C]"

g3_queries = [g3_q1, g3_q2, g3_q3]
g3_answers = [g3_a1, g3_a2, g3_a3]

#########################################
# queries - graph 4
#########################################

g_4 = LatentGraph({'S', 'T', 'C'}, {('S', 'T'), ('T', 'C')}, {('S', 'C')})
g_4_string = "S->T->C.S<->C."

g4_q1 = ({'C'}, {'S'})

g4_a1 = "C | S = <sum {T} [T|S] ><sum {S} [C|S,T] [S] >"

g4_queries = [g4_q1]
g4_answers = [g4_a1]

#########################################
# queries - graph 5
#########################################

g_5 = LatentGraph({"X", "Y", "Z1", "Z2", "Z3"},
    {("Z1", "Z2"), ("X", "Z2"), ("Z2", "Z3"), ("X", "Y"), ("Z2", "Y"), ("Z3", "Y")}, {("X", "Z1"), ("Z1", "Z3")}
)
g_5_string = "X<->Z1<->Z3.X,Z1->Z2->Z3.X,Z2,Z3->Y."

g5_q1 = ({"Y"}, {"X"})      # paper: Sum_{X} [P(Z3 | Z2, Z1, X), P(Z1 | X), P(X)]
g5_q2 = ({"Y"}, {"X", "Z1", "Z2", "Z3"})

g5_a1 = "Y | X = <sum {Z2, Z1, Z3} [Y|X,Z2,Z3] [Z2|X,Z1] ><sum {X} [Z3|Z1,X,Z2] [Z1|X] [X] >"
g5_a2 = "Y | Z2, Z1, X, Z3 = [Y|X,Z2,Z3]"

g5_queries = [g5_q1, g5_q2]
g5_answers = [g5_a1, g5_a2]

#########################################
# queries - graph 6
#########################################

g_6 = LatentGraph({"X", "Y1", "Y2", "W1", "W2"},
    {("W1", "X"), ("X", "Y1"), ("W2", "Y2")}, {("W1", "W2"), ("W1", "Y1"), ("W2", "X")}
)
g_6_string = "Y1<->W1<->W2<->X.W1->X->Y1.W2->Y2."

g6_q1 = ({"Y1", "Y2"}, {"X"})
g6_a1 = "Y2, Y1 | X = <sum {W2} [Y2|W2] > [W2] <sum {W1} [Y1|W1,X] [W1] >"

g6_queries = [g6_q1]
g6_answers = [g6_a1]

#########################################
# queries - graph 7
#########################################

g_7 = LatentGraph({"Z1", "Z2", "W", "X", "Y"},
    {("Z2", "X"), ("X", "W"), ("W", "Y"), ("Z1", "Y")}, {("Z1", "Z2"), ("Z2", "W"), ("Z1", "W")}
)
g_7_string = "Z1<->Z2<->W<->Z1.Z2->X->W->Y<-Z1."

g7_q1 = ({"Y"}, {"X"})
g7_a1 = "Y | X = <sum {Z1, W} [Y|Z1,Z2,X,W] ><sum {Z2} [W|Z2,Z1,X] [Z2|Z1] [Z1] >"

g7_queries = [g7_q1]
g7_answers = [g7_a1]

#########################################
# queries - graph 8
#########################################

g_8 = LatentGraph({'S1', 'T1', 'C1', 'S2', 'T2', 'C2', 'C'}, {('S1', 'T1'), ('T1', 'C1'), ('S2', 'T2'), ('T2', 'C2'), ('C2', 'C'), ('C1', 'C')}, {('S1', 'C1'), ('S2', 'C2')})

g_8_string = "S1->T1->C1<->S1.S2->T2->C2<->S2.C2->C<-C1."

g8_q1 = ({'C1'}, {'S1'})
g8_q2 = ({'C2'}, {'S2'})
g8_q3 = ({'C1', 'C2'}, {'S1', 'S2'})
g8_q4 = ({'C'}, {'S1', 'S2'})

g8_a1 = "<sum {T1} [T1|S1] <sum {S1} [C1|S1,T1] [S1] >>"
g8_a2 = "<sum {T2} [T2|S2] <sum {S2} [C2|S2,T2] [S2] >>"
g8_a3 = "<sum {T2} [T2|S2] <sum {T1} [T1|S1] ><sum {S1} [C1|S1,T1] [S1] ><sum {S2} [C2|S2,T2] [S2]>>"
g8_a4 = "<sum {C1, C2} [C|C1,C2] <sum {T1} [T1|S1] ><sum {T2} [T2|S2] <sum {S1} [C1|S1,T1] [S1] ><sum {S2} [C2|S2,T2] [S2] >>"

g8_queries = [g8_q1, g8_q2, g8_q3, g8_q4]
g8_answers = [g8_a1, g8_a2, g8_a3, g8_a4]

#########################################

all_tests = [
    {
        "queries": g1_queries,
        "answers": g1_answers,
        "g": g_1,
        "as_string": g_1_string,
    }, {
        "queries": g2_queries,
        "answers": g2_answers,
        "g": g_2,
        "as_string": g_2_string,
    }, {
        "queries": g3_queries,
        "answers": g3_answers,
        "g": g_3,
        "as_string": g_3_string,
    }, {
        "queries": g4_queries,
        "answers": g4_answers,
        "g": g_4,
        "as_string": g_4_string,
    }, {
        "queries": g5_queries,
        "answers": g5_answers,
        "g": g_5,
        "as_string": g_5_string,
    }, {
        "queries": g6_queries,
        "answers": g6_answers,
        "g": g_6,
        "as_string": g_6_string,
    }, {
        "queries": g7_queries,
        "answers": g7_answers,
        "g": g_7,
        "as_string": g_7_string,
    }, {
        "queries": g8_queries,
        "answers": g8_answers,
        "g": g_8,
        "as_string": g_8_string,
    }
]


def test_GraphParse1():
    assert g_1 == parse_graph_string(g_1_string)

def test_GraphParse2():
    assert g_2 == parse_graph_string(g_2_string)

def test_GraphParse3():
    assert g_3 == parse_graph_string(g_3_string)

def test_GraphParse4():
    assert g_4 == parse_graph_string(g_4_string)

def test_GraphParse5():
    assert g_5 == parse_graph_string(g_5_string)

def test_GraphParse6():
    assert g_6 == parse_graph_string(g_6_string)

def test_GraphParse7():
    assert g_7 == parse_graph_string(g_7_string)

def test_GraphParse8():
    assert g_8 == parse_graph_string(g_8_string)


def tests():

    for index, problem_set in enumerate(all_tests, start=1):

        print("*" * 20, f"Beginning Graph {index}", "*" * 20)

        g = problem_set["g"]
        p = PExpression([], [TemplateExpression(x, list(g.parents(x))) for x in g.V])

        # Verify Graph-Parsing
        g_str = problem_set["as_string"]

        print(f"Graph String: {index}")
        print(g_str)
        parsed = parse_graph_string(g_str)

        print("Original:", g)
        print("  Parsed:", parsed)
        assert g == parsed

        # Verify ID
        for i, (query, answer) in enumerate(zip(problem_set["queries"], problem_set["answers"]), start=1):

            y, x = query

            query_str = f"{', '.join(y)} | {', '.join(x)}"
            print(f"Beginning problem ({i}): {query_str}")
            result = Identification(y, x, p, g, True)
            simplify = simplify_expression(result, g)

            print("*********** Proof")
            print(result.proof())

            print("*********** Proof (Simplified)")
            print(simplify.proof())
