# -*- coding: utf-8 -*-

import pathlib
import os


class Config(object):
    PROJECT_ROOT = pathlib.Path(__file__).parent.parent.absolute()
    SECRET_KEY = os.getenv("SECRET_KEY")
    MAPBOX_TOKEN = os.getenv("MAPBOX_TOKEN")
    TEMP_DIR = os.getenv("TEMP_DIR", PROJECT_ROOT / "tmp")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 1024 * 1024 * 16))
    FILE_TIME_LIMIT = os.getenv("FILE_TIME_LIMIT", False)


class DevelopmentConfig(Config):
    FILE_TIME_LIMIT = 30
    DEBUG = True
    WTF_CSRF_ENABLED = False


class TestConfig(Config):
    TESTING = True
