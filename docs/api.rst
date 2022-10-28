.. _using-the-api:
Using the API
=============
.. module:: jiraone

Jiraone basically allows you to create a report based method using Atlassian REST API on your cloud infrastructure.
It uses a class method on the Endpoint class, so you can easily call the direct Atlassian API.
In generating reports, you can create functions, classes or even methods to derive the desired results.


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


The script comes with a "User" and "Project" classes which includes basic reporting examples. The User class has a user generator,
which easily enables you to fetch all users on the instance without you programming such yourself.
All these methods and functions are accessible directly from the jiraone package.


.. _endpoint:

endpoint
--------
This is an alias to the ``EndPoints`` class and it has many methods that can be called directly. 

Example usage: ``endpoint.myself()``, ``endpoint.search_users()``


.. _login:

LOGIN
--------


This is a call to the ``Credentials`` class and the accepted parameters are
  * user - string
  * password - string
  * url - string 
  * oauth - dict - An OAuth 2.0 3LO implementation
  
Example usage:

.. code-block:: python

 from jiraone import LOGIN

 user = "email"
 password = "token"
 link = "https://yourinstance.atlassian.net"
 LOGIN(user=user, password=password, url=link)


**Adding your own custom SSL or self-signed certificate**
 
  You can do this by providing a direct path to your certificate. This way, the entire jiraone library can use your self-signed certificate in performing the HTTP request.
  
  For example::
   
   import os
   
   your_cert_path = "direct_absolute_path/to/cert"
   os.environ["REQUESTS_CA_BUNDLE"] = your_cert_path
   # before calling jiraone statements
 
  
  
**Attributes**, available to the LOGIN alias

* ``LOGIN.base_url``

* ``LOGIN.headers``

* ``LOGIN.password``

* ``LOGIN.user``

* ``LOGIN.api`` <default> to True - This helps with changing the api version from 3 to use the latest version.

* ``LOGIN.auth_requests`` 

* ``LOGIN.save_oauth`` Is a property value of a saved OAuth data session

* ``LOGIN.instance_name`` represents the name of an instance when using OAuth

* ``LOGIN.session`` represents the session from the initialization

* ``LOGIN.auth2_0`` represents the oauth attribute for the property setter.

**Methods**, available to the LOGIN alias, it returns a response object.

The keyword argument of payload can be any json object you want to pass to the method. Subsequently, you can pass other keyword arguments
such as ``files``, ``data`` etc.

* ``LOGIN.get(url, *args, payload=None, **kwargs)``

* ``LOGIN.post(url, *args, payload=None, **kwargs)``

* ``LOGIN.delete(url, **kwargs)``

* ``LOGIN.put(url, *args, payload=None, **kwargs)``

* ``LOGIN.custom_method(*args, **kwargs)``


.. note::
 
  If you want to save the OAuth data session, you will need to call the ``LOGIN.save_oauth`` property. 
  This property is set once an OAuth authentication  has been initialized. If an OAuth session is not created, the value won't return anything.
  
  Also, if you want to save the OAuth data session into a ``DB`` of ``file``, you can call this property value ``LOGIN.save_oauth``. 
  To access the saved oauth session, please see the example used by the oauth method. You will need to push the data to the property setter using ``LOGIN.save_oauth``.



.. _echo:
echo
--------
.. autofunction:: echo

This is a function which uses a copy of the PrettyPrint class used to nicely format a represented printed result. To call, simply use the function ``echo``.
It accepts one required parameter, which can be any object. 
Example usage:

.. code-block:: python

     from jiraone import echo
    
     data = "hello world"
     echo(data)
     # prints //
     # 'hello world'


.. _add_log:
add_log
--------

.. autofunction:: add_log

This function is used to log messages to a log file. It accepts two required parameters ``message`` and ``level`` of which both are strings.
The function uses the logging module and writes a log, based on 3 levels. 

* ``debug``

* ``info``

* ``error``

The message part is a string used to denote what is written to the log and the level parameter can use any of the strings above as options.
Example usage: 

.. code-block:: python

 from jiraone import add_log
    
 message = "successfully Initiated the script"
 add_log(message, "info")
  


.. _file_writer:
file_writer
-------------

.. autofunction:: file_writer

This function helps in creating a csv file or a normal file. It comes with the below parameters as keyword arguments 
  * ``folder``: string - a path to the name of the folder
  * ``file_name``:  string - the name of the file being created.
  * ``data``: iterable - an iterable data, usually in form of a list.
  * ``mark``: string - helps evaluates how data is created, available options ["single", "many", "file"], by default mark is set to "single"
  * ``mode``: string - file mode, available options ["a", "w", "a+", "w+", "wb"], by default the mode is set to "a+".
  * ``content``: string - outputs the file in bytes.
  * ``delimiter``: string - a file separator. Defaults to ","
  * ``encoding``: string - a string of character encoding. Defaults to "utf-8"
 Example usage:
 
