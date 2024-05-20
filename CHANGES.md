# Jira one change log

**Release 0.8.4** - 2024-05-20

Thanks to [@huyz](https://github.com/huyz) for the below fixes and improvements to v0.8.4

Fixes:
- 🐛 `get_attachments_on_projects`: Overwrite attachment file by default
- 🐛 `json_field_builder`: check if `sprint_custom_id` is None
- 🐛 `path_builder`: handle multi-dir base_dir
- 🐛 `download_attachments`: avoid conflicts/overwrites by isolating attachments (helps with https://github.com/princenyeche/jiraone/issues/112)
  
Improvements:
- ✨ `download_attachments`: make defaults and behaviour match `get_attachments_on_projects`

Features:
- ✨ `download_attachments`: support `create_html_directors` option (resolves https://github.com/princenyeche/jiraone/issues/112)
- ✨ `download_attachments`: support `overwrite=False` option (to speed up incremental backups)


**Release 0.8.3** - 2024-04-01
* Fixing the CSV change file type and merge_files to run without JQL
* Added a new endpoint to `runbackup`


**Release 0.8.2** - 2024-01-02
* Minor fix to `process_executor` function with invalid arguments


**Release 0.8.1** - 2024-01-01
### Minor update #123
- Fix to issue reported on #124
- Corrected the documentation
- Minimized arguments on each method or function to max 5, then the rest are called via keyword arguments
- Added a new function for argument validation called `validate_argument_name`
- v0.8.0 and v0.8.1 are practically the same.


**Release 0.7.9** - 2023-12-23
### Minor update #115
* Update to `time_in_status` function to include timestamp in UTC
* Update to `issue_export` method for better performance and caching
* Fix to `field` class in Server/DC Jira preventing key error
* Added to `async_change_log` method which now supports multiprocessing and/or threading
```python
# import statement
PROJECT.async_change_log(
               jql, folder="TEST", file="sample.csv", flush=10
            )
```

* Added new methods to `endpoint` alias for issuetype scheme, security scheme etc
* Added tests for all the major functions/methods for CI/CD process
* Added requirement for Python 3.8.x and above to run jiraone
* Removed deprecated method `get_attachment_meta_data` from `endpoint` constant as this has been active for more than 2 years.
* Removed duplicated URL link in code for `task`, `issue_watchers`, and `issue_votes`  method in `endpoint` constant.


**Release 0.7.8** - 2023-07-04
### Minor update #113
* Fix to management API for organization management.


**Release 0.7.7** - 2023-06-14
### Minor update #111
* Added minor updates to the `export_issues` method. Corrected some few grammatical errors

**Release 0.7.6** - 2023-05-27
### Minor update #110
* Added multiple arguments to the `issue_export` method
  * It is now possible to perform export in JSON format
  * Added field exclusion and inclusion in CSV format export
* Added new methods `get_project_versions` and `issue_link_types` to access.py module
* Added a `process_executor` function, regular express constants and a `DateFormat` class to
the utils module of jiraone.
* Added examples in the documentation


**Release 0.7.5** - 2023-03-16
### Update #109
* Added a new condition to using encoding argument in `file_writer` in text mode
* Added examples in documentation


**Release 0.7.4** - 2023-03-13
### Update #107
* Reformatting entire module to use **black**
* Patch to `PROJECT.export_issues` method, added two new arguments `encoding` and `errors` which should help in character encoding formatting
* Added new methods to `endpoint` which are `server_info`, and `project_avatar`
* Added new info to documentation


**Release 0.7.3** - 2022-10-28
### Update #98
* Patch to file descriptor error in windows machine. Thanks to [@NomadSU](https://github.com/NomadSU)
* Patch to file_writer encoding. This will help to prevent any encoding errors that might happen due to non utf-8 encoding use cases.
* Added a new method `LOGIN.from_jira()` which takes an instance of the `jira` object from the python jira package.
  * This allows the ability to access jira's object methods, classes and properties. Making it possible to combine both
   jiraone's and jira's packages as one. Please note this will only work with basic authentication as of now!

Example:
```python
from jira import JIRA
from jiraone import LOGIN, endpoint

my_jira = JIRA(server="https://nexusfive.atlassian.net",
                 basic_auth=("prince@example.com",
                 "MXKSlsXXXXX"))
LOGIN.from_jira(my_jira)
print(LOGIN.get(endpoint.myself()))
# response
# <Response [200]>
```


**Release 0.7.2** - 2022-10-04
### Update #97
* Patch to OAuth 2.0 connection error - which caused the connection not to work.
* Added new method to the `endpoint` alias, `issue_link`, `work_logs`, `instance_info`, `task`, `worklog_properties`, `issue_watchers`, `issue_votes`, `webhooks`


**Release 0.7.1** - 2022-09-15
### Patch #95
* Patch to method `issue_export` which omit certain rows from final export.
* Added new argument to `token_session` method `_type` which helps to change the context of authorization header.
* Added new method `remote_links` to the `endpoint` alias.


**Release 0.7.0** - 2022-09-05
### Minor #93
* Added a new method `PROJECT.issue_count` which helps to count issues using JQL.
* Added new method `issue_export` which allows you to export all issues within your Jira in a single CSV file.

```python
from jiraone import LOGIN, issue_export
import json

file = "config.json"
config = json.load(open(file))
LOGIN(**config)

jql = "project in (AB, BC, IT, IP) order by created DESC"
issue_export(jql=jql)
```

**Release 0.6.5** - 2022-08-26
### Patch  #86
* * Skipped v0.6.4 as its equivalent to v0.6.5
* Fix for `file_reader` in windows system
* Update to OAuth authentication. Removed `JIRAONE_OAUTH` environment variable and used a property setter instead.
Simply use `LOGIN.save_oauth` and assign a value

### Update
* Added new method to `LOGIN` alias for custom methods
```python
from jiraone import LOGIN, endpoint

# previous statement
LOGIN.custom_method("GET", endpoint.myself())
# You can use any HTTP method "PATCH", "OPTIONS"

```
* Added a new method to the `endpoint` alias
```python
from jiraone import LOGIN, endpoint

# previous statement
jql = "order by created DESC"
LOGIN.get(endpoint.issue_export(jql))

```
* Now you can use Bearer token with the `LOGIN.token_session()` and you can assign a token to this function.
```python
from jiraone import LOGIN, endpoint

# previous statement
url = "https://nexusfive.atlassian.net"
token = "GHxxxxxPPPxx"
# First assign a base_url to the attribute below
LOGIN.base_url = url
# You need to pass the token variable to a keyword argument called `sess`
LOGIN.token_session(sess=token)

```

**Release 0.6.3** - 2022-06-04
### Patch update #85
* Added offline access to OAuth argument
* Bug fix on issue [JIR-8](https://github.com/princenyeche/jiraone/issues/89) affecting windows devices on change_log function
* General patches and doc updates.

**Release 0.6.2** - 2022-04-27
### Patch update #84
* Added a new authentication method using OAuth 2.0 (3LO)
  * With this new method, you can create and add scope to your oauth connection.
  * You will need to either call or set the environment variable `JIRAONE_OAUTH` that stores the OAuth data session.
  * Please note that the `LOGIN.save_oauth` is stored as a string. However, the underlying data is a dictionary which is converted by the oauth method used for authentication.
  * Without doing the below, you will need to re-authenticate every session with your OAuth 2.0 app.

```python
from jiraone import LOGIN
import json

client = {
               "client_id": "JixkXXX",
               "client_secret": "KmnlXXXX",
               "name": "nexusfive",
               "callback_url": "https://auth.atlassian.com/XXXXX",
           }
# saving the oauth session data locally
file = "DATA/cred.json"
dumps = None
if os.path.isfile(file):
    dumps = json.load(open(file))
os.environ["JIRAONE_OAUTH"] = f"{dumps}"
LOGIN(oauth=client)
# LOGIN.save_oauth is a property value, always available
# after an OAuth session is initialized
json.dump(LOGIN.save_oauth,
          open(file, encoding="utf-8", mode="w+"),
          indent=4)
print(LOGIN.get(endpoint.myself()).json())

# saving to a database is similar
# if using `flask` framework and `flask_sqlachemy` we can do the below
# previous import statement
current_user.oauth_token = LOGIN.save_oauth
db.session.commit()
```

* Corrected dot notation method and changed `range` to `enumerate`
* Made documentation update


**Release 0.6.1** - 2022-04-02
### Minor update #83
* Added a correction to #82 with file_writer() to add argument newline when on windows if not on file mode
  * This way, we do not obstruct the binary mode operation.
* Added a new module utils which will now help in writing dictionary object with dot notation.

```python
from jiraone.utils import DotNotation

my_dict = {"name": "Prince"}
dot = DotNotation(my_dict)
print(dot.name)
# result
# Prince
```
* Added a security, code_of_conduct and contribution document files

**Release 0.6.0** - 2022-03-11
### Patch update #80
* Patch to `time_in_status()` fix on windows platform. A carriage return in `file_writer` throws a `TypeError: Expected 13 arguments, got 0`
* Documentation fix


**Release 0.5.9** - 2022-02-24
### Patch update #78
* Patch to `delete_attachments()` and modification of `manage` API docs


**Release 0.5.8** - 2022-02-22
### Patch update #77
* Patch to `delete_attachments()` and API docs update


**Release 0.5.7** - 2022-02-21
### Update
* Added a new function `delete_attachments()` that can perform deletion of attachments with filtering.
* Provided a checkpoint in the iteration of the above function, so it can start from the last known point.
* Corrected some docs in `access.py` module
* `file_writer` and `file_reader` functions now has the ability to enter a delimiter as a parameter.


**Release 0.5.6** - 2022-02-02
### Patch update #73
* Patch v5 to `time_in_status()`. Noticed that the statuses time were wrong. There seems to be
a change in the way the previous API payload was retrieved. Tweaked the logic for retrieving
accurate difference in time.
* The statuses and their time can now be retrieved accurately.
* The save check_point is turned off for the `time_in_status()` function as a slight logic needs
to be added to account for when a breakpoint happens between checkpoint to retain
accurate difference in time between statuses.

**Release 0.5.5** - 2022-01-30
### Patch update #72
* Patch v4 to `time_in_status()`. Noticed the current status not updated on result file.


**Release 0.5.4** - 2022-01-29
### Micro update #69
* Fixed a regression in `time_in_status()`
* Patch v3


**Release 0.5.3** - 2022-01-29
### Micro update #69
* Fixed a regression in `time_in_status()` which caused the data not to
be written to the file.

**Release 0.5.2** - 2022-01-29
### Micro update #67
* Removed encoding argument for `file_writer`

**Release 0.5.1** - 2022-01-29
### Micro update #66
* Added a save point to `PROJECT.change_log()` method
* Added type hint to the entire `jiraone` module, classes and functions.


**Release 0.5.0** - 2022-01-04
### Micro update #65
* Corrected URL for codacy on `README.md` file.


**Release 0.4.9** - 2022-01-04
### Micro update #64
* Updated the repo project URL
* Updated name on MIT License #63


**Release 0.4.8** - 2021-12-20
### Micro update #62
* Added new methods to endpoint API.


**Release 0.4.7** - 2021-10-24
### Micro update #60
* Added two other methods to manage api. `get_all_users` and `find_user`.
* The former returns all the users in the organization and the later finds a specific user based on displayname, accountId or email address


**Release 0.4.6** - 2021-10-11
### Micro update #57

* Added two new functions used by organization users such as `bulk_change_email` and `bulk_change_swap_email` in the `jiraone.module`. It makes use of the organization API that was released in #54

For example
```python
from jiraone.module import bulk_change_email

token = "Vhsj28UJsXXX"
file = "user.csv"
bulk_change_email(file, token)

# A CSV file needs to be added to the same directory the script is running from
# The format of the CSV file has to be in the below format of max 4 columns
# id,current_email, name, target_email
# processes the information.
```

**Release 0.4.5** - 2021-10-10
### Micro update #55
* Made a patch on #55


**Release 0.4.4** - 2021-10-09
### Micro update #54
* Added new organization and user management REST API
* You can be able to create and manage organization users. See more details [here](https://princenyeche.github.io/atlassian-cloud-api/api#manage)
Example

```python
from jiraone import manage

token = "Edfj78jiXXX"
account_id = "5bc7uXXX"
payload = {"message": "On 6-month suspension"} # A payload needs to be passed for the endpoint to work
manage.add_token(token) # Authenticate to the resource
manage.manage_user(account_id, json=payload) # By default it is set to disable a user
# manage.manage_user(account_id, json=payload, disable=False) # Changing disable=False enables back the user
# output
# <Response 204>
```

**Release 0.4.3** - 2021-09-23
### Micro update #53
* Added a new function in `jiraone.module`  which you can use as below. The helps to generate a report of the`time in status` of Jira issues. You can create an output file either in CSV or JSON format. #53
_Example usage_
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
```

**Release 0.4.2** - 2021-08-31
### Micro update #52
* Made patch to v0.4.1 from #51  due to key error when using on server instance.


**Release 0.4.1** - 2021-08-30
### Micro update #51
* Patch to v0.4.0 about the bug reported on #47


**Release 0.4.0** - 2021-08-29
### #49 Minor update
* Fixed problem associated with `None` value reported on #47
* Fixed some minor issues with `field_update` from `jira.module`
* Added access to `user` and `password` attribute with `LOGIN` variable. Now you can do
    * `LOGIN.user` and `LOGIN.password` to get a call to those attributes.


**Release 0.3.9** - 2021-08-1
### Micro update #45
- Patch and removal of print statement in `field.cascading`.


**Release 0.3.8** - 2021-08-1
### Micro update #43
- Patch to `USER.search_user` unable to find some users
  - Apparently increasing the **maxResult** from 50 to 100 caused this unknown behaviour. Reverted back to 50.
- Patch to `field.search_field` unable to find some custom fields.
  - Apparently increasing the **maxResult** from 50 to 100 caused this unknown behaviour. Reverted back to 50.


**Release 0.3.7** - 2021-08-1
## v0.3.7 #42
- Added exceptions class `exceptions.py`
- Created a new module for fields  
- A new function  `field_update` from the module file to handle most field updates.
- v0.3.6 is equivalent to v0.3.7

```python
from jiraone import field, echo, module
#...previous login statements
# first parameter is the field class alias, 2nd param is an issue key, 3rd a Jira field and
# 4th the data value you want to update or change
key = 'T6-73'
field_name = 'A Cascading field'
vals = ['Browser', 'Firefox'] # Cascading field type
echo(module.field_update(field, key, field_name, data=vals))
```


**Release 0.3.5** - 2021-07-12
### #41 Micro update
- Added a new method to get field value in a issue.
```python
from jiraone import field, echo
#...previous login statements
# it expects the field name as the first parameter and the issue key where the field is used as the second parameter
value = field.get_field_value("Labels", "COM-15")
echo(value)
```


**Release 0.3.4** - 2021-05-16
### #38 Micro update
* Added two more attributes to the comment(key).comment() method
* `first_comment` -> returns the first comment in the body content. Can only be called when "body" option is called on the type_field else returns "None".

 * `last_comment` -> returns the last comment in the body content. Can only be called when "body" option is called on the type_field else returns "None".
**Example usage**:

```python
from jiraone import LOGIN, comment

user = "email"
password = "token"
link = "https://yourinstance.atlassian.net"
LOGIN(user=user, password=password, url=link)

keys = "COM-42"
LOGIN.api = False # this changes the api from 3 to latest.
s = comment(keys).comment("body").first_comment
print(s)
```


**Release 0.3.3** - 2021-04-23
### #37 Micro updates

* Added new methods to the `USER` class and updated the `comment` variable. Now you can be able to post a comment and get a proper comment. The `GET` method has various properties, see the documentation for more details.

* Get a mention of a cloud user.
```python
from jiraone import LOGIN, USER

user = "email"
password = "token"
link = "https://yourinstance.atlassian.net"
LOGIN(user=user, password=password, url=link)


if __name__ == '__main__':
    # the output of the file would be absolute to the directory where this python file is being executed from
    # displayName of a user, to output multiple users separate by a comma
    # name = "Prince Nyeche,Prince,John Doe"
    name = "Prince Nyeche"  
    USER.mention_user(name)
```
* POST a comment to a Jira issue and mention users sequentially on a comment.

```python
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
```

The name of users separated by comma, will be changed dynamically within the method. Using the `event=True` argument enables the comment endpoint to switch to post. See more from the `endpoint` methods. As you can see, for any place in the text string where I used
     ***< user >*** that will be replaced to a mentioned format for cloud e.g. [~accountId:5584xxxxxx]



**Release 0.3.1** - 2021-04-10
### #36 Fix bug
* `USER.search_user()` method fails with `TypeError: Expected 4 arguments, got 3` when running a multiuser search via a loop. Somehow the script appends a 3 column header to the csv file. The fix to this problem was to add a kwargs arg to the reader which will skip the header.


**Release 0.3.0** - 2021-03-29
### #34 Minor updates
* Corrected USER.search_user() method if the search file doesn't exist. Rather than throw `FileNotFoundError`, create an empty file.



**Release 0.2.9** - 2021-03-29
### #33 Micro update
* Corrected the return statement for USER.search_user() method so it can return multiple users of the same name if exist.


**Release 0.2.8** - 2021-03-29
### #32 Micro updates
* Added a new reporting method PROJECT.change_log() for fetching issue history.
* updated method PROJECT.download_attachments() method.
* Added method PROJECT.bytes_converter() used for checking KB and MB conversions.
* Added new reporting called USER.search_user() method.

## Find user

```python
from jiraone import LOGIN, USER

user = "email"
password = "token"
link = "https://yourinstance.atlassian.net"
LOGIN(user=user, password=password, url=link)


if __name__ == '__main__':
    # the output of the file would be absolute to the directory where this python file is being executed from
    name = "Prince Nyeche"  # displayName of a user
    USER.search_user(pull="active", user_type="atlassian", find_user=name)
```

## Changelog

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


**Release 0.2.7** - 2021-03-15
### #31 Micro updates
* Changed the error name on field.extract_issue_field_options() method
* No release for v0.2.6 as it's equivalent to v0.2.7
* Added a comment method which can be called by saying
```python
from jiraone import comment

```

* That variable is still a work in progress, for now you can only get comments. Other abilities should include creating and updating comments



**Release 0.2.5** - 2021-03-04
### #30 Micro updates
* Added attribute `LOGIN.api` - it is a bool attribute and it helps to toggle the api version from "3" to "latest". This is useful, when you want to make a call to a Server or Datacenter instance of Jira.
Example usage:
```python
from jiraone import LOGIN

user = "username"
password = "password"
link = "https://yourinstance.server.com"
LOGIN.api = False # this sets the api to latest
LOGIN(user=user, password=password, url=link)
```


**Release 0.2.4** - 2021-02-21
### #27 Micro update
* Corrected some methods of the `Field class`



**Release 0.2.3** - 2021-02-14
### #23 Micro update

* Added a new class `Field` with an alias `field` used to link to the class. It comes with various methods for updating system or custom fields.
* No release for v0.2.2 as it is equal to v0.2.3

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
# add multiple values to a multiselect custom field
for value in case_value:
    c = field.update_field_data(data=value, find_field=fields, key_or_id=issue, options="add", show=False)
    echo(c)

# output
# < Response[204] >
```


**Release 0.2.1** - 2021-02-09
### #21 Micro updates
* Added new method `PROJECT.get_total_comments_on_issues()`
* Example Usage:

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


**Release 0.2.0** - 2021-02-07
### #20 Micro changes

* Added one class `For` and one function `replacement_placeholder`
* Changed the documentation on the `Endpoints` class to be more pythonic.
* Revamp the documentation and readme file with direct links to a documentation.



**Release 0.1.9** - 2021-01-17
### #16 Micro changes
* patch to v2 v0.1.8
* corrected keyword args on `move_attachments_across_instances()` method.


**Release 0.1.8** - 2021-01-17
### #13 Micro changes
* Changed functions from `csv_writer` to `file_writer` and `csv_reader` to `file_reader`
* added new arguments `content` to both `file_writer` and `file_reader` functions.

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


**Release 0.1.7** - 2021-01-14
### #12 Micro update
* Added new argument to `csv_reader` function
   * `skip` -> bool: True allows you to skip the header if the file has any. otherwise defaults to False

* Added an attachment report generator. which allows you to get attachment url, who added the attachment and total number of attachments on all project.

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


**Release 0.1.6** - 2021-01-10
### #10 Micro update
* rectified condition for issue method e.g. `endpoint.issues()`


**Release 0.1.5** - 2021-01-10
### #7 Micro updates
* Corrected and patch v0.1.4 to be of standard to Codacy code test.


**Release 0.1.4** - 2021-01-10
### #7 Micro change
* Added more API endpoints specific to Jira Software, Jira Service Management and Jira Core.


**Release 0.1.3** - 2021-01-05
### #6 Micro update
* added mode parameter for csv_reader and csv_writer function
* Added new reporting example
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


**Release 0.1.2** - 2021-01-05
### Micro update #5
Micro updates
* Corrected Docstrings


**Release 0.1.1** - 2021-01-04
### Micro changes #4
* code clean up on codacy


**Release 0.1.0** - 2021-01-04
## JiraOne
* Create a report using REST API for your Jira Cloud instance
* Use example reports and get the data you need
