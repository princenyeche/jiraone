#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Includes any other functions or global variables
"""
import os
import re
import json
from typing import Union, Any, Optional, List, Callable, Dict
from jiraone.exceptions import JiraOneErrors
from collections import namedtuple, deque
from datetime import datetime as dt
from itertools import zip_longest
from copy import deepcopy


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


def field_update(field,
                 key_or_id: Union[str, int],
                 name: str = None,
                 update: Optional[str] = None,
                 data: Any = None,
                 **kwargs: Any) -> Any:
    """Ability to update a jira field or add to it or remove from it.

    :param name: The name of the field

    :param key_or_id: The issue key or id of the field

    :param field: An alias to jiraone's field variable

    :param update: A way to update a field value.

    :param data: A way to send out data.

            *options to use for ``update`` parameter*

                  * add - add to list value or dict value

                  * remove - remove an option value from a list or dict

    :return: Any object
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


def time_in_status(
        # a variable to call the `PROJECT` alias of `jiraone.report.PROJECT`
        var: Any,
        # issue key or id of an issue, or a list of issue key or id
        key_or_id: Union[str, int, List[Union[str, int]], dict],
        # a file reader function
        reader: Callable = None,
        # A file name used to store the output file
        report_file: Optional[str] = "time_status.csv",
        # a folder which can used to store the file
        report_folder: Optional[str] = "TimeStatus",
        # shows an output type
        output_format: Optional[str] = None,
        # A status to check
        status: Optional[str] = None,
        **kwargs: Any):
    """Return a difference in time between two status or multiple statuses.
    across different sets of issues. Display the output or send the output into
    a file either in CSV or JSON.

    :param var: Alias to the ``PROJECT`` which can invoke the ``change_log()`` method

    :param key_or_id: An issue key or id or keys put in a list to derive multiples values
                    or use a jql format in dictionary

    :param reader: ``file_reader`` function needs to be passed here

    :param report_file: A string of the name of the file

    :param report_folder: A folder where data resides

    :param output_format: An output format either in CSV or JSON. e.g csv or json (case insensitive)

    :param status: A status name to check or output.

    :param kwargs: Additional keyword arguments to use

               *Available options*

               * login - Required keyword argument to authenticate request

               * pprint -Bool, Optional -formats the datetime output into a nice pretty format.

               * is_printable - Bool, prints output to terminal if true


    .. code-block:: python

      # previous expression
      # To print out the function, you can either use ``echo`` function or ``print`` built-in
      status = time_in_status(PROJECT, key, file_reader, login=LOGIN, pprint=True, output_format="json",
                            is_printable=True)
      echo(status)


    :return: A Printable representation of the data or output files.

    """
    login = kwargs["login"] if "login" in kwargs else False
    pprint = kwargs["pprint"] if "pprint" in kwargs else False
    is_printable = kwargs["is_printable"] if "is_printable" in kwargs else False
    output_filename = kwargs["output_filename"] if "output_filename" in kwargs else "data_output_file"
    if login is False:
        raise JiraOneErrors("login", "The `LOGIN` alias is required to authenticate this request")
    if reader is None or not callable(reader):
        raise JiraOneErrors("value", "You need to pass the `file_reader` function, so the data can be read.")
    determine = key_or_id
    form = "key {ins} {determine}"
    if "," in determine:
        determine.split(",")
    jql = "key in ({})".format(determine) if isinstance(determine, (str, int)) else \
        "{}".format(determine["jql"]) if isinstance(determine, dict) else \
            form.format(ins="in" if len(determine) > 1 else "=", determine=tuple(determine)
            if len(determine) > 1 else determine[0]) if isinstance(determine, list) else \
                exit("Unexpected data type received as issue key. Exiting")
    var.change_log(folder=report_folder, file=report_file, jql=jql, field_name="status", show_output=False,
                   fix=True, allow_cp=False)
    data_dog = namedtuple("data_dog", ["IssueKey", "Summary", "Author", "created", "FieldType",
                                       "Field", "From", "fromString", "To", "toString"]) if login.api is False else \
        namedtuple("data_dog", ["IssueKey", "Summary", "Author", "created", "FieldType",
                                "Field", "FieldId", "From", "fromString", "To", "toString", "FromAccountId",
                                "ToAccountId"])

    history = reader(folder=report_folder, file_name=report_file, skip=True)
    log_data = deque()
    collect_data = deque()
    for histories in history:
        items = data_dog._make(histories)
        time_stat = {
            "issue_key": items.IssueKey,
            "created": items.created,
            "from_string": items.fromString,
            "summary": items.Summary,
            "author": items.Author,
            "to_string": items.toString,
            "blank_data": items.FieldType
        }
        log_data.append(time_stat)

    # do the difference in time between two status
    rows = 0
    number_of_history_items = len(log_data)
    history_copy = deepcopy(log_data)
    if len(history_copy) > 0:
        del history_copy[0]
    else:
        exit("No data to read.Quiting...")
    for items, item in zip_longest(log_data, history_copy, fillvalue={
        "issue_key": 0,
        "created": 0,
        "author": 0,
        "from_string": 0,
        "to_string": 0,
        "summary": 0,
        "blank_data": 0
    }):
        def initialize(to_, from_) -> None:
            """Rerun the data for time extraction.

            :param to_: A timedelta object showing the present or future datetime

            :param from_: A timedelta object showing the previous datetime

            :return: none
            """
            difference = to_ - from_
            data_bundle = {
                "time_status": pretty_format(difference, pprint),
                "issue_key": items['issue_key'],
                "from_string": items['from_string'],
                "to_string": items['to_string'],
                "summary": items['summary'],
                "author": items['author'],
                "blank_data": items['blank_data']
            }
            collect_data.append(data_bundle)

        rows += 1
        # for each row, check the next row if exist and if the key is the
        # same as of the period the status changed
        if items['issue_key'] == item['issue_key']:
            # parse the datetime string with a proper format
            from_time = dt.strptime(items['created'], "%Y-%m-%dT%H:%M:%S.%f%z")
            to_time = dt.strptime(item['created'], "%Y-%m-%dT%H:%M:%S.%f%z")
            # get a timedelta of the datetime value
            initialize(to_time, from_time)
        else:
            if items['from_string'] == items['to_string']:
                from_time = dt.strptime(items['created'], "%Y-%m-%dT%H:%M:%S.%f%z")
                # convert the current time to something we that we can use timedelta on
                present = dt.strftime(dt.astimezone(dt.now()), "%Y-%m-%dT%H:%M:%S.%f%z")
                today = dt.strptime(present, "%Y-%m-%dT%H:%M:%S.%f%z")
                initialize(today, from_time)
            else:
                # default here if this is the current status.
                from_time = dt.strptime(items['created'], "%Y-%m-%dT%H:%M:%S.%f%z")
                present = dt.strftime(dt.astimezone(dt.now()), "%Y-%m-%dT%H:%M:%S.%f%z")
                today = dt.strptime(present, "%Y-%m-%dT%H:%M:%S.%f%z")
                initialize(today, from_time)
        if rows >= number_of_history_items:
            break

    data_collection = deque()

    def matrix_loop(proxy, rev: bool = True) -> None:
        """Repeat of ``if`` steps validating the status.

        :param proxy: The name of the iterable data within the dict

        :param rev: Changes context of dict value for proxy argument

        :return: None
        """
        matrix = [proxy['issue_key'], proxy['summary'], proxy['author'], proxy['time_status'],
                  proxy['from_string' if proxy['blank_data'] == "" else 'to_string'] if rev is True else
                  proxy['to_string']]
        data_collection.append(matrix)

    if status is not None:
        if isinstance(status, str):
            for name in collect_data:
                if name['blank_data'] == "":
                    if name['from_string'].lower() == status.lower():
                        matrix_loop(name)
                else:
                    if name['to_string'].lower() == status.lower():
                        matrix_loop(name)

        else:
            raise JiraOneErrors("wrong", "Expecting `status` argument to be a string value "
                                         "got {} instead".format(type(status)))
    elif status is None:
        for name in collect_data:
            matrix_loop(name)

    collect_data.clear()
    from jiraone import file_writer, path_builder
    output_name = f"{output_filename}.{output_format.lower()}"
    if output_format is None:
        pass
    else:
        if output_format.lower() == "csv":
            header = ["Issue Key", "Summary", "Author", "Time in Status", "Status"]
            file_writer(folder=report_folder, file_name=output_name, mode="w+", data=header)
            file_writer(folder=report_folder, file_name=output_name, mode="a+", data=data_collection, mark="many")
        elif output_format.lower() == "json":
            make = []
            for load in data_collection:
                payload = {
                    "issueKey": load[0],
                    "summary": load[1],
                    "author": load[2],
                    "timeStatus": load[3],
                    "status": load[4]
                }
                make.append(payload)
            json.dump(make, open(f"{report_folder}/{output_name}", mode="w+", encoding="utf-8"), sort_keys=True,
                      indent=4)
        else:
            raise JiraOneErrors("value", f"Unexpected output \"{output_format}\" received as value, "
                                         f"for output_format argument - unable to understand option. Exiting")

    return f"Output file is located at: {path_builder(report_folder, output_name)}" if is_printable \
                                                                                       is False else data_collection


