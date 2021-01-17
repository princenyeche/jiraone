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
* `endpoint` -&gt; This is an alias to the `EndPoints` class and it has many methods that can be called directly
  * example usage: `endpoint.myself()`, `endpoint.search_users()`
* `echo` -&gt; A copy of the PrettyPrint Class used to nicely format a represented printed result. to call, simply use the function `echo`
  * example usage: 
     ```python
    from jiraone import echo
    
    data = "hello world"
    echo(data)
    # prints //
    # 'hello world'
     ```
* `add_log` -&gt; This function is used to log messages to a log file. it accepts two parameters `message` and `level`.
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
* `file_writer` -&gt; This function helps in creating a csv file or a normal file. it comes with the below parameters 
  * `folder` -> string: a path to the name of the folder
  * `file_name` -> string: the name of the file being created
  * `data` -> iterable: an iterable data.
  * `mark` -> string: helps evaluates how data is created, available options ["single", "many", "file"]
  * `mode` -> string: file mode, available options ["a", "w", "a+", "w+", "wb"]
  * `content` -> string: outputs the file in bytes.
* `file_reader`  -&gt; This function helps in reading a csv file and returning a list comprehension of the data or read a byte file. Accepted
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

## Using the API
Jiraone basically allows you to create a report based method using Atlassian REST API on your cloud infrastructure.
it uses a class method on the Endpoint Class, so you can easily call the direct Atlassian API.
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
The Script comes with a User and Project Classes which includes basic reporting examples. The User class has a user generator,
which easily enables you to fetch all users on the instance without you programming such yourself.
All these methods and functions are accessible directly from the jiraone package.

## Basic Report Usage
The script comes with some basic reporting Classes and methods which you can use to generate a report in CSV format.
currently only CSV file output is supported. other format such as JSON might be available in future.
* generate a report of all active users in your instance
```python
from jiraone import LOGIN, USER

user = "email"
password = "token"
link = "https://yourinstance.atlassian.net"
LOGIN(user=user, password=password, url=link)


if __name__ == '__main__':
    # the output of the file would be absolute to the directory where this python file is being executed from
    USER.get_all_users(pull="active", user_type="atlassian", file="user_file.csv")
```
* generate a report of users in your instance, who has BROWSE access to the projects on the instance.
```python
from jiraone import LOGIN, PROJECT

user = "email"
password = "token"
link = "https://yourinstance.atlassian.net"
LOGIN(user=user, password=password, url=link)


if __name__ == '__main__':
    # the output of the file would be absolute to the directory where this python file is being executed from
    PROJECT.projects_accessible_by_users("expand=insight,description", "searchBy=key,name", permission="BROWSE",
                                        pull="active", user_type="atlassian")
```
* generate a report of the number of Dashboard on the Instance, who's the owner and who it is shared with.
```python
from jiraone import LOGIN, PROJECT

user = "email"
password = "token"
link = "https://yourinstance.atlassian.net"
LOGIN(user=user, password=password, url=link)


if __name__ == '__main__':
    # the output of the file would be absolute to the directory where this python file is being executed from
    PROJECT.dashboards_shared_with()
```
* generate a report of all user in the instance and which group do they belong to
```python
from jiraone import LOGIN, USER

user = "email"
password = "token"
link = "https://yourinstance.atlassian.net"
LOGIN(user=user, password=password, url=link)


if __name__ == '__main__':
    # the output of the file would be absolute to the directory where this python file is being executed from
    USER.get_all_users_group(pull="active", user_type="atlassian")
```

* generate a report, get all project list and users within a project as well as their corresponding project role in the project.
```python
from jiraone import LOGIN, PROJECT

user = "email"
password = "token"
link = "https://yourinstance.atlassian.net"
LOGIN(user=user, password=password, url=link)


if __name__ == '__main__':
    # the output of the file would be absolute to the directory where this python file is being executed from
    PROJECT.get_all_roles_for_projects(pull="active", user_type="atlassian")
```

* generate a report, get all attachments per issue on a project or search for projects and get all attachment urls

```python
from jiraone import LOGIN, PROJECT

user = "email"
password = "token"
link = "https://yourinstance.atlassian.net"
LOGIN(user=user, password=password, url=link)


if __name__ == '__main__':
    # the output of the file would be absolute to the directory where this python file is being executed from
    # you can use any valid jql query
    jql = "project%20in%20(COM%2C%20PYT)%20order%20by%20created%20DESC"
    PROJECT.get_attachments_on_projects(query=jql)
```

* Transfer a file across instances or download a file to your local drive from an Instance

```python
from jiraone import LOGIN, PROJECT
from threading import Thread


user = "email"
password = "token"
link = "https://yourinstance.atlassian.net"
LOGIN(user=user, password=password, url=link)


if __name__ == '__main__':
    # the output of the file would be absolute to the directory where this python file is being executed from
    jql = "project%20in%20(COM%2C%20PYT)%20order%20by%20created%20DESC"
    # the below method, helps you download a report of a list of files per issue on a project or on projects
    Thread(target=PROJECT.get_attachments_on_projects(query=jql)).start()
    # afterwards, you can use the below method to move attachments across instances without downloading it
    PROJECT.move_attachments_across_instances()
    # if you're using your own file structure say a csv file, you need to identify the index of the attachment
    # for this, 3 keyword args are use key=0, attach=1,  and file=2 -> all requires an integer value.
    # PROJECT.move_attachments_across_instances(attach_file="new.csv", key=0, attach=1, file=2)
    # To download an attachment locally use
    PROJECT.download_attachments(download_path="Download", attach=1, file=2)
```


## Support
* For any issues or feature request, feel free to create an issue on Github or email me at support@elfapp.website
