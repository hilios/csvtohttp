HEADER = r"""
____ ____ _  _    ___ ____    _  _ ___ ___ ___
|    [__  |  |     |  |  |    |__|  |   |  |__]
|___ ___]  \/      |  |__|    |  |  |   |  |
"""


TEMPLATE_HELPERS = {
    'upper': lambda _, value: value.upper(),
    'lower': lambda _, value: value.lower(),
    'first': lambda _, value: value[0],
}
