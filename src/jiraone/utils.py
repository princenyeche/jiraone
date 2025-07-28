#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module provides any utility classes or functions that helps to
provide additional ability to jiraone.
"""
import typing as t
import threading
import re
from datetime import datetime as dt, timedelta, timezone
from jiraone import add_log
from jiraone.exceptions import JiraOneErrors


class DotNotation(dict):
    """Provides the ability of using a dot notation on any dict object.
    Makes it easier when working with dictionary objects.

    """

    def __init__(self, *args, **kwargs) -> None:
        """
         Initializes the data within this class.

        Example 1::

        # for dict operation
        my_dict = {"name": "John", "unit": 7}
        notation =  DotNotation(my_dict)
        print(notation.name)

        # result

        # John

        Example 2::

        # for list[dict] operations
        my_dict = [{"name": "John", "unit": 7}, {"name": "Jane", "unit" 8}]
        notation =  DotNotation(value=my_dict)
        print(notation.value[0].name)

        # result - access the list using index

        # John

         :param args: Any argument

         :param kwargs: Any argument

         :return: None

        """
        super().__init__(*args, **kwargs)
        for items in args:
            for key, value in items.items():
                if isinstance(value, dict):
                    value = DotNotation(value)
                elif isinstance(value, list):
                    self.__expose_list__(value)
                self[key] = value

        if kwargs:
            for key, value in kwargs.items():
                if isinstance(value, dict):
                    value = DotNotation(value)
                elif isinstance(value, list):
                    self.__expose_list__(value)
                self[key] = value

    def __getattr__(self, item) -> t.Optional[t.Any]:
        """Gets the attributes."""
        return self[item]

    def __setattr__(self, key, value) -> None:
        """Sets the attributes."""
        self.__setitem__(key, value)

    def __setitem__(self, key, value) -> None:
        """Sets an item in the attribute."""
        super().__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item) -> None:
        """Deletes the attribute."""
        self.__delitem__(item)

    def __delitem__(self, key) -> None:
        """Deletes an item in the attribute."""
        super().__delitem__(key)
        del self.__dict__[key]

    def __expose_list__(self, value) -> None:
        """Defines a list value from a set of values."""
        for key, values in enumerate(value):
            if isinstance(values, dict):
                value[key] = DotNotation(values)
            elif isinstance(values, list):
                self.__expose_list__(values)


def process_executor(
    func: t.Callable,
    *,
    data: t.Iterable = None,
    workers: int = 4,
    timeout: t.Union[float, int] = 2.5,
    **kwargs,
) -> None:
    """
    A process executor function. This function allows you to run asynchronous
    request on certain functions of jiraone, thus making multiple request at
    the same time.

    :param func: A function to act upon
    :param data: A data that the function processes (an argument)
    :param workers: Number of threads to use and wait until terminates
    :param timeout: Specifies a timeout if threads are still running
    :param kwargs: Additional arguments supplied to Thread class or
                   the keyword arguments from the function

    :return: None
    """
    process = threading.Thread(target=func, args=(data,), kwargs=kwargs)
    process.start()
    if threading.active_count() > workers:
        process.join(timeout=timeout)


# Regular expressions
CUSTOM_FIELD_REGEX = r"(Custom field).+([\(]{1}.+?[\)]{1})$"
ISSUE_KEY_REGEX = r"(?:\s|^)([A-Za-z0-9]+-[0-9]+)(?=\s|$)"
INWARD_ISSUE_LINK = r"(Inward issue link).+([\(]{1}.+?[\)]{1})$"
OUTWARD_ISSUE_LINK = r"(Outward issue link).+([\(]{1}.+?[\)]{1})$"


# date utility
class DateFormat:
    """
    A representation of Python's string directive for
    datetime formats
    """

    dd_MM_YYYY_hh_MM_AM_PM = "%d/%m/%Y %I:%M %p"  # dd/MM/YYYY h:mm: AM
    dd_MMM_yy_hh_MM_AM_PM = "%d/%b/%y %I:%M %p"  # dd/MMM/yy h:mm: AM
    dd_MMM_YYYY_hh_MM_SS_AM_PM = (
        "%d-%b-%Y %I:%M:%S %p"  # dd-MMM-YYYY h:mm:ss AM
    )
    MM_dd_yy_hh_MM_AM_PM = "%m-%d-%y %I:%M %p"  # MM-dd-yy h:mm AM
    YYYY_MM_dd_hh_MM_SS_AM_PM = "%Y-%m-%d %I:%M:%S %p"  # YYYY-MM-dd h:mm:ss AM
    dd_MM_YYYY_hh_MM_SS_AM_PM = "%d/%m/%Y %I:%M:%S %p"  # dd-MM-YYYY h:mm:ss AM
    # YYYY-MM-ddTHH:mm:ss.s+0
    YYYY_MM_dd_HH_MM_SS_MS_TZ = "%Y-%m-%dT%H:%M:%S.%f%z"
    YYYY_MM_dd_HH_MM_SS_MS = "%Y-%m-%d %H:%M:%S.%f"  # YYYY-MM-ddTHH:mm:ss.s
    dd_MM_yy_hh_MM_AM_PM = "%d/%m/%y %I:%M %p"  # dd/MM/yy h:mm AM
    YYYY_MM_dd_T_HH_MM_SS_MS = "%Y-%m-%dT%H:%M:%S.%f"  # YYYY-MM-ddTHH:MM:SS.s
    MM_dd_yy_space_hh_MM_AM_PM = "%m/%d/%y %I:%M %p"  # MM/dd/yy h:mm AM
    dd_MM_YYYY_space_hh_MM_AM_PM = "%d/%m/%Y %I:%M %p"  # dd/MM/YYYY h:mm AM
    # MMM dd, YYYY h:mm:ss AM
    MMM_dd_YYYY_hh_MM_SS_AM_PM = "%b %d, %Y %I:%M:%S %p"
    MM_dd_YYYY_hh_MM_AM_PM = "%m/%d/%Y %I:%M %p"  # MM/dd/YYYY h:mm AM
    dd_MMM_yy = "%d/%b/%y"  # dd/MMM/yy
    # dd MMM YYYY h:mm (12-hour)
    dd_space_MMM_space_YYYY_space_hh_MM = "%d %b %Y %I:%M"
    # dd MMM YYYY HH:mm (24-hour)
    dd_space_MMM_space_YYYY_space_HH_MM = "%d %b %Y %H:%M"
    # Wed Oct 18 2023 18:17:15 GMT+0300 (LOCALTIME)
    WD_MMM_dd_YYYY_HH_MM_SS_GMT_TZ = "%a %b %d %Y %H:%M:%S GMT%z (LOCALTIME)"
    # Wed Oct 18 2023 18:17:15 GMT+0300 (TIME) user-defined
    WD_MMM_dd_YYYY_HH_MM_SS_GMT_TZU = "%a %b %d %Y %H:%M:%S GMT{z} (TIME)"


def convert_to_local_time(
    tzinfo: str = None, ahead: int = 0, use_format: str = None,
        sep: str = "T", curr_time: bool = True
) -> t.Union[tuple, str]:
    """Converts from any time to user time given data extracted from
    user timezone

    :param tzinfo: A user timezone information

             Example 1::

             # from datetime import datetime
             d = "2023-07-01 09:11:54.718"
             e = datetime.strptime(d,
                 DateFormat.YYYY_MM_dd_HH_MM_SS_MS).astimezone().strftime(
                 DateFormat.WD_MMM_dd_YYYY_HH_MM_SS_GMT_TZU.format(z="+0300"))
             # +0300 denotes the timezone the user is in. This way
             # you can automatically convert
             # datetime objects to local time
             f = convert_to_local_time(e, 0, sep=" ",
                   use_format=DateFormat.WD_MMM_dd_YYYY_HH_MM_SS_GMT_TZ)
             print(f)

            Example 2::

            tz = ""
            f = convert_to_local_time(tz, 0, sep=" ",
                   use_format=DateFormat.WD_MMM_dd_YYYY_HH_MM_SS_GMT_TZ)
            print(f)

    :param ahead: The number of day or days in the future

    :param use_format: Defines a datetime format to use as output
                       for the datetime value output

    :param sep: A separator string, used to separate date, time and
               datetime values

    :param curr_time: Whether the output should be current time or time
                      that should be converted to local time.

    :return: tuple of date, time, and datetime all in strings
    """

    def parse_timezone(_tzinfo_: str = None) -> str:
        """Process a timezone info"""
        value = _tzinfo_.split("GMT")[1].split("(")[0].strip(" ")
        pattern = re.compile(r"(.\d{3})")
        get_num = pattern.search(value)
        return get_num.string

    def actual_time(gmt: str = None):
        """Send an actual timezone then get the hour or minute"""
        new_time = list(gmt)
        sign, *hour_or_min, _ = new_time
        hour_hand = (
            int(hour_or_min[1])
            if int(hour_or_min[0]) == 0
            else int(f"{hour_or_min[0]}{hour_or_min[1]}")
        )
        get_time_info = tzinfo.split("GMT")[0].rstrip(" ")
        current_time = (dt.now(timezone.utc)  # noqa
                        if curr_time is True
                        else from_datetime_utcnow(
            get_time_info, "%a %b %d %Y %H:%M:%S"))
        if int(hour_or_min[2]) != 0:
            min_hand = 30
            if sign == "-":
                new_zone = timedelta(hours=-hour_hand, minutes=min_hand)
                final_time = current_time - (-new_zone)
            else:
                final_time = current_time + timedelta(
                    hours=hour_hand, minutes=min_hand
                )
        else:
            if sign == "-":
                new_zone = timedelta(hours=-hour_hand)
                final_time = current_time - (-new_zone)
            else:
                final_time = current_time + timedelta(hours=hour_hand)

        return final_time

    current_zone = parse_timezone(tzinfo)  # noqa
    make_time = actual_time(current_zone)
    future_time = make_time + timedelta(days=ahead)
    datetime_string = (
        make_time.strftime(
            DateFormat.YYYY_MM_dd_HH_MM_SS_MS_TZ
            if use_format is None
            else use_format
        )
        if ahead == 0
        else future_time.strftime(
            DateFormat.YYYY_MM_dd_HH_MM_SS_MS_TZ
            if use_format is None
            else use_format
        )
    )
    partition = (
        datetime_string.split(sep)[0],
        datetime_string.split(sep)[1],
        datetime_string,
    ) if curr_time is True else datetime_string
    return partition


def validate_on_error(
    name_field: t.Any = None, data_type: tuple = None, err_message: str = None
) -> None:
    """
    Validate an argument and prepares an error response


    Example 1::

     # import statements
     name: str = "Mr. John"
     validate_on_error(
            name,
            (str, "name", "a string"),
            "the name of a user in strings"
        )

    The second example below shows how you can use multiple data type instance
    to check for the field_name.

    Example 2::

     # import statements
     salary: Union[float, int] = 1230.45
     validate_on_error(
            salary,
            ((float, int), "salary", "a number"),
            "a number to indicate the salary of a user"
        )

    :param name_field: An argument field name

    :param data_type: The data type of the argument, it expects
                     a datatype object, the name of the argument and a message
                     which explains the expected object of the argument

    :param err_message: Expected error message

    :return: None
    :raise: JiraOneErrors
    """

    if not isinstance(name_field, data_type[0]):
        add_log(
            f"The `{data_type[1]}` argument seems to be using the wrong"
            f'data structure "{name_field}" as value, '
            f"expecting {data_type[2]}.",
            "error",
        )
        raise JiraOneErrors(
            "wrong",
            f"The `{data_type[1]}` argument should be "
            f"{err_message}."
            f"Detected {type(name_field)} instead.",
        )


def validate_argument_name(
    name_field: str, valid_args: t.Union[dict, list] = None
):
    """
    Validates the key word argument name of the argument

    :param name_field: The key word argument name
    :param valid_args: The values of arguments expected
    :return: None
    :raise: JiraOneErrors
    """
    if name_field not in valid_args:
        raise JiraOneErrors(
            "errors",
            f"The `{name_field}` argument is invalid, as it does not"
            f" exist in the list of accepted keyword arguments.",
        )


def check_is_type(obj_type: str) -> str:
    """Check whether the item passed is of a
    specific data type
    :param obj_type: The searched obj
    :return: str
    """
    if not isinstance(obj_type, str):
        return ""
    return obj_type

def get_datetime_utcnow() -> t.Any:
    """Return an aware datetime object
    of the current time

    Example 1::

     curr_date = get_datetime_utcnow()
     # returns datetime object with TZ info
     # datetime.datetime(2024, 11, 12, 11, 4, 16, 824379,
     # tzinfo=datetime.timezone.utc)

    :return: A datetime object with timezone info
    """
    today = dt.now()
    get_date = today.fromtimestamp(today.timestamp(), timezone.utc)
    return get_date


def from_datetime_utcnow(from_date: str, _format: str = None) -> t.Any:
    """Return an aware datetime object
    from a string value by adding a timezone info

    :param from_date: The string value to be converted
    :param _format: The string directive for datetime format

    Example 1::

     curr_date = from_datetime_utcnow("2024-12-31 21:00:20.535875")
     # returns datetime object with TZ info
     # datetime.datetime(2024, 12, 31, 20, 0, 20, 535875,
     # tzinfo=datetime.timezone.utc)

    Example 2::

      curr_date = from_datetime_utcnow("2024-12-31 21:00:20.535875",
                  "%Y-%m-%d %H:%M:%S.%f")
     # returns datetime object with TZ info
     # datetime.datetime(2024, 12, 31, 20, 0, 20, 535875,
     # tzinfo=datetime.timezone.utc)

    :return: A datetime object with timezone info
    """
    curr_date = dt.strptime(from_date,
                            DateFormat.YYYY_MM_dd_HH_MM_SS_MS
                            if _format is None else _format)
    get_date = curr_date.fromtimestamp(curr_date.timestamp(), timezone.utc)
    return get_date


def create_urls(**kwargs: t.Any) -> str:
    """
    Dynamically generate a URL pattern based on user supplied arguments.
    It follows the same argument structure as ``endpoint.search_cloud_issues``.
    See doc for the list of arguments that can be supplied.

    :param kwargs: Keyword arguments.

            **Acceptable arguments are**:

                * method - string values "GET" or "POST"
                * fields - list[str] defaults to "*all", you can use
                                    "*all,-comment" - return all fields except
                                     comments. Specify fields returned by name
                * expand - string defaults to None, you can use
                                    "schema,names"
                * properties - list[str] -A list of up to 5 issue
                                        properties to include in the results
                                        defaults to None
                * fields_by_keys - bool - Reference fields by their key
                                        (rather than ID)
                * fail_fast - bool - Fail this request early if we
                                     can't retrieve all field data.
                                     Only for GET request.
                * reconcile_issues - list[int] - Strong consistency
                                          issue ids to be reconciled
                * max_results - int - Maximum number of results to return
                * query - str - The JQL query to submit
                * next_page - str - The next page token of results to return
                                    if available


    :return: A URL pattern based on user supplied arguments.
    """
    from jiraone import endpoint

    method: str = kwargs.get("method", "GET")
    fields: t.Union[str, list[str], None] = kwargs.get("fields", "*all")
    expand: t.Union[str, None] = kwargs.get("expand", "schema,names")
    properties: t.Union[str, list[str], None] = kwargs.get("properties", None)
    fields_by_keys: bool = kwargs.get("fields_by_keys", False)
    fail_fast: bool = kwargs.get("fail_fast", False)
    reconcile_issues: t.Union[
        int, list[int], None] = kwargs.get("reconcile_issues", None)
    query: t.Union[str, None] = kwargs.get("query", None)
    next_page: t.Union[str, None] = kwargs.get("next_page", None)
    max_results: int = kwargs.get("max_results", 50)
    pathway: str = "/rest/api/3/search/jql"
    params: list = []
    # valid key names to parameters
    name_to_token = {
        "jql": query,
        "nextPageToken": next_page,
        "maxResults": max_results,
        "fields": fields,
        "expand": expand,
        "properties": properties,
        "fieldsByKeys": fields_by_keys,
        "failFast": fail_fast,
        "reconcileIssues": reconcile_issues,
    }

    name_popper = []
    for key, value in name_to_token.items():
        if value is not None:
            params.append(f"{key}={value}")
        else:
            name_popper.append(key)
    for _name in name_popper:
        name_to_token.pop(_name)
    if method.upper() == "GET":
        if not params:
            return pathway
        else:
            return f"{pathway}?" + "&".join(params)
    elif method.upper() == "POST":
        if "fields" in name_to_token:
            if not isinstance(name_to_token["fields"], list):
                get_field = name_to_token.pop("fields")
                name_to_token["fields"] = get_field.split(",")
        if "properties" in name_to_token:
            if not isinstance(name_to_token["properties"], list):
                get_property = name_to_token.pop("properties")
                name_to_token["properties"] = get_property.split(",")
        if "reconcileIssues" in name_to_token:
            get_reconcile_issues = name_to_token.pop("reconcileIssues")
            name_to_token["reconcileIssues"] = get_reconcile_issues
        endpoint.get_issue_search_payload = name_to_token
        return pathway
    else:
        raise JiraOneErrors("error",
                            "Invalid `method` argument value provided")


def enhance_search(
        defined_url: str,
        method: str = "GET",
        limit: int = 5000,
) -> dict:
    """Performs a search of issues keeping the payload mechanism looking like
    the old API for search, while retaining the new features of search in Cloud.
    It performs the search for the next-page automatically and returns all issues
    within the project. The URL creation is done automatically by the endpoint
    constant and accepts various argument, see ``endpoint.search_cloud_issues``
    docs for more info on the arguments that can be used. You can also supply
    a direct URL, if it is defined well enough, the API will return results.
    Works with ``GET`` or ``POST`` method.

    :param defined_url: The URL pattern to issue search

    Example 1::

     from jiraone.utils import enhance_search
     from jiraone import endpoint, LOGIN

     # auth process here
     jql = "project = IT AND order by createdDate DESC"
     search = enhance_search(endpoint.search_cloud_issues(
      jql, fields=*all)
     )
     print(search)
     # output
     # {"total": 123, "issues": [...] }


    Example 2::

      from jiraone.utils import enhance_search
      from jiraone import LOGIN

      # auth process here
      jql = "project = IT AND order by createdDate DESC"
      url = "https://yoursite.atlassian.net/rest/api/3/search/jql"
      search = enhance_search(f"{url}?jql={jql}&fields=*all")
      print(search)
      # output
      # {"total": 123, "issues": [...] }

    :param method: values are "GET" or "POST" and case-insensitive
                   defaults to "GET" method

    Example 3::

      from jiraone.utils import enhance_search
      from jiraone import endpoint, LOGIN

      # auth process here
      jql = "project = IT AND order by createdDate DESC"
      url = "https://yoursite.atlassian.net/rest/api/3/search/jql"
      search = enhance_search(endpoint.search_cloud_issues(
      jql, method="POST", fields=*all), method="POST")
      print(search)
      # output
      # {"total": 123, "issues": [...] }


    :param limit: maximum number of results to return, defaults to 5000.

    :return: A dictionary with the results of the search
    """
    from jiraone import endpoint, LOGIN

    if not isinstance(defined_url, str):
        raise JiraOneErrors(
            "error", "The `defined_url` argument must "
                     "be a string that is a valid URL."
        )
    if defined_url == "":
        raise JiraOneErrors(
            "error", "The `defined_url` argument "
                     "must not be an empty string."
        )
    data_obj: dict = {}
    issue_count = 0
    # switch between GET or POST method automatically based on the provided
    # arguments.
    if "?" in defined_url:
        get_param_list: list = defined_url.split("?")[1].split("&")
        jql: str = [
            item.split("jql=")[1] for item in get_param_list if "jql=" in item
        ][0]
    else:
        jql: dict = endpoint.get_issue_search_payload.get("jql")

    total: int = LOGIN.post(endpoint.search_issue_count(),
                            payload={"jql": jql},
                            )
    data_obj["total"] = total.json().get("count", 0)

    if defined_url is not None:
        resp = LOGIN.get(
           defined_url,
        ) if method.upper() == "GET" else LOGIN.post(
            defined_url, payload=endpoint.get_issue_search_payload
        )
        if resp.status_code < 300:
            resp_obj = resp.json()
            def get_issues() -> None:
                """
                process the issue response
                """
                if "issues" in resp_obj:
                    issues = resp_obj["issues"]
                    if "issues" not in data_obj:
                        data_obj["issues"] = issues
                    if "issues" in data_obj:
                        data_obj["issues"] = data_obj["issues"] + issues
            get_issues()

            while "nextPageToken" in resp_obj:
                get_issues()
                next_token, token = resp_obj["nextPageToken"], None
                if "nextPageToken=" in defined_url:
                    get_token_list = defined_url.split("?")[1].split("&")
                    token = \
                    [item.split("nextPageToken=")[1] for item in get_token_list
                     if "nextPageToken=" in item
                     ][0]
                else:
                    token = next_token

                if method.upper() == "POST":
                    modify_payload: dict = endpoint.get_issue_search_payload
                    if next_token is not None:
                        modify_payload.update({"nextPageToken": next_token})
                        endpoint.get_issue_search_payload = modify_payload
                is_token_on = (defined_url.replace(
                        f"nextPageToken={token}",
                        f"nextPageToken={next_token}",
                    1) if "nextPageToken=" in defined_url else
                 defined_url + f"&nextPageToken={token}")

                resp = (
                    LOGIN.get(is_token_on)
                    if method.upper() == "GET" else LOGIN.post(
                    defined_url, payload=endpoint.get_issue_search_payload
                    )
                        )
                if resp.status_code < 300:
                    resp_obj = resp.json()

                if issue_count >= limit:
                    break
                issue_count += 1
        else:
            raise JiraOneErrors(
                "error","Failed to get issue data - {}".format(
                    resp.text
                )
            )


    return data_obj
