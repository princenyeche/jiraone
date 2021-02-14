# Using the API
Jiraone basically allows you to create a report based method using Atlassian REST API on your cloud infrastructure.
It uses a class method on the Endpoint class, so you can easily call the direct Atlassian API.
In generating reports, you can create functions, classes or even methods to derive the desired results.


```python
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
```


The script comes with a "User" and "Project" classes which includes basic reporting examples. The User class has a user generator,
which easily enables you to fetch all users on the instance without you programming such yourself.
All these methods and functions are accessible directly from the jiraone package.


## endpoint
***endpoint.MethodName()*** <br />
This is an alias to the `EndPoints` class and it has many methods that can be called directly. <br />
Example usage: `endpoint.myself()`, `endpoint.search_users()` <br />

## LOGIN
***LOGIN()*** <br />
This is a call to the `Credentials` class and the accepted parameters are
  * user &gt; string
  * password &gt; string
  * url &gt; string <br />
Example usage: <br />

```python
from jiraone import LOGIN

user = "email"
password = "token"
link = "https://yourinstance.atlassian.net"
LOGIN(user=user, password=password, url=link)

```

<br />

**Attributes**, available to the LOGIN alias
* LOGIN.base_url 
* LOGIN.headers 
* LOGIN.auth_requests <br />

**Methods**, available to the LOGIN alias, it returns a response object. <br />
The keyword argument of payload can be any object you want to pass to the method. Subsequently, you can pass other keyword arguments
such as `files`, `data` etc.
* LOGIN.get(url, *args, payload=None, **kwargs)
* LOGIN.post(url, *args, payload=None, **kwargs)
* LOGIN.delete(url, **kwargs)
* LOGIN.put(url, *args, payload=None, **kwargs)


## echo
***echo(object)*** <br />
This is a function which uses a copy of the PrettyPrint Class used to nicely format a represented printed result. To call, simply use the function `echo`. <br />
It accepts one required parameter, which can be any object. <br />
Example usage: <br />

 ```python
from jiraone import echo
    
data = "hello world"
echo(data)
# prints //
# 'hello world'
  ```
 <br />
 
## add_log
***add_log(message, level)*** <br />
This function is used to log messages to a log file. It accepts two required parameters `message` and `level` of which both are strings.
The function uses the logging module and writes a log, based on 3 levels. 
* debug
* info
* error <br />
The message part is a string used to denote what is written to the log and the level parameter can use any of the strings above as options.<br />
Example usage: <br />

 ```python
from jiraone import add_log
    
message = "successfully Initiated the script"
add_log(message, "info")
   ```
<br />  

## file_writer
***file_writer(folder="string", file_name="string", data=[iterable], mark="string", mode="string", content="string[bytes]")*** <br />
This function helps in creating a csv file or a normal file. It comes with the below parameters as keyword arguments <br />
  * `folder` > string: a path to the name of the folder
  * `file_name` > string: the name of the file being created.
  * `data` > iterable: an iterable data, usually in form of a list.
  * `mark` > string: helps evaluates how data is created, available options ["single", "many", "file"], by default mark is set to "single"
  * `mode` > string: file mode, available options ["a", "w", "a+", "w+", "wb"], by default the mode is set to "a+".
  * `content` > string: outputs the file in bytes. <br />
 Example usage: <br />
 
  ```python
from jiraone import file_writer
    
a_list = [1, 14, 22, "hello", "file"]
files = file_writer(folder="TEST", file_name="test.csv", data=a_list)
    
   ```

## file_reader
***file_writer(folder="string", file_name="string", mode="string", content=bool, skip=bool)*** <br />
This function helps in reading a csv file and returning a list comprehension of the data or read a byte file. Accepted
parameter include
  * `folder` > string: a path to the name of the folder
  * `file_name` > string: the name of the file being created
  * `mode` > string: file mode, available options ["r", "rb"]
  * `skip` > bool: True allows you to skip the header if the file has any. Otherwise defaults to False
  * `content` > bool: True allows you to read a byte file. By default it is set to False <br />
  Example usage: <br />
  
  ```python
from jiraone import file_reader
    
files = file_reader(folder="TEST", file_name="test.csv")
    
   ```

## path_builder
***path_builder(path="string", file_name="string")***  <br />
This function helps to build a directory path and file path then returns the file path in the directory.
parameters include
  * `path` > string: a path to declare absolute to where the script is executed.
  * `file_name` > string: the name of the file being created <br />
   Example usage: <br />
  
  ```python
from jiraone import path_builder
    
path = "Test_folder"
file = "test.csv"
dir_path = path_builder(path=path, file_name=file)
    
# output
# "Test_folder/test.csv"

   ```

