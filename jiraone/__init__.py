#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JiraOne is an Atlassian REST API Interface used to Generate report on certain aspect of Jira.

You can dynamically generate a report of
1. Total no of Fields used on per project or the instance
2. Total Number of Users (active, inactive as well as user type)
3. Report of Users able to Browse a certain Project, No of Issues of those Project
4. Total no of Screens used on per projects or the instance
5. Total no of workflows used on per projects or the instance
6. Total no of notification schemes on the instances and their names
7. Total no of permissions schemes on the instance and their names
8. Total no of components used on the instance and their names
9. Total no of projects on the instance
   a) Total no of project roles used per projects or the instance
   b) Total no of issue types on the projects
10. Total no of groups on the instance with their names
11. Total no of dashboards on the instance, who it is shared with
12. Total no of attachments on the project and on the instance
and many more depending on what you can come up with.
"""
from jiraone.access import LOGIN, endpoint, echo, For, field
from jiraone.jira_logs import add_log, WORK_PATH
from jiraone.reporting import PROJECT, USER, file_writer, file_reader, path_builder, replacement_placeholder, comment

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
           "field", "comment"]
