""" Singleton class

:author: Michel Bierlaire
:date: Sat Jul 18 16:45:35 2020

"""


class Singleton(type):
    """
    A singleton is a class with only one instance
    """

    _instances = {}

    def __call__(self, *args, **kwargs):
        if self not in self._instances:
            self._instances[self] = super(Singleton, self).__call__(*args, **kwargs)
        return self._instances[self]
