#!/usr/bin/python
## @package RAID5.frontend.__main__
# Main module that runs the Frontend Server
#

import argparse
import ConfigParser
import errno
import logging
import os
import signal
import traceback

from utilities import async_server
from utilities import poller
from utilities import constants

if not hasattr(os, 'O_BINARY'):
    os.O_BINARY = 0

## Poll types
POLL_TYPE = {
    "poll": poller.Poller,
    "select": poller.Select
}

## Parse Arguments for running the Frontend Server
def parse_args():
    """Parse program argument."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--bind-address',
        default=constants.DEFAULT_HTTP_ADDRESS,
        help='Bind address, default: %(default)s',
    )
    parser.add_argument(
        '--bind-port',
        default=constants.DEFAULT_HTTP_PORT,
        type=int,
        help='Bind port, default: %(default)s',
    )
    parser.add_argument(
        '--base',
        default=constants.DEFAULT_BASE_DIRECTORY,
        help='Base directory to search files in, default: %(default)s',
    )
    parser.add_argument(
        '--poll-timeout',
        type=int,
        default=constants.DEFAULT_POLL_TIMEOUT,
    )
    parser.add_argument(
        '--poll-type',
        choices=POLL_TYPE.keys(),
        default=sorted(POLL_TYPE.keys())[0],
        help='poll or select, default: poll'
    )
    parser.add_argument(
        '--log-file',
        type=str,
        default=None,
    )
    parser.add_argument(
        '--users-file',
        type=str,
        default=constants.DEFAULT_USERS_FILE,
    )
    args = parser.parse_args()
    args.base = os.path.normpath(os.path.realpath(args.base))
    return args

## Main Function that creates the AsyncServer and lets the server run. creates
## also the volumes that are saved in the configuration file.
def main():
    # parse args
    args = parse_args()

    # delete the previous log
    try:
        os.remove(args.log_file)
    except BaseException:
        pass
    logging.basicConfig(filename=args.log_file, level=logging.DEBUG)

    # create opplication context from config_file and args
    application_context = {
        "bind_address": args.bind_address,
        "bind_port": args.bind_port,
        "base": args.base,
        "poll_type": POLL_TYPE[args.poll_type],
        "poll_timeout": args.poll_timeout,
        "users_file" : args.users_file,
        "stats_file" : constants.DEFAULT_STATS_FILE,
    }
    server = async_server.AsyncServer(application_context)
    server.run()


if __name__ == '__main__':
    main()
