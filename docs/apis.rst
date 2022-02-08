API Documentation
=====================

.. module:: jiraone.access

endpoint
--------

This is an alias to the ``EndPoints`` class and it has many methods that can be called directly.
You can access this classmethod by calling ``jiraone.endpoint``.

.. code-block:: python

  from jiraone import LOGIN

  user = "email"
  password = "token"
  link = "https://yourinstance.atlassian.net"
  LOGIN(user=user, password=password, url=link)
  
  def priorities():
         load = LOGIN.get(endpoint.get_all_priorities())
         if load.status_code == 200:
              # some expression here
              ...
  

.. autoclass:: EndPoints
   :members:


LOGIN
--------

This is a call to the ``Credentials`` class. The way to use this class is to make a call to
``LOGIN``

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



field
---------

Alias to the ``Field`` class and it basically helps to update custom or system fields on Jira. 
You can access this class and make updates to Jira fields.

.. code-block:: python

  from jiraone import LOGIN, field, echo
  
  # previous login statement
  issue = "T6-75"
  fields = "Multiple files" # a multiselect custom field
  case_value = ["COM Row 1", "Thanos"]
  for value in case_value:
      c = field.update_field_data(data=value, find_field=fields, key_or_id=issue, options="add", show=False)
      echo(c)

.. autoclass:: Field
   :members:
   
 
 For
 -------
 The ``For`` class shows an implementation of a ``for`` loop. It comes with a special method that
 helps with dictionary indexing.
 
.. autoclass:: For
   :members:
   
 
 
.. module:: jiraone.management

manage
----------

The ``manage`` class is a alias to ``UserManagement`` class of the ``management`` module. It focuses primarily on
user and organization management. The authentication is different as it uses a bearer token.

.. code-block:: python

  from jiraone import manage

  token = "Edfj78jiXXX"
  manage.add_token(token)
  
  

.. autoclass:: UserManagement
   :members:
   
 
.. module:: jiraone.reporting


PROJECT
-----------

This is an alias to the ``Projects`` class of the ``reporting`` module. It performs various project reporting task and data extraction.

.. code-block:: python

   from jiraone import LOGIN, PROJECT
  
   # previous login statement
   jql = "project = ABC ORDER BY Rank DESC"
   PROJECT.change_log(jql)
   
   
.. autoclass:: Projects
   :members:
   
   
 USER
 -------
 
 This is an alias to the ``Users`` class of the ``reporting`` module. It contains methods that are used to easily get user details.
 
.. code-block:: python

   from jiraone import LOGIN, USER
  
   # previous login statement
   USER.get_all_users(file="user.csv", folder="USERS")
   
 
   
.. autoclass:: Users
   :members:
   
   
   
.. module:: jiraone.module

Module
---------

The ``module`` module contains functions that are specific towards certain task. Each function is designed to be as straightforward
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
