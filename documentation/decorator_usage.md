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
        function()

    return foo_wrapper

@foo
def bar():
    print("Bar!")
```

We can essentially "wrap" a function and its usage neatly around other, generalized, reusable code, allowing us to essentially "plug in" any function, without code copying.
An example usage as I have done in the ``utilities/Decorators.py`` module is decorators that allow for **timing** a function, as well as **debugging**.
