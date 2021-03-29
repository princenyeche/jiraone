# Basic Report Usage
The script comes with some basic reporting Classes and methods which you can use to generate a report in CSV format.
currently only CSV file output is supported. other format such as JSON might be available in future.

## USER API
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
    USER.search_user(pull="active", user_type="atlassian", find_user=name)
```

## PROJECT API

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

* generate a report of all the issue history within a project or projects

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

## Support
* For any issues or feature request, feel free to create an issue on Github or email me at support@elfapp.website
