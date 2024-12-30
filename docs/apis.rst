API Documentation
=====================

.. module:: jiraone.access


.. _endpoint-class:
endpoint
--------

This is an alias to the :ref:`endpoint-class` class and it has many methods that can be called directly.
You can access this classmethod by calling ``jiraone.endpoint``.

.. code-block:: python

  from jiraone import LOGIN, endpoint

  user = "email"
  password = "token"
  link = "https://yourinstance.atlassian.net"
  LOGIN(user=user, password=password, url=link)

  def priorities():
         load = LOGIN.get(endpoint.get_all_priorities())
         if load.status_code == 200:
              # some expression here
              ...

.. note::

The :ref:`endpoint-class` gives a base framework for utilising Atlassian API. It does not perform any form of complex data collection or modification. It only applies HTTP requests to retrieve Jira data and returns that data as a response object when combined with jiraone's request functions. For example, the sample code above shows a typical way these functions can be used. In terms of pagination, you must construct your own to retrieve the data using either a ``for`` or ``while`` loop depending on what context the information retrieval may be. The API of the :ref:`endpoint-class` does not produce a payload with all data, rather it will only give a subset of that data and if the retrieval of all data is required, use a loop to get all data.

.. autoclass:: EndPoints
   :members:


.. _credential-class:

LOGIN
--------

This is a call to the :ref:`credential-class` class. The way to use this class is to make a call to
:ref:`login`

.. code-block:: python

  from jiraone import LOGIN

  user = "email"
  password = "token"
  link = "https://yourinstance.atlassian.net"
  LOGIN(user=user, password=password, url=link)

Once a login session starts, you can join other classes and make a call directly to other objects.

.. code-block:: python

  from jiraone import LOGIN, endpoint

  # previous login statement
  LOGIN.get(endpoint.myself())



.. autoclass:: Credentials
   :members:


.. _field-class:

field
---------

Alias to the :ref:`field-class` class and it basically helps to update custom or system fields on Jira.
You can access this class and make updates to Jira fields.

.. code-block:: python

  from jiraone import LOGIN, field, echo

  # previous login statement
  issue = "T6-75"
  fields = "Multiple files" # a multi-select custom field
  case_value = ["COM Row 1", "Thanos"]
  for value in case_value:
      c = field.update_field_data(data=value, find_field=fields, key_or_id=issue, options="add", show=False)
      echo(c)


.. autoclass:: Field
   :members:


.. _for-class:

For
-------
 The :ref:`for-class` class shows an implementation of a ``for`` loop. It comes with a special method that
 helps with dictionary indexing.



.. autoclass:: For
   :members:




.. module:: jiraone.management

manage
----------

The :ref:`manage` class is an alias to the :ref:`usermanage-class` class of the ``management`` module. It focuses primarily on
user and organization management. The authentication is different as it uses a bearer token.

.. code-block:: python

  from jiraone import manage

  token = "Edfj78jiXXX"
  manage.add_token(token)


.. _usermanage-class:

.. autoclass:: UserManagement
   :members:


.. module:: jiraone.reporting


.. _project-class:

PROJECT
-----------

This is an alias to the :ref:`project-class` class of the ``reporting`` module. It performs various project reporting task and data extraction.

.. code-block:: python

   from jiraone import LOGIN, PROJECT

   # previous login statement
   jql = "project = ABC ORDER BY Rank DESC"
   PROJECT.change_log(jql)



.. autoclass:: Projects
   :members:


.. _user-class:

USER
------

 This is an alias to the :ref:`user-class` class of the ``reporting`` module. It contains methods that are used to easily get user details.

.. code-block:: python

   from jiraone import LOGIN, USER

   # previous login statement
   USER.get_all_users(file="user.csv", folder="USERS")



.. autoclass:: Users
   :members:


.. _module-api:

.. module:: jiraone.module

Module
---------

The ``module`` module contains functions that are specific towards a certain task. Each function is designed to be as straightforward
as possible, so you can easily make calls to Jira's endpoint and get the required data.

.. code-block:: python

 from jiraone import LOGIN, USER, echo, field
 from jiraone.module import field_update
 import json

 # a configuration file which is a dict containing keys user, password and url
 config = json.load(open('config.json'))
 LOGIN(**config)

 key = 'ITSM-4'
 name = 'Last Update User'  # A single user picker field

 if __name__ == "__main__":
     change = USER.search_user('Prince Nyeche')[0].get('accountId')
     make = field_update(field, key, name, data=change)
     echo(make)

 # output
 # <Response [204]>


.. autofunction:: field_update

.. autofunction:: time_in_status

.. autofunction:: bulk_change_email

.. autofunction:: bulk_change_swap_email


.. module:: jiraone.utils


.. _dotnotation-class:

Utils
---------


.. autoclass:: DotNotation
   :members:

This ``DotNotation`` class provides the ability to use a dot notation on any dict object. Making it easier when working with dictionary objects.
Examples below

.. code-block:: python

    from jiraone.utils import DotNotation

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

.. note::

   When loading a list of dictionaries, please refer to the second example as shown on the above code. The dictionary needs to be assigned to a key (any naming convention will do) to get the value. Failure will result in an error.


.. autoclass:: DateFormat
    :members:

The ``DateFormat`` class provides the ability to construct datetime string directive which is used in Python's datetime class.

.. code-block:: python

    from jiraone.utils import DateFormat

    my_date = DateFormat.dd_MM_YYYY_hh_MM_AM_PM

.. autofunction:: process_executor

The ``process_executor`` helps to generate multiple threads used to make HTTP requests. To properly use this function,
you should pass a function which has an argument in a ``for`` loop to begin the iteration. You can increase the number of
threads to start with by increasing the ``workers`` argument

.. code-block:: python

    from jiraone.utils import process_executor

    # a function called extract_issues(data)
    # list_items a list of data
    for items in list_items
        process_executor(extract_issues, data=items)


.. autofunction:: validate_on_error

.. autofunction:: validate_argument_name
