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
from utilities import util

## A Block Device Service that allows the Frontend to supply it with a
## long_password for later communication
class UpdateService(base_service.BaseService):

    ## Constructor for LoginService
    # @param entry (entry) the entry (probably @ref
    # common.pollables.service_socket) using the service
    # @param pollables (dict) All the pollables currently in the server
    # @param args (dict) Arguments for this service
    def __init__(self, entry, pollables, args):
        super(UpdateService, self).__init__([], [], args)

        ## the password recieved from the frontend
        self._table_content = ""

    ## Name of the service
    # needed for Frontend purposes, creating clients
    # required by common.services.base_service.BaseService
    # @returns (str) service name
    @staticmethod
    def get_name():
        return "/update"
        
    def handle_content(self, entry, content):
        self._table_content += content
        
    ## What the service does before sending a response status
    # function reads the block requested from the disk file
    # @param entry (pollable) the entry that the service is assigned to
    # @returns (bool) if finished and ready to move on
    def before_response_status(self, entry):
        # self._table content contains everything
        parsed_table = util.parse_table(self._table_content)
        
        # parsed table is of format:
        # [{<col_name> : <col_val>}, ...] where each dict represents a row
        xml_data = ""
        for row in parsed_table:
            xml_row = ""
            for col, val in row.items():
                xml_row += "<%s>%s</%s>" % (col, val, col)
            xml_data += "<row>%s</row>" % xml_row
        
        try:
            os.remove(entry.application_context["stats_file"])
        except:
            pass
            
        try:
            xml_fd = os.open(
                entry.application_context["stats_file"],
                os.o_RDWR | os.O_CREAT
            )
            util.write(
                xml_fd,
                "<Statistics>%s</Statistics>" % (
                    xml_data,
                ),
            )
        except:
            self._response_status = 500
        finally:
            os.close(xml_fd)
            
        return True

