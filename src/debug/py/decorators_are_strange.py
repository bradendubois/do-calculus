from random import randint

def do_it(function):

    def wrap(*args, **kwargs):
        return function(*args, **kwargs) + randint(-1, 1)

    return wrap


def do_it_twice(function):

    def wrap(*args, **kwargs):
        total = 0
        total += function(*args, **kwargs) + randint(-1, 1)
        total += function(*args, **kwargs) + randint(-1, 1)
        return total
    return wrap


def do_it_five_times(function):

    def wrap(*args, **kwargs):
        total = 0
        total += function(*args, **kwargs) + randint(-1, 1)
        total += function(*args, **kwargs) + randint(-1, 1)
        total += function(*args, **kwargs) + randint(-1, 1)
        total += function(*args, **kwargs) + randint(-1, 1)
        total += function(*args, **kwargs) + randint(-1, 1)
        return total

    return wrap


@do_it
@do_it_twice
@do_it_five_times
def count(i: int):
    return i


print(count(1))