# get a pretty format of the datetime output
def pretty_format(date: Any, pprint: bool) -> str:
    """Scan the datetime value and return a pretty format in string if true else returns string of datetime object.

        :param date: A datetime object or a string datetime value

        :param pprint: A bool object

        :return: A string value
        """
    pattern = r"\d+"  # searches for the digits in the value
    make_date = str(date)
    if pprint is True:
        if "," in make_date:
            new_date = make_date.split(",")
            get_days = re.compile(pattern)
            get_times = re.compile(pattern)
            if get_days is not None:
                m = get_times.findall(new_date[1])
                return f"{get_days.search(new_date[0]).group()}d {m[0]}h {m[1]}m {m[2]}s"
        else:
            get_numbers = re.compile(pattern)
            if get_numbers is not None:
                d = get_numbers.findall(make_date)
                return f"{d[0]}h {d[1]}m {d[2]}s"
    return make_date


def bulk_change_email(data: str, token: str) -> None:
    """Bulk change managed user's email address if they do not exist.

    :param data: A string of the file name

    :param token: A string of the API token to authenticate the request

    Additionally, the output of failed attempts it written back to your data file.

    :return: None
    """
    from jiraone import file_reader, file_writer, manage as org
    collect = deque()
    # Provide a CSV file data source
    read = file_reader(file_name=data, skip=True)
    data_check = deepcopy(read)
    headers = ["account_id", "current_email", "name", "target_email"]
    file_writer(file_name=data, mode="w+", mark="single", data=headers)
    if len(data_check[0]) != 4:
        raise JiraOneErrors("value", f"The expected data column should be 4 columns got {len(data_check[0])} instead")
    items = namedtuple("items", ["account_id", "current_email", "name", "target_email"])
    org.add_token(token)
    for _ in read:
        user = items._make(_)
        payload = {
            "email": user.target_email
        }
        response = org.manage_profile(account_id=user.account_id, method="put", json=payload)
        if response.status_code < 300:
            print(f"Changed current email: {user.current_email} to target email: {user.target_email}")
        else:
            print(f"Not able to change current email: {user.current_email} to target email: {user.target_email} "
                  f"- {response.reason}")
            collect.append(_)

    # If any of the email address isn't changed, write the output to the same file.
    file_writer(file_name=data, mode="a+", mark="many", data=collect)
    print("Change process completed".upper())
    collect.clear()


