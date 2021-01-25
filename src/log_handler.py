###
# File: log_handler.py
# Created: 01/23/2021
# Author: Jordan Williams (jwilliams13@umassd.edu)
# -----
# Last Modified: 01/25/2021
# Modified By: Jordan Williams
###

"""
Initializes the logging object with specific parameters.
Rotates the pre-existing latest.log into a log with its file name representing its creation date.
"""

# Packages
import datetime
import logging
import os
import platform
import time
from win32_setctime import setctime

def create_new_latest_log(path):
    # Create new latest.log
    f = open(path + 'latest.log', 'x')
    
    # Update creation time (stupid file system tunneling crap)
    if(platform.system() == 'Windows'):
        setctime(path + 'latest.log', time.time())

    f.close()

def rotate_latest_log(path):
    os_stats = os.stat(path + 'latest.log')
    if  (platform.system() == 'Windows'):
        creation_time = datetime.datetime.fromtimestamp(os_stats.st_ctime)
    elif(platform.system() == 'Darwin'): # macOS
        creation_time = datetime.datetime.fromtimestamp(os_stats.st_birthtime)
    elif(platform.system() == 'Linux'):
        # Creation time is impossible on Linux; use last modified time instead
        creation_time = datetime.datetime.fromtimestamp(os_stats.st_mtime)
    else:
        logging.error('platform.system() not identified: %s' % (platform.system()))

    try:
        # Rename old latest.log to <creation_date>.log (YYYY-MM-DDTHHmmss)
        os.rename(path + 'latest.log', '%s%s.log' % (path, creation_time.strftime('%Y-%m-%dT%H%M%S')))
    except FileExistsError as e:
        # TODO(jordan): If log file already exists with same name (in the same second), name the new file to <creation_time>_<index>.log
        # where <index> is 1, 2, 3, ...
        raise e
        pass

    # New latest.log
    create_new_latest_log(path)

# Determine where latest.log resides relative to current working directory
path = './logs/'
# If file exists one directory deep into ./logs
if(os.path.exists('./logs/latest.log')):
    # Rotate latest.log to <creation_date>.log
    rotate_latest_log(path)
# Else, no logs/latest.log found. Create one in /logs directory from CWD.
else:
    # Create dir if it doesn't exist
    if(not os.path.isdir('./logs')):
        os.mkdir('./logs')

    # New latest.log
    create_new_latest_log(path)


# Initialize logging object
logging.basicConfig(
    filename = path + 'latest.log'
    , level = logging.INFO  # NOTE(jordan): Change log detail level here
    , format = '%(asctime)s.%(msecs)03d:%(levelname)s: %(message)s'
    , datefmt = '%Y-%m-%d %H:%M:%S'
)
logging.getLogger().addHandler(logging.StreamHandler())