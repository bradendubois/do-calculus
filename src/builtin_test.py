#! /usr/bin/env python

class B:

    def __init__(self):
        pass


class A:

    def __init__(self):
        pass

    def __eq__(self, other):
        if isinstance(other, B):
            return True
        return False


print([] == A())
print(B() == A())
