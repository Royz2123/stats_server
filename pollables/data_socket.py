#!/usr/bin/python
## @package stats_server.pollables.data_socket
# Module that defines the DataSocket pollable
#

import dicttoxml
import errno
import logging
import os
import select
import socket
import time
import traceback

from pollables import pollable
from utilities import constants
from utilities import util

## A Socket that listens to new updated data.
class DataSocket(pollable.Pollable):
    (
        DATA_STATE,
        CLOSING_STATE,
    )=range(2)

    ## Constructor for DataSocket
    # @param socket (socket) async socket we work with
    # @param application_context (dict) the application_context for the block
    # device
    # @param pollables (dict) all of the pollables in the server, so that it
    # can add new ones upon connection
    def __init__(self, socket, application_context, pollables):
        ## Application_context
        self._application_context = application_context

        ## Socket to work with
        self._socket = socket

        ## File descriptor of socket
        self._fd = socket.fileno()

        ## Current state the socket is in
        self._state = DataSocket.DATA_STATE

        ## Pointer to all the pollables in the server
        self._recvd_data = ""

        ## Info regarding the data packet
        self._packet_size = 0

    ## File descriptor getter
    # @returns File descriptor (int)
    @property
    def fd(self):
        return self._fd

    ## Socket getter
    # @returns Socket (socket)
    @property
    def socket(self):
        return self._socket

    ## Socket setter
    # @param s (int) new state for the socket
    @socket.setter
    def socket(self, s):
        self._socket = s

    ## recvd_data getter
    # @returns recvd_data (str)
    @property
    def recvd_data(self):
        return self._recvd_data

    ## recvd_data getter
    # @param recvd_data (str)
    @recvd_data.setter
    def recvd_data(self, r):
        self._recvd_data = r

    ## data_to_send setter
    # @returns data_to_send (str)
    @property
    def data_to_send(self):
        return self._data_to_send

    ## data_to_send getter
    # @param data_to_send (str)
    @data_to_send.setter
    def data_to_send(self, d):
        self._data_to_send = d

    ## When DataSocket is terminating.
    ## required by @ref common.pollables.pollable.Pollable
    def is_terminating(self):
        return self._state == DataSocket.CLOSING_STATE

    ## What DataSocket does on close.
    ## required by @ref common.pollables.pollable.Pollable
    def on_close(self):
        self._socket.close()

    def fixed_data(self, parsed_data):
        # parsed_data - list of fixed data numbers
        # these need to be written into the xml file
        self._application_context["Statistics"] = {}

        # set statistics
        for fixed_data in parsed_data:
            self._application_context["Statistics"]["a%s" % fixed_data] = {
                "sc" : "f",
                "tc" : "f",
                "s" : "--",
                "t" : "--",
            }

        # write into xml file
        util.open_and_write(
            self._application_context["stats_file"],
            dicttoxml.dicttoxml(
                {"stats" : self._application_context["Statistics"]}
            )
        )

    def query(self, parsed_data):
        f, s, t = tuple(parsed_data)

        # set colors based on changes
        if self._application_context["Statistics"]["a%s" % f]["s"] not in (s, "--"):
            self._application_context["Statistics"]["a%s" % f]["sc"] = "t"

        if self._application_context["Statistics"]["a%s" % f]["t"] not in (t, "--"):
            self._application_context["Statistics"]["a%s" % f]["tc"] = "t"

        # set data
        self._application_context["Statistics"]["a%s" % f]["s"] = s
        self._application_context["Statistics"]["a%s" % f]["t"] = t

        # write into xml file
        util.open_and_write(
            self._application_context["stats_file"],
            dicttoxml.dicttoxml(
                {"stats" : self._application_context["Statistics"]}
            )
        )

    def delete(self, parsed_data):
        self.fixed_data([
            a[1:] for key in self._application_context["Statistics"].keys()
        ])

    def info(self, parsed_data):
        self._recvd_data = "Coming Soon..."

    DATA_REQUEST = {
        'fd' : fixed_data,
        'q' : query,
        'x' : delete,
        'i' : info,
    }

    ## What DataSocket does on read.
    ## func required by @ref pollables.pollable.Pollable
    def on_read(self):
        try:
            # recv buffer
            util.get_buf(self)

            while len(self._recvd_data):
                # create packet
                if self._packet_size == 0:
                    if len(self._recvd_data) < 4:
                        break
                    self._packet_size = ord(self._recvd_data[0])
                    self._recvd_data = self._recvd_data[4:]

                if len(self._recvd_data) < self._packet_size:
                    break

                # packet fully recieved
                parsed_data, self._recvd_data = (
                    self._recvd_data[:self._packet_size].split(','),
                    self._recvd_data[self._packet_size:],
                )
                DataSocket.DATA_REQUEST[parsed_data[0]](self, parsed_data[1:])

                # get ready for the next packet
                self._recvd_data = self._recvd_data[self._packet_size:]
                self._packet_size = 0

        except Exception as e:
            logging.error("%s :\t %s" %
                (
                    self,
                    traceback.print_exc()
                )
            )
            self.on_error()

    def on_write(self):
        util.send_buf(self)

    ## What DeclarerSocket does on error.
    ## Sets state to closing state
    ## see @ref pollables.pollable.Pollable
    def on_error(self):
        self._state = DataSocket.CLOSING_STATE

    ## Specifies what events the DataSocket listens to.
    ## see @ref pollables.pollable.Pollable
    # @returns event (event_mask)
    def get_events(self):
        event = constants.POLLERR
        if self._state == DataSocket.DATA_STATE:
            event |= constants.POLLIN
        elif len(self._recvd_data):
            event |= constants.POLLOUT
        return event

    ## Returns a representatin of DataSocket Object
    # @returns representation (str)
    def __repr__(self):
        return ("Data Socket Object: %s\t\t\t" % self._fd)
