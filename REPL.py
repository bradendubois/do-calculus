
from sys import stdin
from re import sub


def REPL_probability_parse(s):

    space = [',', '=']

    p = s

    for c in space:
        p = sub(c, " " + c + " ", p)

    p = sub(r'\s+', ' ', p)

    print(p)

REPL_probability_parse(stdin.read())