def bulk_change_swap_email(data: str, token: str, **kwargs: Any) -> None:
    """The function helps to swap an email address to another.

    If the target email exist as an Atlassian account email, this will help to swap
    that email address to the desired target email.

    :param data: A string of the file name

    :param token: An API token to authenticate the API.

    :param kwargs: Additional keyword argument to pass

                *Valid values*

                * dummy - A dummy email address to choose if not a default is formed
                   from your email address

                * users - The name of a file to check the users and their account_id
                    only needed if you want to search a predefined set of users.

    :return: None
    """
    from jiraone import file_reader, file_writer, manage as org
    collect = deque()
    org.add_token(token)
    # Provide a CSV file data source
    read = file_reader(file_name=data, skip=True)
    data_check = deepcopy(read)
    copy_name = data.split('.')[0] + "_cp.csv"
    headers = ["account_id", "current_email", "name", "target_email", "reason"]
    headers_2 = ["account_id", "email"]
    file_writer(file_name=data, mode="w+", mark="single", data=headers)
    file_writer(file_name=copy_name, mode="w+", mark="single", data=headers_2)
    dummy = kwargs['dummy'] if 'dummy' in kwargs else ""
    if len(data_check[0]) != 4:
        raise JiraOneErrors("value", f"The expected data column should be 4 columns got {len(data_check[0])} instead")
    user_items = namedtuple("user_items", ["account_id", "email"])
    items = namedtuple("items", ["account_id", "current_email", "name", "target_email"])
    # If you want, you can supply your own user list for find_id()
    users = file_reader(file_name=kwargs['users'], skip=True) if 'users' in kwargs else None
    data_response = {'count': 0, 'email': None}
    source_data = org.get_organization(filter_by="users").json()
    source_user = org.get_all_users(source_data)
    file_writer(file_name=copy_name, mark="many", mode="a+", data=source_user)
    source_user.clear()
    get_file = file_reader(file_name=copy_name, skip=True)

    def find_id(email: str) -> Any:
        """Return a string if email is found else None.

        :param email: A string

        :return: str if email is found else None.
        """
        data_parse = get_file if 'users' not in kwargs else users
        for z in data_parse:
            obtain = user_items._make(z)
            if email in obtain._asdict().values():
                return obtain.account_id

    def dummy_swap(emails: Any, count: int) -> Dict:
        """Returns a dictionary

            :param emails: A namedtuple to string of an email address

            :param count: An integer count, basically trying to see if we can keep track of the changes.

            :return: dict
            """
        check_email = org.manage_profile(emails.account_id).json()
        if dummy == check_email.get("account").get("email"):
            access = {
                "email": emails.target_email
            }
            result = org.manage_profile(emails.account_id, json=access, method="put")
            if result.status_code < 300:
                count += 1
                return {"result": result, "count": count, "email": emails.target_email}
        return {"result": None, "count": count, "email": None}

    def target_swap(emails: Any, count: int) -> Dict:
        """Returns a dictionary

            :param emails: A namedtuple to string

            :param count: An integer count, basically trying to see if we can keep track of the changes.

            :return: dict
            """
        access = {
            "email": emails.current_email
        }
        get_id = find_id(emails.target_email)
        if get_id is not None:
            result = org.manage_profile(get_id, json=access, method="put")
            if result.status_code < 300:
                count += 1
                return {"result": result, "count": count, "email": emails.current_email}
        return {"result": None, "count": count, "email": None}

    swap_completion = 0
    for _ in read:
        user = items._make(_)
        current = user.current_email.split("@")[1]
        dummy = "dummy0000008@" + current if 'dummy' not in kwargs else kwargs['dummy']
        payload = {
            "email": dummy
        }

        response = org.manage_profile(user.account_id, method="put", json=payload)
        if response.status_code < 300:
            print("Success:", f"Status: {response.status_code}", sep="---")
            print(f"Changing current email: {user.current_email} to dummy email: {dummy}")
            data_response['count'] += 1
            if data_response['count'] > 0:
                data_response = target_swap(user, data_response['count'])
                if data_response['email'] is not None:
                    print(f"Changing target email: {user.target_email} to current email: {data_response['email']}")
                    data_response = dummy_swap(user, data_response['count'])
                    if data_response['email'] is not None:
                        print(f"Changing dummy email: {dummy} to target email: {data_response['email']}")
                        swap_completion += 1
                        data_response['count'] -= 2
                    else:
                        print(
                            f"Unable to change dummy email: {dummy} to target email: {data_response['email']}")
                else:
                    print(
                        f"Unable to change target email: {user.target_email} to current email: {data_response['email']}")
                    error_data = [user.account_id, user.current_email, user.name, user.target_email,
                                  data_response['result']]
                    collect.append(error_data)
        else:
            print("Error:", f"status: {response.status_code}", f"Reason: {response.reason}", sep="---")
            print(f"Unable to change current email: {user.current_email} to dummy email: {dummy}")
            error_data = [user.account_id, user.current_email, user.name, user.target_email, response.reason]
            collect.append(error_data)
        print("*" * 100)

    # For any email that is not changed, write it back to the same file
    file_writer(file_name=data, mode="a+", mark="many", data=collect)
    print("Process complete, made swap attempt of {} email(s), complete cycle swap of {} email(s)."
          .format(data_response['count'], swap_completion))
    os.remove(copy_name)
    collect.clear()


permissions = Permissions()
