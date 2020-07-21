# Decorator Usage

A quick intro on how to use the "decorators" of Python, in particular in this project.

They seem like a very advanced concept (I don't know if I understand them completely), and they expose the more "functional programming" side of Python.

A handy guide (that I have been following myself) is here: [realpython.com/primer-on-python-decorators](https://realpython.com/primer-on-python-decorators/)

## Decorators

First, a decorator is the ``@foo`` in the following example:

```python
@foo
def bar():
    print("bar!")
```

The usage of a decorator, is an abstraction of a "function wrapper". For example, we can do the following:

```python
def foo(function):
    print("Foo!")
    function()

def bar():
    print("Bar!")

foo(bar)
```

And our output will be:

```
> "Foo!"
> "Bar!"
```

To create an equivalent decorator, we can do:

```python
def foo(function):

    def foo_wrapper(*args, **kwargs):
        print("Foo!")
        function(*args, **kwargs)

    return foo_wrapper

@foo
def bar():
    print("Bar!")
```

We can essentially "wrap" a function and its usage neatly around other, generalized, reusable code, allowing us to essentially "plug in" any function, without code copying.
An example usage as I have done in the ``utilities/Decorators.py`` module is decorators that allow for **timing** a function, as well as **debugging**.

This part of the software is a bit complicated, and it can generally be ignored.

### How do I use them?

There's currently two decorators that have been sufficient for development purposes, ``@time`` and ``@debug``.

Consider the following function:

```py
def slow(*args):
    print("I'm a slow function. Maybe.")
    # do some stuff...
```

If I want to see how long it takes, I could always save the current time, call it, check the new time, compare, etc.

```py
current_time = time()
slow("Blah!")
end_time = time()
taken = end_time - current_time
```

An easier way is to find the actual definition of the function, and simply add the decorator ``@time`` above it.

```python
@time
def slow(*args):
    print("I'm a slow function. Maybe.")
    # do some stuff...
```

And now, simply run whatever code already uses slow, and any time slow is called and completes its body, the following information will be printed in the console:

```
slow completed in: <time>.
```

Similarly, the ``@debug`` decorator can be used to profile a function call and its result.

```python
@debug
def slow(*args):
    print("I'm a slow function. Maybe.")
    # do some stuff...
```

Calling ``slow("Blah!")`` now will likely print information similar to as follows in the console:

```
slow called with "Blah!", returned "Foo!"
```

This can be especially useful in debugging / profiling development without actually changing any of the code to do the analyzing.
