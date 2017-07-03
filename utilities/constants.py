#!/usr/bin/python
## @package RAID5.common.utilities.constants
# Module that defines all of the systems constants
#

import os
import select

## Polling constants
# Define polling constants based on OS
POLLIN, POLLOUT, POLLERR, POLLHUP = (
    1, 4, 8, 16,
) if os.name == "nt" else (
    select.POLLIN, select.POLLOUT, select.POLLERR, select.POLLHUP,
)

## Polling event names (for debugging purposes mostly)
POLL_EVENTS = {
    POLLIN : "POLLIN",
    POLLOUT : "POLLOUT",
    POLLERR : "POLLERR",
    POLLHUP : "POLLHUP",
}

## Default frontend server http bind port
DEFAULT_HTTP_PORT = 8000

## Default bind address (should always by "0.0.0.0")
DEFAULT_HTTP_ADDRESS = "0.0.0.0"

## Default timeout for POLL
DEFAULT_POLL_TIMEOUT = 1000

## Maximum buffer size
MAX_BUFFER = 10000

## Maximum connection
MAX_CONNECTIONS = 1000

## My Seperator
USERS_SEPERATOR = '$'
CREDENTIALS_SEPERATOR = ':'

## CRLF new line
CRLF = '\r\n'
CRLF_BIN = CRLF.encode('utf-8')

## Http signature we work with, http version
HTTP_SIGNATURE = 'HTTP/1.1'

## Max size of a header
MAX_HEADER_LENGTH = 4096

## Max headers allowed
MAX_NUMBER_OF_HEADERS = 100

## Standard input and outputs
STANDARD_INPUT = 0
STANDARD_OUTPUT = 1
STANDARD_ERROR = 2

## Default base directory for requested files
DEFAULT_BASE_DIRECTORY = "files"

## Default file location of users
DEFAULT_STATS_FILE = "files/table.xml"
DEFAULT_USERS_FILE = "users.txt"
MAX_USERS_FILE_SIZE = 10000

## Default time until page refreshes. Once refreshed, the frontend server
## checks for terminated connections of disks
DEFAULT_REFRESH_TIME = 6

## Default style sheet (css)
DEFAULT_STYLE_SHEET = "style.css"

## Default title for HTML page
HTML_DEFAULT_HEADER = "Capitalead"

## Mapping between file names
MIME_MAPPING = {
    'html': 'text/html',
    'png': 'image/png',
    'txt': 'text/plain',
    'css': 'text/css',
}

## Dict of all the mdoules of services a Server can use
HTTP_SERVICES = [
    "services.login_service",
    "services.get_file_service",
]

## HTTP States
(
    GET_STATUS_STATE,
    GET_REQUEST_STATE,
    GET_HEADERS_STATE,
    GET_CONTENT_STATE,
    SEND_STATUS_STATE,
    SEND_REQUEST_STATE,
    SEND_HEADERS_STATE,
    SEND_CONTENT_STATE,
    SLEEPING_STATE,
    LISTEN_STATE,
    CLOSING_STATE,
    OFFLINE_STATE,
) = range(12)
