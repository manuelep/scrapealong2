# -*- coding: utf-8 -*-

from .helpers import Loop
from .common import logger

import asyncio
import aiohttp
from pyppeteer import launch
import pyppeteer.errors
from bs4 import BeautifulSoup
import traceback

from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
import selenium.common.exceptions

FETCH_TIMEOUT = 25.
BROWSE_TIMEOUT = 25000
RETRY_WITHIN = 8

parser = lambda body: BeautifulSoup(body, "html.parser")

import functools

def force_async(fn):
    ''' Courtesy of: https://gist.github.com/phizaz/20c36c6734878c6ec053245a477572ec
    turns a sync function to async function using threads
    '''
    from concurrent.futures import ThreadPoolExecutor
    import asyncio
    pool = ThreadPoolExecutor()

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        future = pool.submit(fn, *args, **kwargs)
        return asyncio.wrap_future(future)  # make it awaitable

    return wrapper

class ScrapeError(object):
    """docstring for ScrapeError."""

    def __init__(self, key, *args, **kw):
        super(ScrapeError, self).__init__(*args, **kw)
        self.key = key


class BasePicker(object):
    """docstring for BasePicker."""

    def __call__(self, *args, **kwargs):
        with Loop() as loop:
            res = loop.run_until_complete(self.run(*args, **kwargs))
        return res

    async def run(self):
        """ """
        raise NotImplementedError()

fetch_semaphoro = asyncio.Semaphore(10)
browse_semaphoro = asyncio.Semaphore(1)

class BaseBrowser(object):
    """docstring for BaseBrowser."""

    def __init__(self, url):
        super(BaseBrowser, self).__init__()
        self.url = url
        # self.lon_lat = None

    @staticmethod
    async def _page_callback(page):
        """  """
        raise NotImplementedError

    def __call__(self):
        """ """
        raise NotImplementedError

    def _load(self):
        """  """
        raise NotImplementedError

    async def _fetch(self, retry=5):
        """ Fetches the given url and return the parsed page body
        DOC:
            * https://www.crummy.com/software/BeautifulSoup/bs4/doc/
        """
        timeout = aiohttp.ClientTimeout(total=FETCH_TIMEOUT)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            for tt in range(1, retry+1):
                async with fetch_semaphoro:
                    try:
                        async with session.get(self.url) as response:
                            body = await response.text()
                    except (aiohttp.ClientConnectorError, asyncio.TimeoutError) as err:
                        if tt < retry:
                            logger.warning(err)
                            logger.info(f"Attempt {tt} failed. Fetch will be retryed within {RETRY_WITHIN} sec")
                            logger.info(self.url)
                            await asyncio.sleep(RETRY_WITHIN)
                            continue
                        else:
                            logger.warning(f"Attempt {tt} failed")
                            logger.error(err)
                            # raise
                            return
                    else:
                        self.status = response.status
                        if response.status>=400:
                            return
                        break

        self._body = body
        self._load()

    async def _seleniumBrowse(self, retry=5):
        """
        """

        opts = Options()
        opts.set_headless()
        browser = Firefox(options=opts, timeout=FETCH_TIMEOUT)

        @force_async
        def calll_url():
            browser.get(self.url)

        for tt in range(1, retry+1):
            try:
                res = await calll_url()
            except selenium.common.exceptions.TimeoutException as err:
                if tt < retry:
                    logger.warning(err)
                    logger.info(f"Attempt {tt} failed. Fetch will be retryed within {RETRY_WITHIN} sec")
                    logger.info(self.url)
                    await asyncio.sleep(RETRY_WITHIN)
                    continue
                else:
                    logger.warning(f"Attempt {tt} failed")
                    logger.error(err)
                    break
            else:
                html = browser.find_element_by_tag_name('html')
                self._body = html.get_attribute('outerHTML')
                break


    async def _browse(self, retry=5):
        """

        TODO: Test other solutions like:
            - https://github.com/HDE/arsenic
            - https://realpython.com/modern-web-automation-with-python-and-selenium/
        """

        async with browse_semaphoro:

            for tt in range(1, retry+1):
                try:
                    browser = await launch()
                    page = await browser.newPage()
                    response = await page.goto(self.url, timeout=BROWSE_TIMEOUT)
                except pyppeteer.errors.TimeoutError as err:
                    if tt < retry:
                        logger.warning(err)
                        logger.info(f"Attempt {tt} failed. Fetch will be retryed within {RETRY_WITHIN} sec")
                        logger.info(self.url)
                        await page.close()
                        await browser.close()
                        await asyncio.sleep(RETRY_WITHIN)
                        continue
                    else:
                        logger.warning(f"Attempt {tt} failed")
                        logger.error(err)
                        await page.close()
                        await browser.close()
                        break
                        # raise
                except pyppeteer.errors.BrowserError as err:
                    logger.critical(err)
                    logger.error(traceback.format_exc())
                    continue
                except pyppeteer.errors.PageError as err:
                    logger.critical(err)
                    logger.error(traceback.format_exc())
                    continue
                else:
                    self.status = response.status
                    if response.status>=400:
                        logger.critical(response.status)
                        return
                    else:
                        try:
                            await self._page_callback(page)
                        except NotImplementedError:
                            pass
                    self._body = await page.content()
                    await page.close()
                    await browser.close()
                    try:
                        self._load()
                    except NotImplementedError:
                        pass
                    break

    @property
    def body(self):
        return parser(self._body)
