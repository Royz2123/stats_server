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
import struct
import time
import traceback

from pollables import pollable
from utilities import constants
from utilities import util

## A Socket that listens to new updated data.
class DataSocket(pollable.Pollable):
    (
        SEND_CONNECT_STATE,
        RECV_CONNECT_STATE,
        SEND_LOGIN_STATE,
        SEND_SHAHAR_STATE,
        RECV_SHAHAR_STATE,
        RECV_DATA_STATE,
        CLOSING_STATE,
    )=range(7)

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
        self._state = DataSocket.SEND_CONNECT_STATE

        ## Data need to send back to moshe
        self._data_to_send = "IsConnected?"
        self.create_packet()

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
        f, ign1, ign2, s, t = tuple(parsed_data)

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

    def delete(self):
        self.fixed_data([
            key[1:] for key in self._application_context["Statistics"].keys()
        ])

    def info(self, parsed_data):
        self._data_to_send = ""

        for username, info in self._application_context["users"].items():
            self._data_to_send += "%s:%s," % (
                username,
                info["timestamp"]
            )
        self._data_to_send = self._data_to_send[:-1]
        self.create_packet()

    ## What DataSocket does on read.
    ## func required by @ref pollables.pollable.Pollable
    def on_read(self):
        # recv buffer
        util.get_buf(self)

        try:
            if self._state == DataSocket.RECV_CONNECT_STATE:
                if (
                    (not self.check_packet()) and
                    (not self.check_prefix("Connected=Yes"))
                ):
                    return
                # handle connection (not interesting)
                self._recvd_data = ""

                # Prepare packet to send
                self._data_to_send = "Login:user,pass"
                self.create_packet()
                self._state = DataSocket.SEND_LOGIN_STATE

            if self._state == DataSocket.RECV_SHAHAR_STATE:
                if (
                    (not self.check_packet()) and
                    (not self.check_prefix("ShaharList="))
                ):
                    return

                # Got the SHACHAR numbers, process them
                self.fixed_data(self._recvd_data.split(','))
                self._recvd_data = ""

                # Finally move on to data part
                self._packet_size = 0
                self._state = DataSocket.RECV_DATA_STATE

            if self._state == DataSocket.RECV_DATA_STATE:
                while len(self._recvd_data):
                    # check packet
                    if not self.check_packet():
                        return

                    # manually check prefix (either QN or QX)
                    if self.check_prefix("QN:"):
                        self.query(self._recvd_data.split(','))
                    elif self.check_prefix("QX"):
                        self.delete()

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

    def check_packet(self):
        if self._packet_size == 0:
            if len(self._recvd_data) < 4:
                return False
            self._packet_size = ord(self._recvd_data[0])
            self._recvd_data = self._recvd_data[4:]

        if len(self._recvd_data) < self._packet_size:
            return False
        return True

    def check_prefix(self, prefix):
        if (
            self._recvd_data[:len(prefix)]
            == prefix
        ):
            self._recvd_data = self._recvd_data[len(prefix):]
            return True
        return False

    def create_packet(self):
        self._data_to_send = (
            struct.pack('>I', len(self._data_to_send))
            + self._data_to_send
        )

    def on_write(self):
        # send buffer
        util.send_buf(self)

        try:
            if self._state == DataSocket.SEND_CONNECT_STATE:
                if len(self._data_to_send):
                    return

                # Get ready for next packet
                self._packet_size = 0
                self._state = DataSocket.RECV_CONNECT_STATE

            if self._state == DataSocket.SEND_LOGIN_STATE:
                if len(self._data_to_send):
                    return

                # Prepare packet to send
                self._data_to_send = "GetShaharList"
                self.create_packet()
                self._state = DataSocket.SEND_SHAHAR_STATE

            if self._state == DataSocket.SEND_SHAHAR_STATE:
                if len(self._data_to_send):
                    return

                # Get ready for next packet
                self._packet_size = 0
                self._state = DataSocket.RECV_SHAHAR_STATE

        except Exception as e:
            logging.error("%s :\t %s" %
                (
                    self,
                    traceback.print_exc()
                )
            )
            self.on_error()

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
        if self._state in [
            DataSocket.RECV_SHAHAR_STATE,
            DataSocket.RECV_CONNECT_STATE,
            DataSocket.RECV_DATA_STATE,
        ]:
            event |= constants.POLLIN
        if self._state in [
            DataSocket.SEND_CONNECT_STATE,
            DataSocket.SEND_LOGIN_STATE,
            DataSocket.SEND_SHAHAR_STATE
        ]:
            event |= constants.POLLOUT
        return event

    ## Returns a representatin of DataSocket Object
    # @returns representation (str)
    def __repr__(self):
        return ("Data Socket Object: %s\t\t\t" % self._fd)
