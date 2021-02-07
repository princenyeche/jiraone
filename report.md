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


## Support
* For any issues or feature request, feel free to create an issue on Github or email me at support@elfapp.website
