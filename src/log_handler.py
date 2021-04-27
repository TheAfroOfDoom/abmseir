###
# File: log_handler.py
# Created: 01/23/2021
# Author: Jordan Williams (jwilliams13@umassd.edu)
# -----
# Last Modified: 04/26/2021
# Modified By: Jordan Williams
###

"""
Initializes the logging object with specific parameters.
Rotates the pre-existing latest.log into a log with its file name representing its creation date.
"""

# Packages
import datetime
import itertools
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

def unique_file(basename, ext):
    '''https://stackoverflow.com/a/33691348/13789724
    '''
    actualname = "%s.%s" % (basename, ext)
    c = itertools.count()
    while os.path.exists(actualname):
        actualname = "%s_%d.%s" % (basename, next(c), ext)
    return(actualname)

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

    creation_time_formatted = creation_time.strftime('%Y-%m-%dT%H%M%S') # type: ignore
    file_name = unique_file(path + creation_time_formatted, 'log')
    
    # Rename old latest.log to <creation_date>.log (YYYY-MM-DDTHHmmss)
    os.rename(path + 'latest.log', file_name)

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
    #create_new_latest_log(path)

# Get current time
current_time = datetime.datetime.now()

# Initialize logging object
logging.basicConfig(
    filename = path + current_time.strftime('%Y-%m-%dT%H%M%S') + '.log'
    , level = logging.INFO  # NOTE(jordan): Change log detail level here
    , format = '%(asctime)s.%(msecs)03d:%(levelname)s: %(message)s'
    , datefmt = '%Y-%m-%d %H:%M:%S'
)
logging.getLogger().addHandler(logging.StreamHandler())