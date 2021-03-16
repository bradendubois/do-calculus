#########################################################
#                                                       #
#   Expressions                                         #
#                                                       #
#   Author: Braden Dubois (braden.dubois@usask.ca)      #
#   Written for: Dr. Eric Neufeld                       #
#                                                       #
#########################################################

from src.probability.shpitser.structures.Distribution import Distribution

# A representation of Summation / Product symbols for use in Shpitser


class Symbol:

    def __init__(self, s, exp, symbol):
        self.symbol = symbol
        self.s = s
        self.exp = exp

    def __str__(self):

        rep = ""
        if self.s is not None and len(self.s) > 0:
            s = self.s
            if isinstance(s, set):
                s = list(s)
            for i in range(len(s)):
                if not isinstance(i, str):
                    s[i] = "[" + ", ".join(list(s[i])) + "]"

            rep += self.symbol + "_[" + ", ".join(self.s) + "] "

        if isinstance(self.exp, list):
            if len(self.exp) > 1:
                rep += "["
            for item in self.exp:
                if isinstance(item, Symbol) or isinstance(item, Distribution):
                    rep += str(item) + (", " if len(self.exp) > 1 else "")
                else:
                    print("CONFUSED: ", type(item))
            if len(self.exp) > 1:
                rep += "]"
        else:
            rep += str(self.exp)

        return rep


class SigmaObj(Symbol):

    def __init__(self, s, exp):
        super().__init__(s, exp, "Sigma")


class PiObj(Symbol):

    def __init__(self, s, exp):
        super().__init__(s, exp, "Pi")
