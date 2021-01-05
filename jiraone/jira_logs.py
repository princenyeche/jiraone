#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A logging handler file, which helps in providing logs of the script execution."""
from logging.handlers import RotatingFileHandler
from datetime import datetime
from platform import system
import logging
import os

WORK_PATH = os.path.abspath(os.getcwd())
now = datetime.now()
LOGGER = ""

logger = logging.getLogger(__name__)
formatting = logging.Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")

if system() == "Linux" or system() == "Darwin":
    LOGGER += WORK_PATH + "{}".format("/logs")
    if not os.path.exists(LOGGER):
        os.mkdir(LOGGER)
    handler = RotatingFileHandler("{}/{}".format(LOGGER, "app.log"), maxBytes=1000000, backupCount=20)
    handler.setFormatter(formatting)
    logger.addHandler(handler)

if system() == "Windows":
    LOGGER += WORK_PATH + "{}".format("\\logs")
    if not os.path.exists(LOGGER):
        os.mkdir(LOGGER)
    handler = RotatingFileHandler("{}\\{}".format(LOGGER, "app.log"), maxBytes=1000000, backupCount=20)
    handler.setFormatter(formatting)
    logger.addHandler(handler)


def add_log(message, level):
    """Writes a log to a log file with activity done."""
    if level == "debug".lower():
        logger.setLevel(logging.DEBUG)
        logger.debug(message)
    elif level == "error".lower():
        logger.setLevel(logging.ERROR)
        logger.error(message)
    else:
        logger.setLevel(logging.INFO)
        logger.info(message)
