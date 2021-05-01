# -*- coding: utf-8 -*-

import os
from pathlib import Path
from . import __name__ as PACKAGENAME

PAGINATE = 30
PAGINATION_PREFIX = 'oa'

HOME = str(Path.home())

LIB_FOLDER = os.path.dirname(__file__)
LIB_NAME = os.path.split(LIB_FOLDER)[-1]

# db settings
APP_FOLDER = HOME

# DB_FOLDER:    Sets the place where migration files will be created
#               and is the store location for SQLite databases
DB_FOLDER = os.path.join(APP_FOLDER, "databases")
DB_URI = f"sqlite://{LIB_NAME}_temporary.db"
DB_POOL_SIZE = 10
DB_MIGRATE = True
# DB_FAKE_MIGRATE = False  # maybe?

# location where to store uploaded files:
# UPLOAD_FOLDER = os.path.join(APP_FOLDER, "uploads")

# logger settings
LOGGERS = [
    "info:stdout"
]  # syntax "severity:filename" filename can be stderr or stdout

QUEUE_LENGTH = 10

CACHE_LIFE = 120

# try import private settings
try:
    from .settings_private import *
except ModuleNotFoundError:
    pass
