#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
An exceptions list of errors
"""


class JiraOneErrors(Exception):
    """Base class for all exceptions."""

    def __init__(self, errors, messages=None):
        self.errors = errors
        self.messages = messages

        if self.errors is not None:
            self.__str__()

    def __missing_field_value__(self):
        """A field value is missing or doesn't exist."""
        pass

    def __missing_field_name__(self):
        """A field name is missing or doesn't exist."""
        pass

    def __login_issues__(self):
        """An issue with authenticating logins."""
        pass

    def __user_not_found__(self):
        """An Atlassian user cannot be found."""
        pass

    def __file_extraction__(self):
        """An issue with either downloading or uploading an attachment."""
        pass

    def __wrong_method_used__(self):
        """The data being posted is incorrect"""
        pass

    def __str__(self):
        """Return the representation of the error messages."""
        err = self.errors
        if err == "name":
            msg = self.messages or self.__missing_field_name__.__doc__
        elif err == "value":
            msg = self.messages or self.__missing_field_value__.__doc__
        elif err == "login":
            msg = self.messages or self.__login_issues__.__doc__
        elif err == "user":
            msg = self.messages or self.__user_not_found__.__doc__
        elif err == "file":
            msg = self.messages or self.__file_extraction__.__doc__
        else:
            msg = self.messages or self.__wrong_method_used__.__doc__
        return "<JiraOneError: {}>".format(msg)
