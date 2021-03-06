import _zephyr as _z
import os
import sys

from _zephyr import receive, ZNotice

__inited = False

is_py3 = sys.version_info.major >= 3

def init():
    global __inited
    if not __inited:
        _z.initialize()
        _z.openPort()
        _z.cancelSubs()
        __inited = True

def realm():
    return _z.realm()

class Subscriptions(set):
    """
    A set of <class, instance, recipient> tuples representing the
    tuples that have been subbed to

    Since subscriptions are shared across the entire process, this
    class is a singleton
    """
    def __new__(cls):
        if not '_instance' in cls.__dict__:
            cls._instance = super().__new__(cls)
            init()
        return cls._instance

    def __del__(self):
        _z.cancelSubs()

    def _fixTuple(self, item):
        if len(item) != 3:
            raise TypeError('item is not a zephyr subscription tuple')

        item = list(item)
        if item[2].startswith('*'):
            item[2] = item[2][1:]

        if '@' not in item[2]:
            item[2] += '@{}'.format(realm())

        return tuple(item)

    def add(self, item):
        item = self._fixTuple(item)

        if item in self:
            return

        _z.sub(*item)

        super().add(item)

    def sub_all(self, subsfile):
        """Subscribe to all subscriptions listed in subsfile"""
        with open(subsfile) as f:
            _z.subAll([l.rstrip('\n').split(',', 2) for l in f.readlines()])
        super().update(_z.getSubscriptions())

    def remove(self, item):
        item = self._fixTuple(item)

        if item not in self:
            raise KeyError(item)

        _z.unsub(*item)

        super().remove(item)
