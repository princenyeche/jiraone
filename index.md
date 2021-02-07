[![Codacy Badge](https://app.codacy.com/project/badge/Grade/86f1594e0ac3406aa9609c4cd7c70642)](https://www.codacy.com/gh/princenyeche/atlassian-cloud-api/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=princenyeche/atlassian-cloud-api&amp;utm_campaign=Badge_Grade)

# Jira one
A REST API Implementation to Jira Cloud APIs for creating reports and for performing other Jira queries.

## Configurations
Install using `pip`. you have to be on python >= 3.6.x in order to utilize this script.
```bash
pip install jiraone
```

## Classes, functions and methods
Jiraone comes with various classes, functions and methods. Aliases as well, are used to represent
links to classes and functions. The major ones to take note of are the below
* `LOGIN` -&gt; This is a call to the `Credentials` class and the accepted parameters are
  * user -&gt; string
  * password -&gt; string
  * url -&gt; string
  * example usage: LOGIN(user="username", password="token", url="http://example.com")
* `endpoint` -&gt; This is an alias to the `EndPoints` class and has many methods that can be called directly
  * example usage: `endpoint.myself()`, `endpoint.search_users()`
* `echo` -&gt; A copy of the PrettyPrint Class used to nicely format a printed result. to call, simply use the function `echo`
  * example usage: 
     ```python
    from jiraone import echo
    
    data = "hello world"
    echo(data)
    # prints //
    # 'hello world'
     ```
* `add_log` -&gt; This is function is used log messages to a log file. it accepts two parameters `message` and `level`.
the function uses the logging module and writes a log, based on 3 levels. "debug", "info" or "error". The message part
is a string used to denote what is written to the log.
  * example usage:
     ```python
    from jiraone import add_log
    
    message = "successfully Initiated the script"
    add_log(message, "info")
     ```
* `WORK_PATH` -&gt; This is simply the absolute path to where all files used or created in conjunction to the path where the script is
being called from.
* `PROJECT` -&gt; This is an alias to the `Project` class and it includes other methods that helps in quickly generating a
desired report.
* `USER` -&gt; This is an alias to the `User` class and it includes other methods that helps in quickly generating a
desired report.
* `file_writer` -&gt; This function helps in creating a csv file. it comes with the below parameters 
  * `folder` -> string: a path to the name of the folder
  * `file_name` -> string: the name of the file being created
  * `data` -> iterable: an iterable data of any sort.
  * `mark` -> string: helps evaluates how data is created, available options ["single", "many", "file"]
  * `mode` -> string: file mode, available options ["a", "w", "a+", "w+", "wb"]
  * `content` -> string: outputs the file in bytes.
* `file_reader`  -&gt; This function helps in reading a csv file and returning a list comprehension of the data. Accepted
parameter include
  * `folder` -> string: a path to the name of the folder
  * `file_name` -> string: the name of the file being created
  * `mode` -> string: file mode, available options ["r", "rb"]
  * `skip` -> bool: True allows you to skip the header if the file has any. otherwise defaults to False
  * `content` -> bool: True allows you to read a byte file.
* `path_builder` -&gt; This function helps to build a directory path and file path then returns the file path in the directory.
parameters include
  * `path` -> string: a path to declare absolute to where the script is executed.
  * `file_name` -> string: the name of the file being created

For further knowledge on how to use the classes, methods or functions. Open the jiraone package and read the docstring on the
aforementioned methods or functions above to get further information.

# Directory
* [Using the API](https://princenyeche.github.io/atlassian-cloud-api/api#using-the-api)
  * [endpoint](https://princenyeche.github.io/atlassian-cloud-api/api#endpoint)
  * [LOGIN](https://princenyeche.github.io/atlassian-cloud-api/api#login)
  * [echo](https://princenyeche.github.io/atlassian-cloud-api/api#echo)
  * [add_log](https://princenyeche.github.io/atlassian-cloud-api/api#add-log)
  * [file_writer](https://princenyeche.github.io/atlassian-cloud-api/api#file-writer)
  * [file_reader](https://princenyeche.github.io/atlassian-cloud-api/api#file-reader)
  * [path_builder](https://princenyeche.github.io/atlassian-cloud-api/api#path-builder)
  * [For](https://princenyeche.github.io/atlassian-cloud-api/api#for)
  * [replacement_placeholder](https://princenyeche.github.io/atlassian-cloud-api/api#replacement-placeholder)
* [Basic report usage](https://princenyeche.github.io/atlassian-cloud-api/report#basic-report-usage)
  * [PROJECT API](https://princenyeche.github.io/atlassian-cloud-api/report#project-api)
  * [USER API](https://princenyeche.github.io/atlassian-cloud-api/report#user-api)
  * [Support](https://princenyeche.github.io/atlassian-cloud-api/report#support)
