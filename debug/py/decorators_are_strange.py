

def do_it_twice(function):

    def wrap(*args, **kwargs):
        total = 0
        total += function(*args, **kwargs)
        total += function(*args, **kwargs)
        return total
    return wrap


def do_it_five_times(function):

    def wrap(*args, **kwargs):
        total = 0
        total += function(*args, **kwargs)
        total += function(*args, **kwargs)
        total += function(*args, **kwargs)
        total += function(*args, **kwargs)
        total += function(*args, **kwargs)
        return total

    return wrap


@do_it_twice
@do_it_five_times
def count(i: int):
    return i


print(count(1))
