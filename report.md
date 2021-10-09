# Basic Report Usage
The script comes with some basic reporting Classes and methods which you can use to generate a report in CSV format.
currently only CSV file output is supported. other format such as JSON might be available in future.

## USER API
* Generate a report of all active users in your instance

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

* Generate a report of all user in the instance and which group do they belong to

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

* Search and find users within your cloud instance.

```python
from jiraone import LOGIN, USER

user = "email"
password = "token"
link = "https://yourinstance.atlassian.net"
LOGIN(user=user, password=password, url=link)


if __name__ == '__main__':
    # the output of the file would be absolute to the directory where this python file is being executed from
    name = "Prince Nyeche"  # displayName of a user
    # find multiple users, use a list
    # name = ["Prince Nyeche, "Prince"]
    USER.search_user(pull="active", user_type="atlassian", find_user=name)
```

* Get a mention of a cloud user.

```python
from jiraone import LOGIN, USER

user = "email"
password = "token"
link = "https://yourinstance.atlassian.net"
LOGIN(user=user, password=password, url=link)


if __name__ == '__main__':
    # the output of the file would be absolute to the directory where this python file is being executed from
    # displayName of a user, to output multiple users separate by a comman
    # name = "Prince Nyeche,Prince,John Doe"
    name = "Prince Nyeche"  
    USER.mention_user(name)
```


## PROJECT API

* Generate a report of users in your instance, who has BROWSE access to the projects on the instance.

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

* Generate a report of the number of Dashboard on the Instance, who's the owner and who it is shared with.

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


* Generate a report, get all project list and users within a project as well as their corresponding project role in the project.

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

* Generate a report, get all attachments per issue on a project or search for projects and get all attachment urls

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
    # for this, 3 keyword args are used which are key=0, attach=1,  and file=2 -> all requires an integer value.
    # PROJECT.move_attachments_across_instances(attach_file="new.csv", key=0, attach=1, file=2)
    # To download an attachment locally use
    PROJECT.download_attachments(download_path="Download", attach=1, file=2)
```

* Track the number of comments sent to a reporter on per issue and get the total sum sent by the reporter and by other users.

```python
from jiraone import LOGIN, PROJECT


user = "email"
password = "token"
link = "https://yourinstance.atlassian.net"
LOGIN(user=user, password=password, url=link)


if __name__ == '__main__':
    # the output of the file would be absolute to the directory where this python file is being executed from
    # this method uses various keyword arguments:
    # pull -> string - available options [active, inactive, both]
    # user_type -> string - available options [atlassian, customer, app, unknown]
    # find_user -> string - display name of the user you're searching for
    # duration -> string - jql function to denote days of calendar e.g. startOfWeek(-1) or startOfMonth(-1)
    # status -> string - statuses you want to check e.g Open or Closed or Open, Closed for multiple statuses check
    # file -> string - a file name to use as place_holder for user search. if not it defaults to user_file.csv
    PROJECT.get_total_comments_on_issues(find_user="Prince Nyeche", pull="active", user_type="atlassian")
```

* Generate a report of all the issue history within a project or projects

Use `LOGIN.api = False` if you want to extract the issue history from a Server instance.

```python
from jiraone import LOGIN, PROJECT

user = "email"
password = "token"
link = "https://yourinstance.atlassian.net"
# use {LOGIN.api = False} if you want to extract the issue history from a Server instance
LOGIN(user=user, password=password, url=link)

if __name__ == '__main__':
    # the output of the file would be absolute to the directory where this python file is being executed from
    jql = "project in (PYT) ORDER BY Rank DESC"  # A valid JQL query
    PROJECT.change_log(jql=jql)
```

## Module API
The API from the `jiraone.module` uses functions

* Generate a report of time in status of Jira issue.

```python
from jiraone import LOGIN, PROJECT, file_reader
from jiraone.module import time_in_status
import json

config = json.load(open('config.json'))
LOGIN(**config)

key = ["COM-12", "COM-14"]

if __name__ == "__main__":
     time_in_status(PROJECT, key, file_reader, pprint=True, is_printable=False,
     output_format="json", report_folder="STATUSPAGE", report_file="time.csv",
     status="In progress", login=LOGIN, output_filename="result")
     
