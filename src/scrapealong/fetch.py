# -*- coding: utf-8 -*-

from . import settings
from .common import logger
from .helpers import Loop

import aiohttp
from bs4 import BeautifulSoup
import asyncio
import re

from pyppeteer import launch
from pyppeteer.errors import ElementHandleError
from pyppeteer.errors import TimeoutError
# import logging
from mptools.timeformat import prettydelta
import datetime
# from .froxyWrapper import loopOproxies
# from .proxyscrapeWrapper import loopOproxies

FETCH_TIMEOUT = 25.
BROWSE_TIMEOUT = 25000
RETRY_WITHIN = 25

# # create logger
# logger = logging.getLogger(__name__)
#
#
# ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)
#
# logger.addHandler(ch)
#
# logger.setLevel(logging.DEBUG)

def timeit(func):
    async def wrapper(url, *args, **kwargs):
        assert asyncio.iscoroutinefunction(func)
        # logger.info(f"Used method: {func.__name__}")
        # logger.info(f"Calling url: {url}")
        start = datetime.datetime.now()
        result = await func(url, *args, **kwargs)
        end = datetime.datetime.now()
        elapsed = prettydelta(end-start, use_suffix=False)
        logger.debug(f"""Using method {func.__name__} called url: {url}
Download time: {elapsed}""")
        # logger.info(f"Elapsed time: {elapsed}")
        return result
    return wrapper

parser = lambda body: BeautifulSoup(body, "html.parser")

@timeit
async def fetchOldButGold(url, retry=5):
    """ Fetches the given url and return the parsed page body
    DOC:
        * https://www.crummy.com/software/BeautifulSoup/bs4/doc/
    """
    timeout = aiohttp.ClientTimeout(total=FETCH_TIMEOUT)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        for tt in range(retry):
            try:
                async with session.get(url) as response:
                    if response.status>=400:
                        raise Exception(response.status)
                    body = await response.text()
            except (aiohttp.ClientConnectorError, asyncio.TimeoutError) as err:
                logger.debug(f"Called URL: {url} - {tt}/{retry}")
                if tt < retry-1:
                    await asyncio.sleep(RETRY_WITHIN)
                    continue
                else:
                    raise
            else:
                # if response.status>=400:
                #     if tt < retry-1:
                #         await asyncio.sleep(RETRY_WITHIN)
                #         continue
                #     raise Exception(response.status)
                break

    return parser(body)

fetch = fetchOldButGold

@timeit
async def browse(url, retry=3):
    """ DEPRECATED """

    info = {}

    browser = await launch()
    page = await browser.newPage()

    for tt in range(retry):
        try:
            res_ = await page.goto(url, timeout=BROWSE_TIMEOUT)
        except TimeoutError as err:
            if tt < retry-1:
                await asyncio.sleep(RETRY_WITHIN)
                continue
            else:
                raise err
        else:
            # body = await res_.text()
            body = await page.content()
            break

    try:
        # This code get longitude and latitude information for *tripadvisor* pages only
        span = await page.evaluate('''() => {
            var elem = document.querySelector('[data-test-target="staticMapSnapshot"]');
            return elem.outerHTML
        }''')
    except ElementHandleError:
        lon_lat = None
    else:
        center_ = re.search(';center=.*?\&', span)
        if not center_ is None:
            lon_lat = list(map(float, center_.group()[8:-1].split(',')))[::-1]
        else:
            lon_lat = None

    await browser.close()

    return lon_lat, parser(body), url,

class SlowFetcher(object):
    """docstring for SlowFetcher."""

    def __init__(self, QUEUE_LENGTH=settings.QUEUE_LENGTH):
        super(SlowFetcher, self).__init__()
        self.semaphoro = asyncio.Semaphore(QUEUE_LENGTH)

    async def fetch(self, url):
        async with self.semaphoro:
            response = await fetch(url)
        return response

    def __call__(self, *args, **kwargs):
        with Loop() as loop:
            res = loop.run_until_complete(self.fetch(*args, **kwargs))
        return res

    # async def browse(self, url):
    #     async with self.semaphoro:
    #         response = await browse(url)
    #     return response
