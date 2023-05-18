#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module provides any utility classes or functions that helps to
provide additional ability to jiraone.
"""
import typing as t
import threading


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
        super(DotNotation, self).__init__(*args, **kwargs)
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
        super(DotNotation, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item) -> None:
        """Deletes the attribute."""
        self.__delitem__(item)

    def __delitem__(self, key) -> None:
        """Deletes an item in the attribute."""
        super(DotNotation, self).__delitem__(key)
        del self.__dict__[key]

    def __expose_list__(self, value) -> None:
        """Defines a list value from a set of values."""
        for key, values in enumerate(value):
            if isinstance(values, dict):
                value[key] = DotNotation(values)
            elif isinstance(values, list):
                self.__expose_list__(values)


def process_executor(func: t.Callable,
                     *,
                     data: t.Iterable = None,
                     workers: int = 4,
                     timeout: t.Union[float, int] = 2.5,
                     **kwargs) -> None:
    """
    A process executor function

    :param func: A function to act upon
    :param data: A data that the function processes
    :param workers: Number of threads to use and wait until terminates
    :param timeout: Specifies a timeout to join threads
    :param kwargs: Additional arguments supplied to Thread class
    :return: None
    """
    process = threading.Thread(target=func, args=(data,), kwargs=kwargs)
    process.start()
    if threading.active_count() > workers:
        process.join(timeout=timeout)


# Regular expressions
CUSTOM_FIELD_REGEX = r"(Custom field).+([\(]{1}.+?[\)]{1})$"
CUSTOM_FIELD_REGEX_PLUS = r"(Custom field).+([\(]{1}.+?[\)]{1})\w+"
ISSUE_KEY_REGEX = r"(?:\s|^)([A-Za-z0-9]+-[0-9]+)(?=\s|$)"