# output
# result.json file
```

This function has the ability to generate the time an issue has stayed in a particular status or it can generate all the time it stays in each and every status that exists within a Jira issue. I’ll explain what each argument within the function does, so you can get a clear picture of how to use it. The standard way to call this function is the way it is shown above. First, the PROJECT alias is used as a required positional argument and within the function calls the `change_log()` method. The second argument requires an issue key. Now you can be able to pass the issue key in various formats such as below
```python
# previous statement

key = "COM-12" # as a string
key = "COM-12,COM-14" # a string separated by comma
key = 10034 # an integer denoting the issueid
key = ["COM-12", "COM-114", "TPS-14", 10024] # a list of issue keys or issue ids
key = {"jql": "project = COM ORDER BY created DESC"} # a dict using JQL
```
The third argument is file_reader function which you will need to pass or you can pass as a keyword argument as reader=file_reader. The remaining arguments can be passed as keyword arguments, pprint enables you to print out the time in status in Jira’s pretty format e.g. 13d 11h 22m 15s if it is set to True otherwise if it is not set at all, you will get the DateTime output as *13 days, 11:22:15.913* which is a time delta string of the DateTime string collected from the issue history. The output_format argument enables you to generate a report file either in *CSV* or *JSON* format. The words have to be strings and are case insensitive. E.g cSV or JsoN will output the correct file. The output_file argument basically just allows you to name the file, avoid using any extension as this will be automatically added based on the output_format. The status argument allows you to only output statuses that have that status name. For example, you want a report of only “In Progress” status, then you should write the name "In Progress" (this is case sensitive) as the value to the status argument. If left blank, the result will be all the statuses within the issues being searched. Therefore, if you want the time in status for all the statuses that exist within the Jira issues, do not set the status argument. The login argument is essential to the function as it is required for authenticating your API to the Jira issues. The `report_file` basically helps within the history generation, you do not have to set this as it is optional. The same goes for `report_folder` you do not have to set this as it is optional.

Once you run the script, you will end up with a report that looks like the one below as the output

```json
[
 {        
  "author": "Prince Nyeche",        
  "issueKey": "COM-12",        
  "status": "To Do",        
  "summary": "Workflow test 3",        
  "timeStatus": "0h 00m 19s"    
 },    
 {        
  "author": "Prince Nyeche",        
  "issueKey": "COM-14",        
  "status": "In Progress",        
  "summary": "Workflow test 3",        
  "timeStatus": "8d 6h 32m 52s"    
 }
]
```

* Update custom field or system fields using a field update function

```python
from jiraone import LOGIN, PROJECT, USER, echo, field
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
```
The above function is able to update all fields used on Jira. All you simple need to do is find the field based on it's name. If it exist, then a result will be shown for it. The field_update requires the below argument.
* field: a call to the field class needs to be passed as the first argument
* key_or_id: An issue key or issue id needs to be passed as the second argument or you can use a keyword argument.
* update: A way to update the custom field. It accepts two valid values either `add` (adds a value to a list or dict) or `remove` (removes from a value to a list or dict)
* name: The name of a field
* data: The data item we want to change which could be any data types.

Another example is given below to update multiple value set to a field. Use the `update` argument to add or remove values. Most of the fields that requires add or removing can be places in a list such as components, labels, fixversions, multicheckboxes, multiselect etc - these fields items can be places in a list as shown below to either add or remove items from it.

```python
from jiraone import LOGIN, PROJECT, USER, echo, field
from jiraone.module import field_update
import json

# a configuration file which is a dict containing keys user, password and url
config = json.load(open('config.json'))
LOGIN(**config)

key = 'ITSM-4'
name = 'Component Field'  # A Component field

if __name__ == "__main__":
     vals = ['Browser', 'Firefox']
     make = field_update(field, key, name, data=vals, update="add")
     echo(make)
     
# output
# <Response [204]>
```

```python
#...previous statement

key = 'ITSM-4'
name = 'Story Points'  # A Story point field

if __name__ == "__main__":
     vals = 3 # An integer and not string for Story Points type field
     make = field_update(field, key, name, data=vals)
     echo(make)
     
# output
# <Response [204]>
```


## Support
* For any issues or feature request, feel free to create an issue on Github or email me at support@elfapp.website
