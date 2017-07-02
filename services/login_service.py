#!/usr/bin/python
## @package RAID5.block_device.services.login_service
# Module that implements the Block Device LoginService
#

import errno
import logging
import os
import socket
import time
import traceback

from services import base_service
from utilities import constants
from utilities import html_util
from utilities import util

## A Block Device Service that allows the Frontend to supply it with a
## long_password for later communication
class LoginService(base_service.BaseService):

    ## Constructor for LoginService
    # @param entry (entry) the entry (probably @ref
    # common.pollables.service_socket) using the service
    # @param pollables (dict) All the pollables currently in the server
    # @param args (dict) Arguments for this service
    def __init__(self, entry, pollables, args):
        super(LoginService, self).__init__([], ["add"], args)

        ## the password recieved from the frontend
        self._password_content = ""

    ## Name of the service
    # needed for Frontend purposes, creating clients
    # required by common.services.base_service.BaseService
    # @returns (str) service name
    @staticmethod
    def get_name():
        return "/login"

    ## What the service does before sending a response status
    # function reads the block requested from the disk file
    # @param entry (pollable) the entry that the service is assigned to
    # @returns (bool) if finished and ready to move on
    def before_response_status(self, entry):
        req_name, req_pswd = (
            self._args["username"][0],
            self._args["password"][0]
        )
        fd = None
        try:
            fd = os.open(entry.application_context["users_file"], os.O_RDONLY)
            users = util.read(fd, constants.MAX_USERS_FILE_SIZE).split(
                constants.USERS_SEPERATOR
            )
            parsed_users = {}
            for user in users[:-1]:
                name, pswd, greet = user.split(constants.CREDENTIALS_SEPERATOR, 2)
                parsed_users[name] = pswd

            if (
                req_name not in parsed_users.keys()
                or req_pswd != parsed_users[req_name]
            ):
                raise RuntimeError("Invalid Credentials")

            self._response_content = html_util.create_html_page(
                html_util.create_stats_page(greet),
                header="Capitalead - Statistics",
            )
            self._response_headers = {
                "Content-Length": len(self._response_content)
            }
        except Exception as e:
            traceback.print_exc()
            self._response_status = 401
        finally:
            if fd is not None:
                os.close(fd)

        return True
