#!/usr/bin/python
## @package RAID5.common.utilities.html_util
# Module that defines many html functions for use of HTTP services
#

import errno
import logging
import os
import select
import time
import traceback

from utilities import constants
from utilities import util

## Build a a html page based on requirements
## @param content (string) content of the html page
## @param header  (optional) (string) title header of the html page
## @param refresh  (optional) (int) refresh time of the html page
## @param redirect_url (optional) (string) redirect_url to new html page
## @returns html_page (string) returns build html page
def create_html_page(
    content,
    header=constants.HTML_DEFAULT_HEADER,
    refresh=None,
    redirect_url="",
):
    refresh_header = ""
    if refresh is not None:
        refresh_header = (
            "<meta http-equiv='refresh' content='%s%s'>"
            % (
                refresh,
                "; %s" % (redirect_url * (redirect_url != ""))
            )
        )

    return (
        (
            "<HTML><HEAD>%s%s%s<TITLE>%s</TITLE></HEAD>" +
            "<BODY>%s</BODY></HTML>"
        ) % (
            create_style_link(),
            create_style_link(
                "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/"
                + "4.7.0/css/font-awesome.min.css"
            ),
            refresh_header,
            header,
            content
        )
    )

## Creates a style tag
## @param sheet (string) name of a CSS stylesheet
## @returns style_link (string) html ink to stylesheet
def create_style_link(
    sheet=constants.DEFAULT_STYLE_SHEET
):
    return (
        "<link rel='stylesheet' type='text/css' href=%s>" % (
            sheet
        )
    )
