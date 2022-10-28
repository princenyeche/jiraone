#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JiraOne is an Atlassian REST API Interface used to generate report on certain aspect of Jira.

You can dynamically generate a report of

* Users/Organization users

* Extract Issue history

* Comments

* Send and download attachments

* Get time in status of issues

* Download a stats of users in a project and their roles

and many more depending on what you can come up with.

"""
from jiraone.access import LOGIN, endpoint, echo, For, field
from jiraone.jira_logs import add_log, WORK_PATH
from jiraone.reporting import PROJECT, USER, file_writer, file_reader, path_builder, \
    replacement_placeholder, comment, delete_attachments, issue_export
from jiraone.management import manage

__author__ = "Prince Nyeche"
__version__ = "0.7.3"
__all__ = ["LOGIN",
           "endpoint",
           "echo",
           "add_log",
           "WORK_PATH",
           "PROJECT",
           "USER",
           "file_writer",
           "file_reader",
           "path_builder",
           "replacement_placeholder",
           "For",
           "field",
           "comment",
           "manage",
           "delete_attachments",
           "issue_export"]
