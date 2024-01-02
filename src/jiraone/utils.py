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

        .. code-block:: python

             # for dict operation
             my_dict = {"name": "John", "unit": 7}
             notation =  DotNotation(my_dict)
             print(notation.name)
             # result
             # >>> John

             # for list[dict] operations
             my_dict = [{"name": "John", "unit": 7}, {"name": "Jane", "unit" 8}]
             notation =  DotNotation(value=my_dict)
             print(notation.value[0].name)
             # result - access the list using index
             # >>> John

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
    tzinfo: str = None, ahead: int = 0, use_format: str = None, sep: str = "T"
) -> tuple:
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
        current_time = dt.now(timezone.utc)  # noqa
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
    (mk_date, mk_time, mk_full) = (
        datetime_string.split(sep)[0],
        datetime_string.split(sep)[1].split(".")[0],
        datetime_string,
    )
    return mk_date, mk_time, mk_full


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
            f"The `{data_type[1]}` argument seems to be using the wrong "
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
    Validates the key word argument name and type of the argument

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
