# Jira one
A REST API Implementation to Jira Cloud APIs for creating reports

## Configurations
Install using `pip`. you have to be on python >= 3.6.x in order to utilize this script.
```bash
pip install jiraone
```
OR use the requirements.txt file to install
```bash
pip install -r requirements.txt
```

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


def priorities(self):
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
* generate a report of all user in the instance and which group do they belong ot
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

## Support
* For any issues or feature request, feel free to create an issue on Github or email me at support@elfapp.website
