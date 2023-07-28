def bar(x):
    return x * 2


def foo(x):
    return 100 * bar(x + 100)


def nonint(x):
    return bar(x)
