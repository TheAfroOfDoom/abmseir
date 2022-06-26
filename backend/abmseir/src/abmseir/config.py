###
# File: config.py
# Created: 01/23/2021
# Author: Jordan Williams (theafroofdoom@gmail.com)
# -----
# Last Modified: 06/04/2022
# Modified By: Jordan Williams
###

"""
Class that stores a dictionary object with attributes defined in `config.json`.
"""

# Modules
from .log_handler import logging as log
from pathlib import Path

# Packages
import json

# Attributes
settings = None


def load(s="load"):
    try:
        global settings
        fp = open(Path(__file__).parent / "./config/base.json", "r+")
        settings = json.load(fp)
        log.info("Config successfully " + s + "ed.")
    except (IOError, OSError) as e:
        log.exception("Failed to " + s + " config.")
        log.exception(e)
        raise e


def reload():
    load("reload")


def write():
    log.info("Config saved.")
    pass


# On initialization, load the config
load()
