# -*- coding: utf-8 -*-

from . import settings
from mptools.logger import package_logger

from . import __name__ as PACKAGENAME

logger = package_logger(PACKAGENAME, settings.LOGGERS)

T = lambda s: s

if settings.DB_URI is None:
    db = None
else:
    from py4web import DAL
    # connect to db
    db = DAL(settings.DB_URI,
        folder = settings.DB_FOLDER,
        pool_size = settings.DB_POOL_SIZE,
        migrate = settings.DB_MIGRATE,
        lazy_tables=False, check_reserved=False
    )
