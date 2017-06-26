#!/usr/bin/python
## @package RAID5.common.utilities.util
# Module that defines many utilities for the project
#

import base64
import errno
import os
import random
import socket
import string
import time
import uuid

from utilities import constants

## Converts a string address to tuple
## @param address (string) address as address:port
## @returns address (tuple) returns (address, port)
def make_address(address):
    try:
        address, port = address.split(constants.ADDRESS_SEPERATOR)
        return (str(address), int(port))
    except BaseException:
        return False

## Makes a tuple address printable
## @param address (tuple) address as (address, port)
## @returns printable_address (string) returns "address:port"
def printable_address(address):
    return "%s%s%s" % (
        address[0],
        constants.ADDRESS_SEPERATOR,
        address[1],
    )

## Writes a buf to a file.
## @param file descriptor (int) open file for writing to which we are writing.
## @param buf (string) buf to write into file.
def write(fd, buf):
    while buf:
        buf = buf[os.write(fd, buf):]

## Reads from a file a certain size
## @param file descriptor (int) open file for reading from which we are
## reading
## @param max_buf (int) max_siz we are willing to read
## @returns file_content (string) file content of size up to max_buffer
def read(fd, max_buffer):
    ret = ""
    while True:
        buf = os.read(fd, max_buffer - len(ret))
        if buf == "":
            break
        ret += buf
    return ret

## Parse a header from a HTTP request or response
## @param line (string) unparsed header line
## @returns parsed_header (tuple) tuple of the header:
## header name, header content
def parse_header(line):
    SEP = ':'
    n = line.find(SEP)
    if n == -1:
        raise RuntimeError('Invalid header received')
    return line[:n].rstrip(), line[n + len(SEP):].lstrip()


    
def update_xml(entry):
    pass
    
# Important Error classes

## Disconnect Error. called when a socket has disconnected ungraceully.
## Inherits from RuntimeError.
class Disconnect(RuntimeError):

    ## Constructor for Disconnect
    ## @param desc (optional) (string) string descrbing the disconnection
    def __init__(self, desc="Disconnect"):
        super(Disconnect, self).__init__(desc)

## InvalidArguments Error.
## Called when recieved invalid arguments for a request from a service.
## Inherits from RuntimeError.
class InvalidArguments(RuntimeError):

    ## Constructor for InvalidArguments.
    ## @param desc (optional) (string) string descrbing the invalid arguments
    def __init__(self, desc="Bad Arguments"):
        super(InvalidArguments, self).__init__(desc)