## For
***For(object)*** <br />
* ***For(list)***
* ***For(dict)***
* ***For(tuple)***
* ***For(set)***
* ***For(string)***
* ***For(int)***

The `For` class is a class to show the implementation of a 'for' loop. it calls the **__iter__** magic method then the **__next__** method
and raises a StopIteration once it reaches the end of the loop. Datatype expected are list, dict, tuple, str, set or int.
It contains one required parameter called `data` which it uses to receive the various datatype and translate them into a list of items, 
retaining their own unique datatype.

It also contains a unique method called `__dictionary__()` which helps in indexing dict objects. It works the same way as any iteration.
<br />
Example usage:

```python
from jiraone import For

diction = {1: 4, "hello": "hi", "value": True, "why": False}
d = For(diction).__dictionary__(2)  # calls the 3rd item in the list

# output
# {"value": True}
```


## replacement_placeholder
***replacement_placeholder(string="", data=[list],
                            iterable=[list],
                            row=integer)***
                            <br />
 This function returns multiple string replacement. This can be used to replace multiple strings in a list where a placeholder can be identified and used
 as a marker to replace the strings.<br />
 
Example usage: <br />
```python
from jiraone import replacement_placeholder

hold = ["Hello", "John doe", "Post mortem"]
text = ["<name> <name>, welcome to the <name> of what is to come"]
cb = replacement_placeholder("<name>", text, hold, 0)
print(cb)

# output
# ["Hello John doe, welcome to the Post mortem of what is to come"]

```

## field
Alias to the `Field` class and it basically helps to update custom or system fields on Jira. It comes with the below methods. <br />

**Attributes** You have access to two vital attributes. <br />
* `field.field_type` > A dictionary of Jira's field properties.
* `field.field_search_key` > A dictionary of Jira's field search key.
<br />

**Methods** The below are the various methods that can be used. <br />
***field.search_field(find_field="string")*** <br />
This helps to search for a custom field. The paramater needed `find_field` which should be a string.

***field.get_field(find_field="string")*** <br />
This helps to search for system fields or custom fields. The paramater needed `find_field` which should be a string.

***field.update_field_data(data=[Any], find_field="string", field_type="string", key_or_id=Union[string, integer], show=[Bool], kwargs=[Any])*** <br />

This method helps with updating fields. Performs a `put` request, with the below parameters. <br />
* `data` datatype[Any] the data you're trying to process, depending on what field it could be any object.
* `find_field` datatype[String] name of the custom field or system field to find in strings.
* `field_type` datatype[String] available options - system or custom.
* `key_or_id` datatype[String or Integer] issue key or id of an issue.
* `show` datatype[Bool] allows you to print out a formatted field that was searched. Set to false, if you don't want the field data shown.
* `kwargs` datatype[String] perform other operations with keyword args
  * options arg is a string and has two values "add" or "remove".
  * query arg is a string and it can have any value that is stated on the endpoint.issue() method e.g. query="notifyUsers=false"


***field.data_load(data=[Any], s=[Any])*** <br />
* `data` any object
* `s` any object that makes it not None.

***field.multi_field(data=[Any], s="string")*** <br />
* `data` any string object data.
* `s` is a placeholder to determine the object key. Value can be "value" or "name"
  * e.g. required output [{"value": "hello"}] -> for Multicheckboxes type of field.
  * e.g. required output [{"name": "hello"}] -> for Components or Fix versions type of field.

***field.cascading(data=[String,List])*** <br />
* `data` any string or list object data.

***field.extract_issue_field_options(key_or_id=Union[string, integer], search=None, amend=None, data=Any, field_type="system")*** <br />
* `key_or_id` datatype[String, Integer] issue key or id of an issue.
* `search` datatype[Dict] issue data of an issue or issue payload.
* `amend` datatype[String] available option "add" or "remove" condition to decide action for appending.
* `data` datatype[string] our object data that will be processed.
* `field_type` datatype[String] provides decision for search parameter.Available options are "system" or "custom".

Example usage: <br />
```python
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
```


### Other variables
* `WORK_PATH`: This is a direct link to the present directory in which you're calling the script. How it works, is that it uses the present working directory of where the script you're initializing. Use this variable, if you want to create your own pathway.