.. code-block:: python

 from jiraone import file_writer
    
 a_list = [1, 14, 22, "hello", "file"]
 files = file_writer(folder="TEST", file_name="test.csv", data=a_list)
    


.. _file_reader:
file_reader
------------
 
.. autofunction:: file_reader

This function helps in reading a csv file and returning a list comprehension of the data or read a byte file. Accepted
parameter include
  * ``folder``: string - a path to the name of the folder
  * ``file_name``:  string - the name of the file being created
  * ``mode``: string - file mode, available options ["r", "rb"]
  * ``skip``: bool - True allows you to skip the header if the file has any. Otherwise defaults to False
  * ``content``: bool - True allows you to read a byte file. By default it is set to False
  * ``encoding``: string - standard encoding strings. e.g “utf-8”.
  * ``delimter``: string - a file separator. Defaults to ","
  
  Example usage: 
  
.. code-block:: python

 from jiraone import file_reader
    
 files = file_reader(folder="TEST", file_name="test.csv")
    


.. _path_builder:
path_builder
-------------

.. autofunction:: path_builder


This function helps to build a directory path and file path then returns the file path in the directory.
parameters include

  * ``path``: string - a path to declare absolute to where the script is executed.
  * ``file_name``:  string - the name of the file being created
  
   Example usage:
  
.. code-block:: python

 from jiraone import path_builder
    
 path = "Test_folder"
 file = "test.csv"
 dir_path = path_builder(path=path, file_name=file)
    
 # output
 # "Test_folder/test.csv"


.. _for:

For
------

It contains one required parameter called ``data`` which it uses to receive the various datatype and translate them into a list of items, 
retaining their own unique datatype.

It also contains a unique method called ``__dictionary__()`` which helps in indexing dict objects. It works the same way as any iteration.


Example usage:

.. code-block:: python

 from jiraone import For

 diction = {1: 4, "hello": "hi", "value": True, "why": False}
 d = For(diction).__dictionary__(2)  # calls the 3rd item in the list

 # output
 # {"value": True}



.. delete_attachments:
delete_attachments
----------------------------

.. autofunction:: delete_attachments

Using Search Method
~~~~~~~~~~~~~~~~~~~~~~~~~

If the ``file`` argument is provided, the search argument is ignored. If the file argument is not provided the search argument has to be provided else an error will be returned. e.g.

.. code-block:: python

 from jiraone import LOGIN, delete_attachments
 import json

 config = json.load(open('config.json'))
 LOGIN(**config)

 ext = [".png", ".pdf"]
 users = ["5abcXXX", "617bcvXXX"]
 size = ">30MB"
 jql = {"jql": "project in (COM) ORDER BY Rank DESC"}
 delete_attachments(search=jql, extension=ext, by_user=users, by_size=size)


The above example is one of the ways you can make a request. You can make a request using the below search criteria

.. code-block:: python

 # previous expression

 key = "COM-120" # a string as issue key
 key = "COM-120,TP-15" # a string separated by comma
 key = ["COM-120", "IP-18", 10034] # a list of issue keys or issue id
 key = {"jql": "project in (COM) ORDER BY Rank DESC"} # a dict with a valid jql
 
The above will enable you to search for viable issues that has an attachment value. The extension argument can be used as below

.. code-block:: python

 # previous expression

 ext = ".png" # a string
 ext = ".png,.pdf" a string separated by comma
 ext = [".png", ".zip", ".csv"] # a list of extensions
 
You can also use it without the “dot” prefix on the extension but make sure that if the dot is not being used for multiple extensions either by string or list, the dot prefix is not maintained at all. E.g

*Valid* :check_mark:

.. code-block:: python

 # previous expression
 ext = [".png", ".zip", ".csv"] # a list of extensions
 
*Valid* :check_mark:

.. code-block:: python

 # previous expression
 ext = ["png", "zip", "csv"] # a list of extensions
 ext = "png,zip,pdf" # a string separated by comma

*Invalid* :check_mark:

.. code-block:: python

 # previous expression
 ext = [".png", "zip", ".csv"] # a list of extension
 
In the case of the invalid example, notice that one of the extensions doesn’t have a “dot” prefix! When such happens the file extension is skipped and won’t be deleted in the final execution of the API.

The ``by_user`` argument allows you to use accountId to filter the deletion by such users. This argument expects a list of users

.. code-block:: python

 # previous expression

 users = ["5abcXXX", "617bcvXXX"]
 
When the user that matches is found, then the deletion will occur.

The ``by_size`` argument helps with deletion by byte size. You can specify the limit by using the below format. The acceptable format for by_size uses this mechanism

