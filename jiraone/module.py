#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Includes any other functions or global variables
"""
from typing import Union, Any, Optional
from jiraone.exceptions import JiraOneErrors


class Permissions(object):
    """A constant of Jira permission scheme attributes."""
    ASSIGNABLE_USER = "ASSIGNABLE_USER"
    ASSIGN_ISSUE = "ASSIGN_ISSUE"
    ATTACHMENT_DELETE_ALL = "ATTACHMENT_DELETE_ALL"
    ATTACHMENT_DELETE_OWN = "ATTACHMENT_DELETE_OWN"
    BROWSE = "BROWSE"
    CLOSE_ISSUE = "CLOSE_ISSUE"
    COMMENT_DELETE_ALL = "COMMENT_DELETE_ALL"
    COMMENT_DELETE_OWN = "COMMENT_DELETE_OWN"
    COMMENT_EDIT_ALL = "COMMENT_EDIT_ALL"
    COMMENT_EDIT_OWN = "COMMENT_EDIT_OWN"
    COMMENT_ISSUE = "COMMENT_ISSUE"
    CREATE_ATTACHMENT = "CREATE_ATTACHMENT"
    CREATE_ISSUE = "CREATE_ISSUE"
    DELETE_ISSUE = "DELETE_ISSUE"
    EDIT_ISSUE = "EDIT_ISSUE"
    LINK_ISSUE = "LINK_ISSUE"
    MANAGE_WATCHER_LIST = "MANAGE_WATCHER_LIST"
    MODIFY_REPORTER = "MODIFY_REPORTER"
    MOVE_ISSUE = "MOVE_ISSUE"
    PROJECT_ADMIN = "PROJECT_ADMIN"
    RESOLVE_ISSUE = "RESOLVE_ISSUE"
    SCHEDULE_ISSUE = "SCHEDULE_ISSUE"
    SET_ISSUE_SECURITY = "SET_ISSUE_SECURITY"
    TRANSITION_ISSUE = "TRANSITION_ISSUE"
    VIEW_VERSION_CONTROL = "VIEW_VERSION_CONTROL"
    VIEW_VOTERS_AND_WATCHERS = "VIEW_VOTERS_AND_WATCHERS"
    VIEW_WORKFLOW_READONLY = "VIEW_WORKFLOW_READONLY"
    WORKLOG_DELETE_ALL = "WORKLOG_DELETE_ALL"
    WORKLOG_DELETE_OWN = "WORKLOG_DELETE_OWN"
    WORKLOG_EDIT_ALL = "WORKLOG_EDIT_ALL"
    WORKLOG_EDIT_OWN = "WORKLOG_EDIT_OWN"
    WORK_ISSUE = "WORK_ISSUE"


def field_update(field, key_or_id: Union[str, int], name: Optional[str] = None, update: Optional[str] = None,
                 data: Optional[Any] = None, **kwargs: Any):
    """Ability to update a jira field or add to it or remove from it.

    :param name The name of the field
    :param key_or_id The issue key or id of the field
    :param field An alias to jiraone's field variable
    :param update A way to update a field value.
    :param data A way to send out data.

            *options to use for `update` parameter*
                  i) add - add to list value or dict value
                  ii) remove - remove an option value from a list or dict
    """
    if name is None:
        raise JiraOneErrors("name")
    try:
        field_type = field.get_field(name).get("custom")
        if field_type is True:
            determine_field = "custom"
        else:
            determine_field = "system"
        output = field.update_field_data(data, name, determine_field, key_or_id, options=update, **kwargs)
    except AttributeError:
        raise JiraOneErrors("name")
    return output

  
  permission = Permissions()
