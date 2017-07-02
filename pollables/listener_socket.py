#!/usr/bin/python
## @package RAID5.common.pollables.listener_socket
# Module that defines the ListenerSocket pollable
#

import errno
import logging
import os
import select
import socket
import traceback

from pollables import pollable
from pollables import service_socket
from pollables import data_socket
from utilities import constants
from utilities import util

## A Socket that listens to new connections to the server. The socket binds to
## the servers bind_address and bind_port and listens to new connections. once
## recieved a new connection, it creates a service socket to handle the
## request.
class ListenerSocket(pollable.Pollable):

    ## Constructor for ListenerSocket
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
        self._state = constants.LISTEN_STATE

        ## Pointer to all the pollables in the server
        self._pollables = pollables

    ## File descriptor getter
    # @returns File descriptor (int)
    @property
    def fd(self):
        return self._fd

    ## State getter
    # @returns State (int)
    @property
    def state(self):
        return self._state

    ## State setter
    # @param s (int) new state for the socket
    @state.setter
    def state(self, s):
        self._state = s

    ## Listen state function. Recieves a new connection and adds to pollables.
    def listen_state(self):
        new_socket, address = self._socket.accept()

        # set to non blocking
        new_socket.setblocking(0)

        # add to database
        # |pollables| = 1 ==> only listener
        # |pollables| = 2 ==> listener + data socket
        if len(self._pollables) == 0:
            new_pollable = data_socket.DataSocket(
                new_socket,
                self._application_context,
                self._pollables
            )
        else:
            new_pollable = service_socket.ServiceSocket(
                new_socket,
                constants.GET_REQUEST_STATE,
                self._application_context,
                self._pollables
            )
        self._pollables[new_socket.fileno()] = new_pollable
        logging.debug(
            "%s :\t Added a new socket, %s"
            % (
                self,
                new_pollable
            )
        )

    ## When ListenerSocket is terminating.
    ## required by @ref common.pollables.pollable.Pollable
    def is_terminating(self):
        return self._state == constants.CLOSING_STATE

    ## What ListenerSocket does on close.
    ## required by @ref common.pollables.pollable.Pollable
    def on_close(self):
        self._socket.close()

    ## What ListenerSocket does on read.
    ## If not closing, recieve new request by calling
    ## @ref common.pollables.listener_socket.ListenerSocket.listen_state
    ## func required by @ref common.pollables.pollable.Pollable
    def on_read(self):
        try:
            if self._state == constants.LISTEN_STATE:
                self.listen_state()

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
    ## see @ref common.pollables.pollable.Pollable
    def on_error(self):
        self._state = constants.CLOSING_STATE

    ## Specifies what events the ListenerSocket listens to.
    ## see @ref common.pollables.pollable.Pollable
    # @returns event (event_mask)
    def get_events(self):
        event = constants.POLLERR
        if (
            self._state == constants.LISTEN_STATE and
            len(self._pollables) < constants.MAX_CONNECTIONS
        ):
            event |= constants.POLLIN
        return event

    ## Returns a representatin of ListenerSocket Object
    # @returns representation (str)
    def __repr__(self):
        return ("HttpListen Object: %s\t\t\t" % self._fd)