size = [condition][number][byte type]

* Condition uses the *greater than (>)* or *lesser than (<)* symbols

* Number could be any digit that you can come up with.

* Byte type refers to the byte size allocation. Either in *kb*, *mb*, *gb* or blank representing sizes in *bytes*

.. code-block:: python
 
 # previous expression

 size = ">12mb" # greater than 12mb in size
 size = "<150mb" # lesser than 150mb in size
 size = ">400kb" # greater than 400kb in size
 size = "<20000" # lesser than 20000 bytes without the suffix byte type specified

Using the ``by_date`` argument within this function helps to determine if and when an attachment should be removed. It uses the initiator's current local time derived from your machine to determine the time and date; down to the last second. Then it compares, that current time to the issue time when the attachment was created and then determine a time delta of the difference. If it can determine that the time period or range is lesser than the DateTime the attachment existed, then it returns true otherwise returns false. You can make the request by performing any of the below tasks.

.. code-block:: python
 
 # previous expression

 dates = "3 days ago"
 dates = "3 months ago" # you can say 3 months
 dates = "15 weeks" # the ago part can be left out and it won't matter.
 
The accepted format of using this argument is given below and only strings are accepted.

dates = "[number] <space> [time_info] <space> ago"

The ago part is optional (i.e not needed but looks visually pleasing) but the number and time_info part are crucial. These are the expected values for time_info

* ``minute or minutes`` , ``hour or hours``, ``day or days``, ``week or weeks``, ``month or months``, ``year or years``

Depending on the context and which one makes the most accurate depiction in the English language.

.. code-block:: python

 # previous expression

 dates = "14 hours ago"
 dates = "1 year ago"
 
Besides using the standard way to call this function, you can always mix and match your search criteria using these four arguments. ``extension``, ``by_user``, ``by_size``, ``by_date``
The hierarchy follows the same way as they are arranged above.


Using File Method
~~~~~~~~~~~~~~~~~~~~~~~~~

Subsequently, if you do not want to run a search, you can perform an entire export of your filter query from your Jira UI by navigating to your *Filter > Advanced* issue search, typing your query to get the desired result and click the export CSV all fields.

You do not have to edit the file or change the format in any way. If you’ve exported it as an xlsx file or you’ve modified the file by removing other columns. Please add a delimiter argument and use “;” as the delimiter. Always ensure that the headers are present and not removed also. Also, ensure that the “Attachment” and “Issue key” columns are always present in the file.

.. code-block:: python

 # previous login statement

 ext = [".csv", ".mov", ".png"]
 file = "Jira-export.csv"
 delete_attachments(file=file, extension=ext)
 
Example with delimiter parameter.
 
.. code-block:: python

 # previous login statement with variable options

 delete_attachments(file=file, extension=ext, delimiter=";")


You can only filter by extension when using the file method.

Turning on Safe mode
If you just want to test the function without actually deleting any attachments for both the file and search method, you can switch the argument delete into False and that will turn on safe mode. E.g.

.. code-block:: python

 # previous login statement with variable options

 delete_attachments(file=file, extension=ext, delimiter=";", delete=False)
 # result
 # Safe mode on: Attachment will not be deleted "jira_workflow_vid.mp4" | Key: COM-701
 
The same argument is available when you use the search method.

.. code-block:: python

 # previous login statement with variable options

 delete_attachments(search=jql, delete=False)
 # result
 # Safe mode on: Attachment will not be deleted "jira_workflow_vid.mp4" | Key: COM-701

When safe mode is on, all filtering is ignored.


.. _replacement_placeholder:
replacement_placeholder
------------------------
 
.. autofunction:: replacement_placeholder


 This function returns multiple string replacement. This can be used to replace multiple strings in a list where a placeholder can be identified and used
 as a marker to replace the strings.
 
Example usage: 

.. code-block:: python

 from jiraone import replacement_placeholder

 hold = ["Hello", "John doe", "Post mortem"]
 text = ["<name> <name>, welcome to the <name> of what is to come"]
 cb = replacement_placeholder("<name>", text, hold, 0)
 print(cb)

 # output
 # ["Hello John doe, welcome to the Post mortem of what is to come"]
 
 
.. _field:

field
--------
Alias to the ``Field`` class and it basically helps to update custom or system fields on Jira. It comes with the below methods. 

   
Example usage: 

.. code-block:: python

 from jiraone import field, echo, LOGIN

 user = "email"
 password = "token"
 link = "https://yourinstance.atlassian.net"
 LOGIN(user=user, password=password, url=link)

 issue = "T6-75"
 fields = "Multiple files" # a multiselect custom field
 case_value = ["COM Row 1", "Thanos"]
 for value in case_value:
     c = field.update_field_data(data=value, find_field=fields, key_or_id=issue, options="add", show=False)
     echo(c)

 # output
 # < Response[204] >

        
