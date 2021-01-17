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

    # produce a session for the script and save the session
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
                return "{}/rest/api/3/project/search?{}&startAt={}&maxResults={}"\
                    .format(LOGIN.base_url, param[0], start_at, max_results)
        else:
            return "{}/rest/api/3/project/search?startAt={}&maxResults={}"\
                .format(LOGIN.base_url, start_at, max_results)

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
    def get_attachment_meta_data(cls, query: str, warning: Any = None):
        """Returns the metadata for an attachment. Note that the attachment itself is not returned.

         :param: id of the attachment
         Use issue search endpoint in conjunction to grab the attachment id
         """
        import warnings
        message = "We will be removing this endpoint soon\n use endpoint.issue_attachments() instead."
        if warning is None:
            warnings.warn(message, DeprecationWarning, stacklevel=2)
        else:
            pass
        return "{}/rest/api/3/attachment/{}".format(LOGIN.base_url, query)

    @classmethod
    def issue_attachments(cls, id_or_key: str = None, attach_id: str = None, uri: Optional[str] = None,
                          query: Optional[str] = None):
        """Returns the attachment content.

        :request: GET - Get Jira attachment settings
        Returns the attachment settings, that is, whether attachments are enabled and the
        maximum attachment size allowed.

                 GET - Get attachment Meta data
        Returns the metadata for an attachment. Note that the attachment itself is not returned.

        :param: attach_id required (id of the attachment), datatype -> string
                DELETE - Deletes an attachment from an issue.

        param: attach_id required (id of the attachment), datatype -> string
               GET - Get all metadata for an expanded attachment
               :param: query, datatype -> string
               available options
                * expand/human -Returns the metadata for the contents of an attachment, if it is an archive,
                     and metadata for the attachment itself. For example, if the attachment is a ZIP archive,
                     then information about the files in the archive is returned and metadata for the ZIP archive.

                * expand/raw - Returns the metadata for the contents of an attachment, if it is an archive.
                     For example, if the attachment is a ZIP archive, then information about the files in the
                     archive is returned. Currently, only the ZIP archive format is supported.

               POST - Adds one or more attachments to an issue. Attachments are posted as multipart/form-data
        POST - Adds one or more attachments to an issue. Attachments are posted as multipart/form-data
        :param: id_or_key required, datatype -> string
        The ID or key of the issue that attachments are added to.
        """
        # TODO: check this endpoint again
        if uri is not None:
            return "{}/rest/api/3/attachment/{}".format(LOGIN.base_url, uri)
        else:
            if query is not None and attach_id is not None and id_or_key is None:
                return "{}/rest/api/3/attachment/{}/{}".format(LOGIN.base_url, attach_id, query)
            elif query is not None and attach_id is None and id_or_key is not None:
                return "{}/rest/api/3/issue/{}/{}".format(LOGIN.base_url, id_or_key, query)
            else:
                return "{}/rest/api/3/attachment/{}".format(LOGIN.base_url, attach_id)

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

    ################################################
    # Jira Software Specifics API endpoints
    ################################################
    # BACKLOG -> API for backlog
    @classmethod
    def move_issues_to_backlog(cls):
        """Move issues to the backlog.

        This operation is equivalent to remove future and active sprints from a given set of issues.
        At most 50 issues may be moved at once.

        :request:POST:
        :body param: issues, datatype -> Array<string>
        Send a POST request within API.
        """
        return "{}/rest/agile/1.0/backlog/issue".format(LOGIN.base_url)

    @classmethod
    def move_issues_to_backlog_from_board(cls, board_id):
        """Move issues to the backlog of a particular board (if they are already on that board).

        This operation is equivalent to remove future and active sprints from a given set of issues
        if the board has sprints If the board does not have sprints this will put the issues back
        into the backlog from the board. At most 50 issues may be moved at once.

        :request:POST:
        :param: board_id required
        :body param: issues, datatype -> Array<string>,
                   : rankBeforeIssue, rankAfterIssue, type -> string
                   : rankCustomFieldId, type -> integer
        """
        return "{}/rest/agile/1.0/backlog/{}/issue".format(LOGIN.base_url, board_id)

    # BOARD -> API for Boards

    @classmethod
    def create_board(cls):
        """Creates a new board. Board name, type and filter ID is required.

        :request:POST:
        :body param: name, type, datatype -> string
                   : filterId, datatype -> integer
                   : location, datatype -> object
        """
        return "{}/rest/agile/1.0/board".format(LOGIN.base_url)

    @classmethod
    def get_board_by_filter_id(cls, filter_id, start_at: int = 0, max_results: int = 50) -> Any:
        """Returns any boards which use the provided filter id.

        This method can be executed by users without a valid software license
        in order to find which boards are using a particular filter.

        :param: filter_id  required
        Filters results to boards that are relevant to a filter.
        Not supported for next-gen boards.

        :query param: start_at defaults to 0
                    : max_results defaults to 50
        """
        return "{}/rest/agile/1.0/board/filter/{}?startAt={}&maxResults={}"\
            .format(LOGIN.base_url, filter_id, start_at, max_results)

    @classmethod
    def get_board(cls, board_id):
        """Returns the board for the given board ID.

        This board will only be returned if the user has permission to view it.
        Admins without the view permission will see the board as a private one,
        so will see only a subset of the board's data (board location for instance).
        """
        return "{}/rest/agile/1.0/board/{}".format(LOGIN.base_url, board_id)

    @classmethod
    def get_issues_on_backlog(cls, board_id, query: str = None, start_at: int = 0, max_results: int = 50) -> Any:
        """Returns all issues from the board's backlog, for the given board ID.

        This only includes issues that the user has permission to view.
        The backlog contains incomplete issues that are not assigned to any future or active sprint.

        :param: board_id required
        :query param: start_at defaults to 0,
                    : max_results defaults to 50
                    : query -> includes other query parameters such as
                         Query           Datatypes
                        ----------------------------
                         jql           | string
                         validateQuery | boolean
                         fields        | Array<string>
                         expand        | string
        """
        if query is not None:
            return "{}/rest/agile/1.0/board/{}/backlog?{}&startAt={}&maxResults={}"\
                .format(LOGIN.base_url, board_id, query, start_at, max_results)
        else:
            return "{}/rest/agile/1.0/board/{}/backlog?startAt={}&maxResults={}"\
                .format(LOGIN.base_url, board_id, start_at, max_results)

    @classmethod
    def get_issues_on_board(cls, board_id, query: str = None, start_at: int = 0, max_results: int = 50) -> Any:
        """Returns all issues from a board, for a given board ID.

        This only includes issues that the user has permission to view.
        An issue belongs to the board if its status is mapped to the board's column.

        :param: board_id required
        :query param: start_at defaults to 0,
                    : max_results defaults to 50
                    : query -> includes other query parameters such as
                         Query           Datatypes
                        ----------------------------
                         jql           | string
                         validateQuery | boolean
                         fields        | Array<string>
                         expand        | string
        """
        if query is not None:
            return "{}/rest/agile/1.0/board/{}/issue?{}&startAt={}&maxResults={}"\
                .format(LOGIN.base_url, board_id, query, start_at, max_results)
        else:
            return "{}/rest/agile/1.0/board/{}/issue?startAt={}&maxResults={}"\
                .format(LOGIN.base_url, board_id, start_at, max_results)

    @classmethod
    def move_issues_to_board(cls, board_id):
        """Move issues from the backog to the board (if they are already in the backlog of that board).

        This operation either moves an issue(s) onto a board from the backlog (by adding it to the issueList
        for the board) Or transitions the issue(s) to the first column for a kanban board with backlog.

        :request:POST:
        :param: board_id required
        :body param: rankBeforeIssue, rankAfterIssue, datatype -> string
                   : rankCustomFieldId, datatype -> integer
                   : issues, datatype -> Array<string>
        """
        return "{}/rest/agile/1.0/board/{}/issue".format(LOGIN.base_url, board_id)

    @classmethod
    def get_projects_on_board(cls, board_id, start_at: int = 0, max_results: int = 50) -> Any:
        """Returns all projects that are associated with the board, for the given board ID.

         If the user does not have permission to view the board, no projects will be returned at all.
         Returned projects are ordered by the name.

         :param: board_id required
         :query param: start_at defaults 0
                     : max_results defaults 50
        """
        return "{}/rest/agile/1.0/board/{}/project?startAt={}&maxResults={}"\
            .format(LOGIN.base_url, board_id, start_at, max_results)

    @classmethod
    def get_all_quick_filters(cls, board_id, start_at: int = 0, max_results: int = 50) -> Any:
        """Returns all quick filters from a board, for a given board ID.

        :param: board_id required
        :query param: start_at defaults 0
                     : max_results defaults 50
        """
        return "{}/rest/agile/1.0/board/{}/quickfilter?startAt={}&maxResults={}"\
            .format(LOGIN.base_url, board_id, start_at, max_results)

    @classmethod
    def get_quick_filter(cls, board_id, quick_filter_id):
        """Returns the quick filter for a given quick filter ID.

        The quick filter will only be returned if the user can view the board that the
        quick filter belongs to.

        :param: board_id required,
                quick_filter_id required
        """
        return "{}/rest/agile/1.0/board/{}/quickfilter/{}".format(LOGIN.base_url, board_id, quick_filter_id)

    @classmethod
    def get_all_sprints(cls, board_id, query: str = None, start_at: int = 0, max_results: int = 50) -> Any:
        """Get all Sprint on a Board."""
        if query is not None:
            return "{}/rest/agile/1.0/board/{}/sprint?startAt={}&maxResults={}"\
                .format(LOGIN.base_url, board_id, query, start_at, max_results)
        else:
            return "{}/rest/agile/1.0/board/{}/sprint?startAt={}&maxResults={}"\
                .format(LOGIN.base_url, board_id, start_at, max_results)

    # SPRINT -> API for Sprints
    @classmethod
    def create_sprint(cls):
        """Creates a future sprint. Sprint name and origin board id are required.

        Start date, end date, and goal are optional.
        :request:POST:
        :body param: name, startDate, endDate, goal, datatype -> string
                   : originBoardId, datatype -> integer
        """
        return "{}/rest/agile/1.0/sprint".format(LOGIN.base_url)

    @classmethod
    def get_sprint(cls, sprint_id):
        """Returns the sprint for a given sprint ID.

        The sprint will only be returned if the user can view the board that the sprint was created on,
        or view at least one of the issues in the sprint.
        :param: sprint_id required
        """
        return "{}/rest/agile/1.0/sprint/{}".format(LOGIN.base_url, sprint_id)

    @classmethod
    def update_sprint(cls, sprint_id):
        """Performs a full update of a sprint.

        A full update means that the result will be exactly the same as the request body.
        Any fields not present in the request JSON will be set to null.

        :request:PUT:
        :param: sprint_id required
        :body param: name, state, startDate, endDate, goal, self (format: uri), completeDate, datatype -> string
                   : id, originBoardId, datatype -> integer
        """
        return "{}/rest/agile/1.0/sprint/{}".format(LOGIN.base_url, sprint_id)

    @classmethod
    def delete_sprint(cls, sprint_id):
        """Deletes a sprint.

        Once a sprint is deleted, all open issues in the sprint will be moved to the backlog.
        :request:DELETE:
        :param: sprint_id required
        """
        return "{}/rest/agile/1.0/sprint/{}".format(LOGIN.base_url, sprint_id)

    ################################################
    # Jira Service Management Specific API endpoints
    ################################################
    @classmethod
    def create_customer(cls):
        """This method adds a customer to the Jira Service Management.

        instance by passing a JSON file including an email address and display name.
        :request:POST
        :body param: email, displayName, datatype -> string
        """
        return "{}/rest/servicedeskapi/customer".format(LOGIN.base_url)

    @classmethod
    def get_server_info(cls):
        """This method retrieves information about the Jira Service Management.

        instance such as software version, builds, and related links."""
        return "{}/rest/servicedeskapi/info".format(LOGIN.base_url)

    @classmethod
    def get_organizations(cls, start: int = 0, limit: int = 50, account_id: str = None) -> Any:
        """This method returns a list of organizations in the Jira Service Management instance.

        Use this method when you want to present a list of organizations or want to locate an organization by name.
        :query param: start defaults to 0
                    : limit defaults to 50
                    : account_id, datatype string. e.g. 5b10ac8d82e05b22cc7d4ef5
        """
        if account_id is not None:
            return "{}/rest/servicedeskapi/organization?{}&start={}&limit={}"\
                .format(LOGIN.base_url, account_id, start, limit)
        else:
            return "{}/rest/servicedeskapi/organization?start={}&limit={}".format(LOGIN.base_url, start, limit)

    @classmethod
    def create_organization(cls):
        """This method creates an organization by passing the name of the organization.

        :request:POST:
        :body param: name, datatype -> string
        """
        return "{}/rest/servicedeskapi/organization".format(LOGIN.base_url)

    @classmethod
    def get_organization(cls, org_id):
        """This method returns details of an organization.

        Use this method to get organization details whenever your application component is passed an organization ID
        but needs to display other organization details.
        :param: org_id required
        """
        return "{}/rest/servicedeskapi/organization/{}".format(LOGIN.base_url, org_id)

    @classmethod
    def delete_organization(cls, org_id):
        """This method deletes an organization.

        Note that the organization is deleted regardless of other associations it may have.
        For example, associations with service desks.
        :request:DELETE:
        :param: org_id required
        """
        return "{}/rest/servicedeskapi/organization/{}".format(LOGIN.base_url, org_id)

    @classmethod
    def get_users_in_organization(cls, org_id, start: int = 0, limit: int = 50) -> Any:
        """This method returns all the users associated with an organization.

        Use this method where you want to provide a list of users for an organization
        or determine if a user is associated with an organization.
        :param: org_id required
        """
        return "{}/rest/servicedeskapi/organization/{}/user?start={}&limit={}".format(LOGIN.base_url, org_id,
                                                                                      start, limit)

    @classmethod
    def add_users_to_organization(cls, org_id) -> Any:
        """This method adds users to an organization.

        :request:POST:
        :param: org_id required
        :body param: usernames, accountIds, datatypes -> Array<string>
        """
        return "{}/rest/servicedeskapi/organization/{}/user".format(LOGIN.base_url, org_id)

    @classmethod
    def remove_users_from_organization(cls, org_id) -> Any:
        """This method removes users from an organization.

        :request:DELETE:
        :param: org_id required
        :body param: usernames, accountIds, datatypes -> Array<string>
        """
        return "{}/rest/servicedeskapi/organization/{}/user".format(LOGIN.base_url, org_id)

    @classmethod
    def get_sd_organizations(cls, service_desk_id, start: int = 0, limit: int = 50, account_id: str = None):
        """This method returns a list of all organizations associated with a service desk.

        :param: service_desk_id required
        :query param: start defaults to 0
                    : limit defaults to 50
                    : account_id, datatype string. e.g. 5b10ac8d82e05b22cc7d4ef5
        """
        if account_id is not None:
            return "{}/rest/servicedeskapi/servicedesk/{}/organization?{}&start={}&limit={}"\
                .format(LOGIN.base_url, account_id, service_desk_id, start, limit)
        else:
            return "{}/rest/servicedeskapi/servicedesk/{}/organization?start={}&limit={}"\
                .format(LOGIN.base_url, service_desk_id, start, limit)

    @classmethod
    def add_sd_organization(cls, service_desk_id):
        """This method adds an organization to a service desk.

        If the organization ID is already associated with the service desk,
        no change is made and the resource returns a 204 success code.
        :request:POST:
        :param: service_desk_id required
        :body param: organizationId, datatype -> integer
        """
        return "{}/rest/servicedeskapi/servicedesk/{}/organization".format(LOGIN.base_url, service_desk_id)

    @classmethod
    def remove_sd_organization(cls, service_desk_id):
        """This method removes an organization from a service desk.

        If the organization ID does not match an organization associated with the service desk,
        no change is made and the resource returns a 204 success code.
        :request:DELETE:
        :param: service_desk_id required
        :body param: organizationId, datatype -> integer
        """
        return "{}/rest/servicedeskapi/servicedesk/{}/organization".format(LOGIN.base_url, service_desk_id)

    # SERVICEDESK -> API specific to servicedesk
    @classmethod
    def get_customers(cls, service_desk_id, start: int = 0, limit: int = 50, query: str = None):
        """This method returns a list of the customers on a service desk.

        The returned list of customers can be filtered using the query parameter.
        The parameter is matched against customers' displayName, name, or email.
        This API is experimental
        :param: service_desk_id required
        :query param: start defaults to 0
                    : limit defaults to 50
                    : query, datatype string.
        """
        if query is not None:
            return "{}/rest/servicedeskapi/servicedesk/{}/customer?{}&start={}&limit={}"\
                .format(LOGIN.base_url, query, service_desk_id, start, limit)
        else:
            return "{}/rest/servicedeskapi/servicedesk/{}/customer?start={}&limit={}"\
                .format(LOGIN.base_url, service_desk_id, start, limit)

    @classmethod
    def add_customers(cls, service_desk_id):
        """Adds one or more customers to a service desk.

        If any of the passed customers are associated with the service desk,
        no changes will be made for those customers and the resource returns a 204 success code.
        :request:POST:
        :param: service_desk_id required
        :body param: usernames, accountIds,  datatype -> Array<string>
                """
        return "{}/rest/servicedeskapi/servicedesk/{}/customer".format(LOGIN.base_url, service_desk_id)

    @classmethod
    def remove_customers(cls, service_desk_id):
        """This method removes one or more customers from a service desk.

        The service desk must have closed access. If any of the passed customers are not associated with
        the service desk, no changes will be made for those customers and the resource returns a 204 success code.
        :request:DELETE:
        :param: service_desk_id required
        :body param: usernames, accountIds,  datatype -> Array<string>
                """
        return "{}/rest/servicedeskapi/servicedesk/{}/customer".format(LOGIN.base_url, service_desk_id)

    ################################################
    # Jira Specific API endpoints
    ################################################
    @classmethod
    def jira_user(cls, account_id: str = None):
        """API for User creation, deletion and retrieval.

        :request:POST - Creates a user. This resource is retained for legacy compatibility.
                        As soon as a more suitable alternative is available this resource will be deprecated
                        :body param: key, name, password, emailAddress, displayName, notification, datatypes -> string
                                    : applicationKeys, datatype -> Array<string>
                                    : Additional Properties, datatypes -> Any
                        returns 201 for successful creation
                :DELETE - Deletes a user.
                          :body param: accountId, datatype -> string required
                          returns 204 for successful deletion
                :GET - Returns a user.
                       :body param: accountId, expand, datatypes -> string
        """
        if account_id is not None:
            return "{}/rest/api/3/user?accountId={}".format(LOGIN.base_url, account_id)
        else:
            return "{}/rest/api/3/user".format(LOGIN.base_url)

    @classmethod
    def jira_group(cls, group_name: str = None, swap_group: str = None):
        """Used for Creation and deletion of Jira groups.

        :request: POST - Creates a group.
                     :body param: name required, datatype -> string
                     returns 201 if successful
                : DELETE - Deletes a group.
                     The group to transfer restrictions to. Only comments and worklogs are transferred.
                     If restrictions are not transferred, comments and worklogs are inaccessible after the deletion.
                     :query param: group_name required, swap_group,  datatype -> string
                     returns 200 if successful
        """
        if group_name is not None and swap_group is None:
            return "{}/rest/api/3/group?groupname={}".format(LOGIN.base_url, group_name)
        elif group_name is not None and swap_group is not None:
            return "{}/rest/api/3/group?groupname={}&swapGroup={}".format(LOGIN.base_url, group_name, swap_group)
        else:
            return "{}/rest/api/3/group".format(LOGIN.base_url)

    @classmethod
    def group_jira_users(cls, group_name: str, account_id: str = None):
        """Used for addition and removal of users to and from groups.

        :request: POST - Adds a user to a group.
                     :query param: groupname required, datatype -> string
                     :body param: name, accountId, datatype -> string
                     returns 201 if successful
                : DELETE - Removes a user from a group.
                     :query param: group_name required, account_id required,  datatype -> string
                     returns 200 if successful
        """
        if account_id is not None:
            return "{}/rest/api/3/group/user?groupname={}&accountId={}".format(LOGIN.base_url, group_name, account_id)
        else:
            return "{}/rest/api/3/group/user?groupname={}".format(LOGIN.base_url, group_name)

    @classmethod
    def projects(cls, id_or_key, query: Optional[str] = None, uri: Optional[str] = None,
                 enable_undo: Optional[bool] = None) -> str:
        """Create, delete, update, archive, get status.

        :request: POST - for project creations.
                         The project types are available according to the installed Jira features as follows:
        :param: id_or_key required
              : uri optional for accessing other project endpoints -> string
                   endpoint: /rest/api/3/project/{projectIdOrKey}/{archive}
                   available options [archive, delete, restore, statuses]
                         archive - Archives a project. Archived projects cannot be deleted.
                         delete - Deletes a project asynchronously.
                         restore - Restores a project from the Jira recycle bin.
                         statuses - Returns the valid statuses for a project.

        see:https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-projects/#api-rest-api-3-project-post

                  :body param: projectTypeKey and projectTemplateKey required, datatype -> string
                             : name, key, description, leadAccountId, url, assigneeType, datatype -> string
                             : avatarId, issueSecurityScheme, permissionScheme, notificationScheme, categoryId,
                              datatype -> integer
                : GET - Returns the project details for a project.
                This operation can be accessed anonymously.
                     :query param: expand, datatype -> string
                                 : properties, datatype -> Array<string>

               : PUT - Updates the project details for a project.
                  :query param: expand, datatype -> string
                  :body param: projectTypeKey and projectTemplateKey required, datatype -> string
                             : name, key, description, leadAccountId, url, assigneeType, datatype -> string
                             : avatarId, issueSecurityScheme, permissionScheme, notificationScheme, categoryId,
                              datatype -> integer

              : DELETE - Deletes a project.
                   :query param: enable_undo, datatype -> boolean

        """
        if uri is not None:
            return "{}/rest/api/3/project/{}/{}".format(LOGIN.base_url, id_or_key, uri)
        else:
            if query is not None:
                return "{}/rest/api/3/project/{}?{}".format(LOGIN.base_url, id_or_key, query)
            else:
                if enable_undo is not None:
                    return "{}/rest/api/3/project/{}?enableUndo={}".format(LOGIN.base_url, id_or_key, enable_undo)
                else:
                    return "{}/rest/api/3/project/{}".format(LOGIN.base_url, id_or_key)

    @classmethod
    def issues(cls, issue_key_or_id: Optional[Any] = None, query: Optional[Any] = None,
               uri: Optional[str] = None) -> str:
        """Creates issues, delete issues,  bulk create issue, transitions.

        A transition may be applied, to move the issue or subtask to a workflow step other than
        the default start step, and issue properties set.

        :request: POST - Creates an issue or, where the option to create subtasks is enabled in Jira, a subtask.
        :param: uri, datatype -> string
        :param: query, datatype -> string
        :param: issue_key_or_id -> string or integer
                available options [bulk, createmeta]
                e.g. endpoint: /rest/api/3/issue/bulk
                e.g. endpoint /rest/api/3/issue/createmeta

                   :query param: updateHistory, datatype -> boolean
                   :body param: transition, fields, update, historyMetadata, datatype -> object
                              : properties, datatype -> Array<EntityProperty>
                              : Additional Properties, datatype -> Any

                  POST - Bulk create issue
                      Creates issues and, where the option to create subtasks is enabled in Jira, subtasks.
                      :body param: issueUpdates, datatype -> Array<IssueUpdateDetails>
                                 : Additional Properties, datatype -> Any

                  GET - Create issue metadata
                  Returns details of projects, issue types within projects, and, when requested,
                  the create screen fields for each issue type for the user.
                  :query param: projectIds, projectKeys, issuetypeIds, issuetypeNames, datatype -> Array<string>
                              : expand, datatype -> string

                  GET - Get issue
                  Return the details of an issue
                  endpoint  /rest/api/3/issue/{issueIdOrKey}
                  :query param: issue_key_or_id required
                              : fields, properties, datatype -> Array<string>
                              : fieldsByKeys, updateHistory,  datatype -> boolean
                              : expand, datatype -> string

                  PUT - Edits an issue. A transition may be applied and issue properties updated as part of the edit.
                  endpoint  /rest/api/3/issue/{issueIdOrKey}
                  :query param: issue_key_or_id required
                              : notifyUsers, overrideScreenSecurity, overrideEditableFlag, datatype -> boolean
                  :body param: transition, fields, update, historyMetadata, properties, Additional Properties,
                              datatype -> object

                  DELETE - Deletes an issue.
                  endpoint  /rest/api/3/issue/{issueIdOrKey}
                  :query param: issue_key_or_id required
                              : deleteSubtasks, datatype -> string, values = (true | false)
        """
        if uri is not None and query is None:
            return "{}/rest/api/3/issue/{}".format(LOGIN.base_url, uri)
        elif uri is not None and query is not None:
            return "{}/rest/api/3/issue/{}?{}".format(LOGIN.base_url, uri, query)
        else:
            if issue_key_or_id is not None and query is None:
                return "{}/rest/api/3/issue/{}".format(LOGIN.base_url, issue_key_or_id)
            elif issue_key_or_id is not None and query is not None:
                return "{}/rest/api/3/issue/{}?{}".format(LOGIN.base_url, issue_key_or_id, query)
            else:
                return "{}/rest/api/3/issue".format(LOGIN.base_url)


def echo(obj):
    """A Call to the Echo Class."""
    e = Echo()
    return e.echo(raw=obj)


endpoint = EndPoints()
