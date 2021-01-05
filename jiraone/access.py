#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Contains all Classes used to Authenticate Jira, endpoints and PrettyPrint.

- Instantiate the endpoint to Jira API
- alias to Authentication
- alias to Endpoints
- friendly name to PrettyPrint
"""
from requests.auth import HTTPBasicAuth
from typing import Any, Optional
from pprint import PrettyPrinter
import requests


class Credentials(object):

    """class.Credentials -> used for authentication of the user to the Instance."""

    auth_request = None
    headers = None

    def __init__(self, user: str, password: str, url: str = Any) -> Optional:
        """Instantiate the login."""
        self.base_url = url
        self.token_session(email=user, token=password)

    # produce a session for the script
    def token_session(self, email: Any = None, token: Any = None) -> Any:
        self.auth_request = HTTPBasicAuth(email, token)
        self.headers = {"Content-Type": "application/json"}

    def get(self, url, *args, payload=None, **kwargs):
        response = requests.get(url, *args, auth=self.auth_request, json=payload, headers=self.headers, **kwargs)

        return response

    def post(self, url, *args, payload=None, **kwargs):
        response = requests.post(url, *args, auth=self.auth_request, json=payload, headers=self.headers, **kwargs)

        return response

    def put(self, url, *args, payload=None, **kwargs):
        response = requests.put(url, *args, auth=self.auth_request, json=payload, headers=self.headers, **kwargs)

        return response

    def delete(self, url, **kwargs):
        response = requests.delete(url, auth=self.auth_request, headers=self.headers, **kwargs)
        return response


class Echo(PrettyPrinter):

    """A Class used to inherit from PrettyPrinter."""

    def __init__(self, *args, **kwargs):
        """Inherit from the parent."""
        super(Echo, self).__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        return self.__init__(*args, **kwargs)

    def echo(self, raw):
        """Prints the formatted representation of object on stream, followed by a newline."""
        return self.pprint(object=raw)


class InitProcess(Credentials):
    """should inherit an instance of Credential class using super().

    Object values are entered directly when called because of the __call__
    dunder method."""

    def __init__(self, user=None, password=None, url=None):
        """A Call to the Credential Class."""
        super(InitProcess, self).__init__(user=user, password=password, url=url)

    def __call__(self, *args, **kwargs):
        return self.__init__(*args, **kwargs)


LOGIN = InitProcess()


class EndPoints:
    
    """A Structural way to dynamically load urls that is fed to other functions."""

    @classmethod
    def myself(cls):
        """Return data on your own user."""
        return "{}/rest/api/3/myself".format(LOGIN.base_url)

    @classmethod
    def search_users(cls, query: int = 0):
        """Search multiple users and retrieve the data

        :param: startAt
        """
        return "{}/rest/api/3/users/search?startAt={}&maxResults=50".format(LOGIN.base_url, query)

    @classmethod
    def get_user_group(cls, account_id: Any):
        """Search for the groups a user belongs to

        :param: accountId required
        """
        return f"{LOGIN.base_url}/rest/api/3/user/groups?accountId={account_id}"

    @classmethod
    def get_projects(cls, *args: Any, start_at=0, max_results=50):
        """Return a list of Projects available on an Instance

        How to use this endpoint /rest/api/3/project/search  is mentioned here
        1. https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-projects/
           #api-rest-api-3-project-search-get
        2. Query Parameters that are useful mostly.
           a) query, example: query=key,name {caseInsensitive}
           b) searchBy, example: searchBy=key,name
           c) action, example: action=browse
               i. available options [view, browse, edit]
           d) status example: status=live
               i. available options [live, archived, deleted]
           e). expand, example: expand=insight
                 i. available options [insight, description, projectKeys, url, issueTypes, lead]
        3. startAt defaults as keyword args, example: startAt=0
        4. maxResults defaults as keyword args, example: maxResults=50
        """
        param = []
        amp = "&"
        num_list = 0
        if args:
            nos = len(args)
            if nos > 0:
                for v in args:
                    param.append(f"{v}{amp}")
                    num_list += 1
                    if num_list >= nos:
                        # cut the last ampersand and clear the list
                        cut = "".join(param).rstrip("&")
                        param.clear()
                        param.append(cut)
                        break
                print("Project Search Query Parameter:", param[0])
                return "{}/rest/api/3/project/search?{}&startAt={}&maxResults={}".format(LOGIN.base_url,
                                                                                         param[0],
                                                                                         start_at,
                                                                                         max_results)
        else:
            return "{}/rest/api/3/project/search?startAt={}&maxResults={}".format(LOGIN.base_url,
                                                                                  start_at,
                                                                                  max_results)

    @classmethod
    def find_users_with_permission(cls, *args):
        """Find users with permissions to a Project

        :param: 1st accountId
        :param: 2nd projectKey
        :param: 3rd permissions that needs checking all in caps e.g "BROWSE", "CREATE_ISSUE" etc
        """
        return "{}/rest/api/3/user/permission/search?accountId={}&projectKey={}&permissions={}" \
            .format(LOGIN.base_url, *args)

    @classmethod
    def get_roles_for_project(cls, id_or_key: Any):
        """Returns a list of project roles for the project returning the name and self URL for each role.

        :param: projectKey or Id
        """
        return "{}/rest/api/3/project/{}/role".format(LOGIN.base_url, id_or_key)

    @classmethod
    def get_project_role(cls, *args):
        """Returns a project role's details and actors associated with the project.

        :param: projectKey or Id of the Project
        :param: id of the role
        """
        return "{}/rest/api/3/project/{}/role/{}".format(LOGIN.base_url, *args)

    @classmethod
    def get_all_permission_scheme(cls, query: str = None):
        """Returns all permission schemes."""
        if query is not None:
            return "{}/rest/api/3/permissionscheme?{}".format(LOGIN.base_url, query)
        else:
            return "{}/rest/api/3/permissionscheme".format(LOGIN.base_url)

    @classmethod
    def get_all_issue_type_schemes(cls, query: Optional[str] = None, start_at=0, max_results=50):
        """Returns a paginated list of issue type schemes.

        Only issue type schemes used in classic projects are returned"""
        if query is not None:
            return "{}/rest/api/3/issuetypescheme?{}&startAt={}&maxResults={}".format(LOGIN.base_url, query,
                                                                                      start_at, max_results)
        else:
            return "{}/rest/api/3/issuetypescheme?startAt={}&maxResults={}".format(LOGIN.base_url,
                                                                                   start_at, max_results)

    @classmethod
    def get_all_issue_types(cls):
        """Returns all issue types.

        if the user has the Administer Jira global permission, all issue types are returned.
        if the user has the Browse projects project permission for one or more projects,
        the issue types associated with the projects the user has permission to browse are returned.
        """
        return "{}/rest/api/3/issuetype".format(LOGIN.base_url)

    @classmethod
    def get_all_issue_security_scheme(cls):
        """Returns all issue security schemes."""
        return "{}/rest/api/3/issuesecurityschemes".format(LOGIN.base_url)

    @classmethod
    def get_all_priorities(cls):
        """Returns the list of all issue priorities."""
        return "{}/rest/api/3/priority".format(LOGIN.base_url)

    @classmethod
    def search_all_notification_schemes(cls, query: Optional[str] = None, start_at=0, max_results=50):
        """Returns a paginated list of notification schemes ordered by display name.

        :param: 1st String value for expand=: {all, field, group, user, projectRole, notificationSchemeEvents}
        :param: 2nd startAt=0 has default value
        :param: 3rd maxResults=50 has default value
        """
        if query is not None:
            return "{}/rest/api/3/notificationscheme?{}&startAt={}&maxResults={}".format(LOGIN.base_url, query,
                                                                                         start_at, max_results)
        else:
            return "{}/rest/api/3/notificationscheme?startAt={}&maxResults={}".format(LOGIN.base_url,
                                                                                      start_at, max_results)

    @classmethod
    def get_field(cls, query: Optional[str] = None, start_at: int = 0, max_results: int = 50):
        """Returns a paginated list of fields for Classic Jira projects. The list can include:

        *  all fields.
        *  specific fields, by defining id.
        *  fields that contain a string in the field name or description, by defining query.
        *  specific fields that contain a string in the field name or description, by defining id and query.
        Only custom fields can be queried, type must be set to custom.
         """
        if query is not None:
            return "{}/rest/api/3/field/search?{}&startAt={}&maxResults={}".format(LOGIN.base_url, query,
                                                                                   start_at, max_results)
        else:
            return "{}/rest/api/3/field/search?startAt={}&maxResults={}".format(LOGIN.base_url,
                                                                                start_at, max_results)

    @classmethod
    def get_attachment_meta_data(cls, query: str):
        """Returns the metadata for an attachment. Note that the attachment itself is not returned.

         :param: id of the attachment
         Use issue search endpoint in conjunction to grab the attachment id
         """
        return "{}/rest/api/3/attachment/{}".format(LOGIN.base_url, query)

    @classmethod
    def search_issues_jql(cls, query, start_at: int = 0, max_results: int = 50):
        """Searches for issues using JQL."""
        return "{}/rest/api/3/search?jql={}&startAt={}&maxResults={}".format(LOGIN.base_url, query,
                                                                             start_at, max_results)

    @classmethod
    def search_for_filters(cls, query: Optional[str] = None, start_at: int = 0):
        """Returns a paginated list of filters. Use this operation to get:

        *  specific filters, by defining id only.
        *  filters that match all of the specified attributes. For example, all filters
           for a user with a particular word in their name. When multiple attributes are
           specified only filters matching all attributes are returned.
        :param: 1st String value: filterName, accountId, owner, groupname, projectId
        :param: 2nd startAt=0 has default value
        :param: filled - maxResults=50 (default)
         """
        if query is not None:
            return "{}/rest/api/3/filter/search?{}&startAt={}&maxResults=50".format(LOGIN.base_url, query, start_at)
        else:
            return "{}/rest/api/3/filter/search?startAt={}&maxResults=50".format(LOGIN.base_url, start_at)

    @classmethod
    def search_for_dashboard(cls, query: Optional[str] = None, start_at: int = 0):
        """Returns a paginated list of dashboards. This operation is similar to

        Get dashboards except that the results can be refined to include dashboards that
        have specific attributes. For example, dashboards with a particular name.
        When multiple attributes are specified only filters matching all attributes
        are returned.
        :param: 1st String value: dashboardName, accountId, owner, groupname, projectId
        :param: 2nd startAt=0 has default value
        :param: filled - maxResult=20 (default)
        """
        if query is not None:
            return "{}/rest/api/3/dashboard/search?{}&startAt={}&maxResults=20".format(LOGIN.base_url, query, start_at)
        else:
            return "{}/rest/api/3/dashboard/search?startAt={}&maxResults=20".format(LOGIN.base_url, start_at)

    @classmethod
    def get_dashboard(cls, dashboard_id: int):
        """Gets the dashboard."""
        return "{}/rest/api/3/dashboard/{}".format(LOGIN.base_url, dashboard_id)

    @classmethod
    def get_all_application_role(cls):
        """
        Returns all application roles.

        In Jira, application roles are managed using the Application access configuration page."""
        return "{}/rest/api/3/applicationrole".format(LOGIN.base_url)

    @classmethod
    def search_all_workflows(cls, query: int = 0):
        """
        Returns a paginated list of published classic workflows. When workflow names are specified.

        details of those workflows are returned. Otherwise, all published classic workflows are returned.
        This operation does not return next-gen workflows.
        :param: 1st startAt=0 has default value
        :param: filled - maxResults=50 (default)
        """
        return "{}/rest/api/3/workflow/search?startAt={}&maxResults=50".format(LOGIN.base_url, query)

    @classmethod
    def search_all_workflow_schemes(cls, query: int = 0):
        """Returns a paginated list of all workflow schemes, not including draft workflow schemes.

        :param: 1st startAt=0 has default value
        :param: filled - maxResults=50 (default)
        """
        return "{}/rest/api/3/workflowscheme?startAt={}&maxResults=50".format(LOGIN.base_url, query)

    @classmethod
    def search_all_screens(cls, query: int = 0):
        """Returns a paginated list of all screens or those specified by one or more screen IDs.

        :param: 1st startAt=0 has default value
        :param: maxResults=100 (default)
        """
        return "{}/rest/api/3/screens?startAt={}&maxResults=100".format(LOGIN.base_url, query)

    @classmethod
    def search_for_screen_schemes(cls, query: int = 0):
        """Returns a paginated list of screen schemes.

            Only screen schemes used in classic projects are returned.
        :param: 1st - startAt=0 has default value
        :param: maxResults=25 (default)
        """
        return "{}/rest/api/3/screenscheme?startAt={}&maxResults=25".format(LOGIN.base_url, query)

    @classmethod
    def get_project_component(cls, id_or_key):
        """Returns all components in a project. See the Get project components paginated

            resource if you want to get a full list of components with pagination.
            The project ID or project key (case sensitive).
        """
        return "{}/rest/api/3/project/{}/components".format(LOGIN.base_url, id_or_key)

    @classmethod
    def get_resolutions(cls):
        """Returns a list of all issue resolution values."""
        return "{}/rest/api/3/resolution".format(LOGIN.base_url)


def echo(obj):
    """A Call to the Echo Class."""
    e = Echo()
    return e.echo(raw=obj)


endpoint = EndPoints()