``field.get_field_value(name='String', keys='Union[string, integer]')`` 

* ``name`` datatype[String] a name of the custom field.
* ``keys`` datatype[String, Integer] issue key or id of an issue.
        
.. code-block:: python

 from jiraone import field, echo
 # ...previous login statements
 # it expects the field name as the first parameter and the issue key where the field is used as the second parameter
 value = field.get_field_value("Labels", "COM-15")
 echo(value) 


.. _comment:

comment
--------


* POST a comment to a Jira issue and mention users sequentially on a comment.

.. code-block:: python

 from jiraone import LOGIN, USER, comment

 user = "email"
 password = "token"
 link = "https://yourinstance.atlassian.net"
 LOGIN(user=user, password=password, url=link)

 key = "COM-42"
 name = "Prince Nyeche,Prince"
 text = """
        <user> please can you help to check the docker environment? Ping <user> to help out.
        """
 comment(key, method="post", text_block=text, placer="<user>", mention=USER.mention_user(name), event=True)



.. _manage:

manage
--------

The ``manage`` API brings organization and user REST API features to jiraone. With this API, you can manage your organization and users by making calls to the entire API endpoints used for organization management.


This API requires that you enter a API token for your organization.
                
.. code-block:: python

 from jiraone import manage

 token = "Edfj78jiXXX"
 manage.add_token(token)



Returns the set of permissions you have for managing the specified Atlassian account. The `account_id` is required and query is an ``Array<string>`` which can be any of the values below:

* Valid values: ``profile``, ``profile.write``, ``profile.read``, ``email.set``, ``lifecycle.enablement``, ``apiToken.read``, ``apiToken.delete``

``manage_profile(account_id: str, method: str = "GET", **kwargs_: t.Any)``

You can be able to call various methods by altering the ``method`` keyword argument

* ``GET`` request: Returns information about a single Atlassian account by ID by using a "GET" request.

* ``PATCH`` request: Updates fields in a user account.
     * Body parameter
         * Any or all user object this is value
            e.g. {"name": "Lila User", "nickname": "marshmallow"}
                
* ``PUT`` request: Sets the specified user's email address.
     * Body parameter
          e.g. {"email": "prince.nyeche@elfapp.website"}
                


Gets the API tokens owned by the specified user or deletes a specifid API token by ID.
                  


Disables the specified user account. The permission to make use of this resource is exposed by the lifecycle.enablement privilege. 
OR
Enables the specified user account.The permission to make use of this resource is exposed by the lifecycle.enablement privilege

.. code-block:: python

 from jiraone import manage

 token = "Edfj78jiXXX"
 account_id = "5bc7uXXX"
 payload = {"message": "On 6-month suspension"} # A payload needs to be passed for the endpoint to work
 manage.add_token(token)
 manage.manage_user(account_id, json=payload) # By default it is set to disable a user
 # manage.manage_user(account_id, json=payload, disable=False) # Changing disable=False enables back the user

 # output
 # <Response 204>
  
 
.. warning::
 
  The token used by the ``manage`` API is completely different from the one used with the basic authentication method. 
  Therefore, ensure that the right token is used when making either calls.
  

GET request for the organization API. Returns organization users, domains, policies and events based on different keyword arguments passed to the method.

The ``filter_by`` arguments accepts 4 valid options which as ``users``, ``domains``, ``policies``, and ``events``. 
The ``action`` argument allows a certain action for the events filter_by option. When set ``action=True`` it returns the event actions rather than a list of events.

The ``kwargs`` argument accepts valid response arguments such as ``json``, ``data`` etc which can be used as body parameter when making the request.
                
                
.. code-block:: python

 from jiraone import manage

 token = "Edfj78jiXXX"
 manage.add_token(token)
 manage.get_organization(filter_by="users")

 # output
 # <Response 204>


Get the data from the list of policies

.. code-block:: python

 from jiraone import manage, echo

 token = "Edfj78jiXXX"
 manage.add_token(token)
 for policy in manage.policy_id:
     deploy = manage.get_organization(filter_by="policies", policy_id=policy)
     echo(deploy)

 # output
 # <Response 204>

                

Create, put and delete organization data, create a policy for an org, send a post request by using ``method="post"`` as keyword args.Update a policy for an org.
Send a put request by using ``method="put"`` as keyword args.
The `method` argument accepts "put", "post" or "delete" (case insensitive)
  
  
.. _other_variables:
Other variables
--------

* ``WORK_PATH``: This is a direct link to the present directory in which you're calling the script. How it works, is that it uses the present working directory of where the script you're initializing. Use this variable, if you want to create your own pathway.
