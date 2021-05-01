# -*- coding: utf-8 -*-

from .fetch import fetch
from .helpers import get_or_call, Loop

from itertools import chain
from concurrent.futures._base import TimeoutError
import asyncio

class Collector(object):
    """docstring for Collector2."""

    EXPIRE = 3600*24*7

    def __init__(self, url):
        """ Instantiate a new Collector object """
        super(Collector, self).__init__()
        self.url = url


def collect(*locations):
    with Loop() as loop:
        cc = Collector()
        res = loop.run_until_complete(cc.run(*locations))
    return res
