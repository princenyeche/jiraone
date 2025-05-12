#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Contains all Classes used to Authenticate Jira, endpoints and PrettyPrint.

- Instantiate the endpoint to Jira API
- alias to Authentication
- alias to Endpoints
- friendly name to PrettyPrint
"""
import string
import random
import sys
import json
from typing import Any, Optional, Union, Dict, List
from pprint import PrettyPrinter
import requests
from requests.auth import HTTPBasicAuth
from jiraone.exceptions import JiraOneErrors
from jiraone.jira_logs import add_log


class Credentials:
    """class.Credentials -> used for authentication of the user
    to the Instance."""

    auth_request = None
    headers = None
    api = True
    auth2_0 = None

    def __init__(
        self,
        user: str,
        password: str,
        url: str = None,
        oauth: dict = None,
        session: Any = None,
    ) -> None:
        """
        Instantiate the login.

        .. versionadded:: 0.6.2

        oauth - Allows the ability to use Atlassian OAuth 2.0 3LO to
                authenticate to Jira. It supports various scopes configured from
                your `Developer Console`_

        session - Provides a means to access the request session.

        save_oauth - Is a property value which provides a dictionary
        object of the current oauth token.

        instance_name - Is an attribute of the connected instance using OAuth.
        Accessing this attribute when OAuth isn't use returns ``None``.

        :param user:  A username or email address

        :param password:  A user password or API token

        :param url: A server url or cloud instance url

        :param oauth: An OAuth authentication request.

        :param session: Creates a context session

        .. _Developer Console: https://developer.atlassian.com/console/myapps/

        :return: None
        """
        self.base_url = url
        self.user = user
        self.password = password
        self.oauth = oauth
        self.instance_name = None

        if session is None:
            self.session = requests.Session()
        else:
            self.session = session

        if self.user is not None and self.password is not None:
            self.token_session(self.user, self.password)
        elif oauth is not None:
            self.oauth_session(self.oauth)

    def oauth_session(self, oauth: dict) -> None:
        """A session initializer to HTTP request using OAuth.

        This method implements the ``Atlassian OAuth 2.0 3LO implementation.
        To reissue token, this method uses a refresh token session.
        This is possible, if the scope in the ``callback_url``
        contains ``offline_access``.

        .. code-block:: python

           client = {
               "client_id": "JixkXXX",
               "client_secret": "KmnlXXXX",
               "name": "nexusfive",
               "callback_url": "https://auth.atlassian.com/XXXXX"
           }

        A typical client object should look like the above.
        Which is passed to the ``LOGIN`` initializer as below.
        The ``name`` key is needed to specifically target an instance,
        but it is optional if you have multiple instances that your app is
        connected to. The ``client_id``, ``client_secret``
        and ``callback_url`` are mandatory.

        .. code-block:: python

           from jiraone import LOGIN

           # previous expression
           LOGIN(oauth=client)

        To store and reuse the oauth token, you will need to call the
        property value. This object is a string which can be stored
        to a database and pulled as a variable.

        .. code-block:: python

           #  Example for storing the OAuth token
           dumps = LOGIN.save_oauth # this is a property value which contains a
           # dict of tokens in strings
           # As long as a handshake has been allowed with OAuth,
           # the above should exist.
           LOGIN.save_oauth = f"{json.dumps(dumps)}"
           # with the above string, you can easily save your
           # OAuth tokens into a DB or file.
           # Please note that when you initialize the oauth method,
           # you do not need to set
           # The property variable, as it will be set automatically
           # after initialization.
           # But you can assign other string objects to it or make a call to it.


        :param oauth: A dictionary containing the client and secret
                     information and any  other client information that
                     can be represented within the data structure.


        :return: None
        """
        if not isinstance(oauth, dict):
            add_log("Wrong data type received for " "the oauth argument.", "error")
            raise JiraOneErrors(
                "wrong",
                "Excepting a dictionary object got {} instead.".format(type(oauth)),
            )
        if (
            "client_id" not in oauth
            or "client_secret" not in oauth
            or "callback_url" not in oauth
        ):
            add_log(
                "You seem to be missing a key or " "keys in your oauth argument.",
                "debug",
            )
            raise JiraOneErrors(
                "value",
                "You seem to be missing some vital "
                "keys in your request."
                "Please check your oauth supplied "
                "data that all keys are present.",
            )
        tokens = {}
        oauth_data = {
            "token_url": "https://auth.atlassian.com/oauth/token",
            "cloud_url": "https://api.atlassian.com/oauth/token/accessible-resources",
            "base_url": "https://api.atlassian.com/ex/jira/{cloud}",
        }

        def token_update(token) -> None:
            """Updates the token to environment variable."""
            self.session.auth = token
            self.auth2_0 = f"{json.dumps(token)}"

        def get_cloud_id():
            """Retrieve the cloud id of connected instance."""
            cloud_id = requests.get(
                oauth_data["cloud_url"], headers=self.headers
            ).json()
            for ids in cloud_id:
                if ids["name"] == oauth.get("name"):
                    self.instance_name = ids["name"]
                    LOGIN.base_url = oauth_data.get("base_url").format(cloud=ids["id"])
                else:
                    self.instance_name = cloud_id[0]["name"]
                    LOGIN.base_url = oauth_data.get("base_url").format(
                        cloud=cloud_id[0]["id"]
                    )
            tokens.update({"base_url": LOGIN.base_url, "ins_name": self.instance_name})

        if self.auth2_0:
            sess = json.loads(self.auth2_0)
            oauth_data.update({"base_url": sess.pop("base_url")})
            self.instance_name = sess.pop("ins_name")
            tokens.update(sess)
            body = {
                "grant_type": "refresh_token",
                "client_id": oauth.get("client_id"),
                "client_secret": oauth.get("client_secret"),
                "refresh_token": tokens.get("refresh_token"),
            }
            get_token = requests.post(
                oauth_data["token_url"], json=body, headers=self.headers
            )
            if get_token.status_code < 300:
                access_token = get_token.json()["access_token"]
                refresh = get_token.json()["refresh_token"]
                expires = get_token.json()["expires_in"]
                scope = get_token.json()["scope"]
                token_type = get_token.json()["token_type"]
                extra = {"type": token_type, "token": access_token}
                tokens.update(
                    {
                        "access_token": access_token,
                        "expires_in": expires,
                        "scope": scope,
                        "refresh_token": refresh,
                    }
                )
                self.__token_only_session__(extra)
                get_cloud_id()
            else:
                add_log(
                    "Token refresh has failed to revalidate. "
                    "Reason [{} - {}]".format(
                        get_token.reason, json.loads(get_token.content)
                    ),
                    "debug",
                )
                raise JiraOneErrors(
                    "login",
                    "Refreshing token failed with code {}".format(
                        get_token.status_code
                    ),
                )

        def generate_state(i):
            """Generates a random key for state variable."""
            char = string.ascii_lowercase
            return "".join(random.choice(char) for _ in range(i))

        def validate_uri(uri) -> bool:
            """Return true or false for a sanitize version of the input url"""
            import urllib.parse

            check_url = oauth.get("callback_url").split("&")
            hostname = None
            for url in check_url:
                if url.startswith("redirect_uri"):
                    hostname = urllib.parse.unquote(url.split("=")[1])
            return hostname == uri

        state = generate_state(12)
        if tokens:
            LOGIN.base_url = oauth_data.get("base_url")
        if not tokens:
            # add an offline_access to the scope, so we can get a refresh token
            call_back = oauth.get("callback_url").replace(
                "scope=", "scope=offline_access%20", 1
            )
            oauth.update({"callback_url": call_back})
            callback = oauth.get("callback_url").format(YOUR_USER_BOUND_VALUE=state)
            print("Please click or copy the link into your browser and hit Enter!")
            print(callback)
            redirect_url = input("Enter the redirect url: \n")
            # Check if the supplied url is true to the one
            # which exist in callback_url
            validate_url = validate_uri(redirect_url.split("?")[0].rstrip("/"))
            assert (
                validate_url is True
            ), "Your URL seems invalid as it cannot be validated."
            code = redirect_url.split("?")[1].split("&")[1].split("=")[-1]
            body = {
                "grant_type": "authorization_code",
                "client_id": oauth.get("client_id"),
                "client_secret": oauth.get("client_secret"),
                "code": code,
                "redirect_uri": redirect_url,
            }
            get_token = requests.post(
                oauth_data["token_url"], json=body, headers=self.headers
            )
            if get_token.status_code < 300:
                access_token = get_token.json()["access_token"]
                refresh = get_token.json()["refresh_token"]
                expires = get_token.json()["expires_in"]
                scope = get_token.json()["scope"]
                token_type = get_token.json()["token_type"]
                extra = {"type": token_type, "token": access_token}
                tokens.update(
                    {
                        "access_token": access_token,
                        "expires_in": expires,
                        "scope": scope,
                        "token_type": token_type,
                        "refresh_token": refresh,
                    }
                )
                self.__token_only_session__(extra)
                get_cloud_id()
            else:
                add_log(
                    "The connection using OAuth was unable to connect, please "
                    "check your client key or client secret. "
                    "Reason [{} - {}]".format(
                        get_token.reason, json.loads(get_token.content)
                    ),
                    "debug",
                )
                raise JiraOneErrors(
                    "login", "Could not establish " "the OAuth connection."
                )

        print("Connected to instance:", self.instance_name)
        token_update(tokens)

    @property
    def save_oauth(self) -> str:
        """Defines the OAuth data to save."""
        return self.auth2_0

    @save_oauth.setter
    def save_oauth(self, oauth: Any) -> None:
        """Sets the OAuth data."""
        self.auth2_0 = oauth

    def __token_only_session__(self, token: dict) -> None:
        """Creates a token bearer session.

        :param token: A dict containing token info.

        :return: None
        """
        self.headers = {"Content-Type": "application/json"}
        self.headers.update(
            {"Authorization": "{} {}".format(token["type"], token["token"])}
        )

    # produce a session for the script and save the session
    def token_session(
        self,
        email: str = None,
        token: str = None,
        sess: str = None,
        _type: str = "Bearer",
    ) -> None:
        """
        A session initializer to HTTP request.


        .. versionadded:: 0.7.1

        _type - Datatype(string) - Allows a change of the Authorization type

        .. versionadded:: 0.6.5

        sess - Datatype(string) - Allows the use of an Authorization header

        :param email: An email address or username

        :param token: An API token or user password

        :param sess: Triggers an Authorization bearer session

        :param _type: An acceptable Authorization type
                     e.g. Bearer or JWT or ...

        :return: None
        """
        if sess is None:
            self.auth_request = HTTPBasicAuth(email, token)
            self.headers = {"Content-Type": "application/json"}
        else:
            if LOGIN.base_url is None:
                raise JiraOneErrors(
                    "value",
                    "Please include a connecting "
                    "base URL by declaring "
                    " LOGIN.base_url "
                    '= "https://yourinstance.atlassian.net"',
                )
            extra = {"type": _type, "token": sess}
            self.__token_only_session__(extra)

    def get(self, url: str, *args, payload: dict = None, **kwargs) -> requests.Response:
        """
        A get request to HTTP request.

        :param url: A valid URL

        :param args: Additional arguments if any

        :param payload: A JSON data representation

        :param kwargs: Additional keyword arguments to ``requests`` module

        :return: An HTTP response
        """
        response = requests.get(
            url,
            *args,
            auth=self.auth_request,
            json=payload,
            headers=self.headers,
            **kwargs,
        )
        return response

    def post(
        self, url: str, *args: Any, payload: dict = None, **kwargs
    ) -> requests.Response:
        """
        A post  request to HTTP request.

        :param url: A valid URL

        :param args: Additional arguments if any

        :param payload: A JSON data representation

        :param kwargs: Additional keyword arguments to ``requests`` module


        :return: An HTTP response
        """
        response = requests.post(
            url,
            *args,
            auth=self.auth_request,
            json=payload,
            headers=self.headers,
            **kwargs,
        )
        return response

    def put(self, url: str, *args, payload: dict = None, **kwargs) -> requests.Response:
        """
        A put request to HTTP request.

        :param url: A valid URL

        :param args: Additional arguments if any

        :param payload: A JSON data representation

        :param kwargs: Additional keyword arguments to ``requests`` module

        :return: An HTTP response
        """
        response = requests.put(
            url,
            *args,
            auth=self.auth_request,
            json=payload,
            headers=self.headers,
            **kwargs,
        )
        return response

    def delete(self, url: str, **kwargs) -> requests.Response:
        """
        A delete request to HTTP request.

        :param url: A valid URL

        :param kwargs: Additional keyword arguments to ``requests`` module

        :return: An HTTP response
        """
        response = requests.delete(
            url, auth=self.auth_request, headers=self.headers, **kwargs
        )
        return response

    def custom_method(self, *args, **kwargs) -> requests.Response:
        """
        A custom request to HTTP request.

        .. code-block:: python

           import jiraone
           # previous login expression
           req = jiraone.LOGIN.custom_method('GET', 'https://nexusfive.atlassian.net')
           print(req)
           # <Response [200]>

        :param args: The HTTP method type e.g. PUT, PATCH, DELETE etc

                    Also, includes the URL that needs to be queried.

        :param kwargs: Additional keyword arguments to ``requests`` module

                     For example::

                       json={"file": content}
                       data={"file": content}

        :return: An HTTP response
        """
        response = requests.request(
            *args, auth=self.auth_request, headers=self.headers, **kwargs
        )
        return response

    @staticmethod
    def from_jira(obj: Any) -> Any:
        """Performs a login initialization from a ``JIRA`` object.
        The authentication, looks into basic auth from
        the ``jira`` python package. It returns the same JIRA object
        after authentication happens, so you can easily access all
        the authenticated instances of both ``jira`` and ``jiraone``
        packages.

        Example 1::

         from jira import JIRA
         from jiraone import LOGIN, endpoint

         my_jira = JIRA(server="https://nexusfive.atlassian.net",
                 basic_auth=("prince@example.com",
                 "MXKSlsXXXXX"))
         LOGIN.from_jira(my_jira)
         print(LOGIN.get(endpoint.myself()))
         # response
         # <Response [200]>


        You can assign a variable to the jiraone :meth:`LOGIN.from_jira`
        and continue to use both ``jira`` and ``jiraone`` packages
        simultaneously.

        Example 2::

         from jira import JIRA
         from jiraone import LOGIN, PROJECT

         jiras = JIRA(server="https://nexusfive.atlassian.net",
                 basic_auth=("prince@example.com",
                 "MXKSlsXXXXX"))
         my_jira = LOGIN.from_jira(jiras)
         # Making a request to JIRA's methods
         print(my_jira.myself())
         # response
         # {'self': 'https://example.atlassian.net/rest/api/2/user?
         #            accountId=557058:xxx',
         #           'accountId': '557058:xxx'}
         # Making a request to jiraone's methods
         jql = "project = CT ORDER BY Created DESC"
         print(PROJECT.issue_count(jql))
         # response
         # {'count': 18230, 'max_page': 18}

        :param obj: A call to a ``JIRA`` Interface

        :return: JIRA object
        """
        try:
            if hasattr(obj, "_session"):
                if obj._session.auth:
                    auth = {
                        "user": obj._session.auth[0],
                        "password": obj._session.auth[1],
                        "url": obj._options["server"],
                    }
                    LOGIN(**auth)
                    return obj
                else:
                    sys.exit(
                        "Unable to read other values within the ``JIRA``"
                        " object. Authentication cannot proceed further."
                    )
            else:
                sys.exit(
                    "Could not detect a `JIRA` object from the command."
                    " Please check that you have the `jira` python package "
                    "installed."
                )
        except Exception as err:
            raise JiraOneErrors(
                "wrong",
                "An unknown exception has occurred " "Other errors: " f" {err}.",
            ) from err


class Echo(PrettyPrinter):
    """A Class used to inherit from PrettyPrinter."""

    def __init__(self, *args, **kwargs) -> None:
        """
        Inherit from the parent.

        :param args: positional arguments

        :param kwargs: additional arguments

        :return: None
        """
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        """Makes our class callable."""
        return self.__init__(*args, **kwargs)

    def echo(self, raw: Any):
        """
        Prints the formatted representation of object on stream,
        followed by a newline.

        :param raw: Any object data

        :return: None
        """
        return self.pprint(object=raw)


class InitProcess(Credentials):
    """should inherit an instance of Credential class using super().

    Object values are entered directly when called because of the __call__
    dunder method."""

    def __init__(
        self, user=None, password=None, url=None, oauth=None, session=None
    ) -> None:
        """
        A Call to the Credential Class.

        .. versionadded:: 0.6.2

        oauth argument added to support OAuth 2.0

        session argument added to create a session context

        :param user: A username or email address

        :param password: A password or user API token

        :param url: A valid URL

        :param oauth: An oAuth session

        :param session: Creates a context session

        :return: None
        """
        super().__init__(
            user=user, password=password, url=url, oauth=oauth, session=session
        )

    def __call__(self, *args, **kwargs):
        """Help to make our class callable."""
        return self.__init__(*args, **kwargs)


LOGIN = InitProcess()


class EndPoints:
    """A Structural way to dynamically load urls that is fed
    to other functions."""

    _issue_payload_: dict = None

    @classmethod
    def myself(cls) -> str:
        """Return data on your own user.

        :return: A string of the url
        """
        return "{}/rest/api/{}/myself".format(
            LOGIN.base_url, "3" if LOGIN.api is True else "latest"
        )

    @classmethod
    def search_users(
        cls, start_at: int = 0, max_result: int = 50, default: bool = False
    ) -> str:
        """Search multiple users and retrieve the data

        :param start_at: An integer record row

        :param max_result: An integer of max capacity

        :param default: Changes context between default user search
        and all search

        :return: A string of the url
        """
        if default is True:
            return "{}/rest/api/{}/users?startAt={}&maxResults={}".format(
                LOGIN.base_url,
                "3" if LOGIN.api is True else "latest",
                start_at,
                max_result,
            )
        return "{}/rest/api/{}/users/search?startAt={}&maxResults={}".format(
            LOGIN.base_url,
            "3" if LOGIN.api is True else "latest",
            start_at,
            max_result,
        )

    @classmethod
    def get_user_group(cls, account_id: str) -> str:
        """Search for the groups a user belongs to

        :param account_id: An alphanumeric required string

        :return: A string of the url
        """
        return "{}/rest/api/{}/user/groups?accountId={}".format(
            LOGIN.base_url, "3" if LOGIN.api is True else "latest", account_id
        )

    @classmethod
    def get_projects(cls, *args: Any, start_at: int = 0, max_results: int = 50) -> str:
        """Return a list of Projects available on an Instance
        How to use this endpoint ``/rest/api/3/project/search``  is mentioned
        `here
        <https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-projects/#api-rest-api-3-project-search-get>`_


                :param args: Query Parameters that are useful mostly.

                   a) query, example: query=key,name {caseInsensitive}

                   b) searchBy, example: searchBy=key,name

                   c) action, example: action=browse

                       i. available options [view, browse, edit]

                   d) status example: status=live

                       i. available options [live, archived, deleted]

                   e). expand, example: expand=insight

                        i. available options [insight, description,
                           projectKeys, url, issueTypes, lead]

                :param start_at:  defaults as keyword args,example startAt=0

                :param max_results: defaults as keyword args,
                                    example maxResults=50

        .. _here:

                :return: A string of the url
        """
        if args:
            nos = len(args)
            if nos > 0:
                param = "&".join(args)
                print("Project Search Query Parameter:", param)
                return (
                    "{}/rest/api/{}/project/search?{}&startAt={}&maxResults={}".format(
                        LOGIN.base_url,
                        "3" if LOGIN.api is True else "latest",
                        param,
                        start_at,
                        max_results,
                    )
                )
        else:
            return "{}/rest/api/{}/project/search?startAt={}&maxResults={}".format(
                LOGIN.base_url,
                "3" if LOGIN.api is True else "latest",
                start_at,
                max_results,
            )

    @classmethod
    def find_users_with_permission(cls, *args) -> str:
        """Find users with permissions to a Project.

        :param args: 1st accountId, 2nd projectKey, 3rd permissions that
                     needs checking all in caps
                     e.g "BROWSE", "CREATE_ISSUE" etc

        :return: A string of the url
        """
        return "{}/rest/api/{}/user/permission/search?accountId={}&projectKey={}&permissions={}".format(
            LOGIN.base_url, "3" if LOGIN.api is True else "latest", *args
        )

    @classmethod
    def get_roles_for_project(cls, id_or_key: Union[str, int]) -> str:
        """Returns a list of project roles for the project returning the name
        and self URL for each role.

        :param id_or_key: An issue key or id

        :return: A string of the url
        """
        return "{}/rest/api/{}/project/{}/role".format(
            LOGIN.base_url, "3" if LOGIN.api is True else "latest", id_or_key
        )

    @classmethod
    def get_project_role(cls, *args) -> str:
        """Returns a project role's details and actors associated
        with the project.

        :param args: projectKey or id or the Project id of the role

        :return: A string of the url
        """
        return "{}/rest/api/{}/project/{}/role/{}".format(
            LOGIN.base_url, "3" if LOGIN.api is True else "latest", *args
        )

    @classmethod
    def project_role(
        cls,
        attr: bool = None,
        key_or_id: Union[str, int] = None,
        role_id: int = None,
    ) -> str:
        """
        Performs multiple functions for project role from creation to
        setting of actors on projects.

        - Creates a new project role with no default actors if attr is None

        - Adds, update and delete actors to a project role for the project
          attr argument must be True to access this function
          Accepts HTTP method "PUT, POST, DELETE".

        - Returns the default actors for the project role. attr argument
          must be False

        :param attr: True if adding project role actors to a project.
                    False if removing project role actors from a project. None
                    creates the project role

        :param key_or_id: The project key or id to assign a role

        :param role_id: The id of the project role when assigning
                        actors to a project

        :return: string
        """
        if attr is None:
            return "{}/rest/api/{}/role".format(
                LOGIN.base_url, "3" if LOGIN.api is True else "latest"
            )
        elif attr is True:
            return "{}/rest/api/{}/project/{}/role/{}".format(
                LOGIN.base_url,
                "3" if LOGIN.api is True else "latest",
                key_or_id,
                role_id,
            )
        elif attr is False:
            return "{}/rest/api/{}/role/{}/actors".format(
                LOGIN.base_url, "3" if LOGIN.api is True else "latest", role_id
            )
        else:
            raise JiraOneErrors(
                "name", "Invalid request received, unable to process request"
            )

    @classmethod
    def get_all_permission_scheme(cls, query: str = None) -> str:
        """Returns all permission schemes.

        :param query: A search term for this resource.

        :return: A string of the url
        """
        if query is not None:
            return "{}/rest/api/{}/permissionscheme?{}".format(
                LOGIN.base_url, "3" if LOGIN.api is True else "latest", query
            )
        else:
            return "{}/rest/api/{}/permissionscheme".format(
                LOGIN.base_url, "3" if LOGIN.api is True else "latest"
            )

    @classmethod
    def get_all_issue_type_schemes(
        cls,
        query: Optional[str] = None,
        start_at=0,
        max_results=50,
        scheme: str = None,
    ) -> str:
        """Returns a paginated list of issue type schemes.
        Only issue type schemes used in classic projects are returned

        :param query: A search term

        :param start_at: A row record

        :param max_results: A maximum number to display

        :param scheme: create allows POST request to create issue type scheme
              (the url generated here is basic, so you can add more endpoint
              depending on the resource you're trying to reach) and "assign"
              allows assignment to a specific project

        .. versionchanged:: 0.7.9

         Scheme - Ability to either create or update an issue type scheme

        :return: A string of the url
        """
        if query is not None:
            return "{}/rest/api/{}/issuetypescheme?{}&startAt={}&maxResults={}".format(
                LOGIN.base_url,
                "3" if LOGIN.api is True else "latest",
                query,
                start_at,
                max_results,
            )
        else:
            if scheme.lower() == "create":
                return "{}/rest/api/{}/issuetypescheme".format(
                    LOGIN.base_url, "3" if LOGIN.api is True else "latest"
                )
            elif scheme.lower() == "assign":
                return "{}/rest/api/{}/issuetypescheme/project".format(
                    LOGIN.base_url, "3" if LOGIN.api is True else "latest"
                )
            elif scheme is None:
                return "{}/rest/api/{}/issuetypescheme?startAt={}&maxResults={}".format(
                    LOGIN.base_url,
                    "3" if LOGIN.api is True else "latest",
                    start_at,
                    max_results,
                )
            else:
                raise JiraOneErrors(
                    "name", "Invalid name for scheme argument received."
                )

    @classmethod
    def get_all_issue_types(cls) -> str:
        """Returns all issue types.

        If the user has the Administer Jira global permission, all issue
        types are returned.

        If the user has the "Browse projects" project permission for one
        or more projects, the issue types associated with the projects
        the user has permission to browse are returned.

        :return: A string of the url
        """
        return "{}/rest/api/{}/issuetype".format(
            LOGIN.base_url, "3" if LOGIN.api is True else "latest"
        )

    @classmethod
    def get_all_issue_security_scheme(
        cls,
        level: bool = False,
        scheme_id: str = None,
        level_id: str = None,
        attr: bool = False,
    ) -> str:
        """Returns all issue security schemes or get the security level

        :param level: Determines if a level is to be checked, then set as true

        :param scheme_id: A scheme id used for updating the security level

        :param level_id: A level id used for updating the security level

        :param attr: Returns the security level is true

         .. versionchanged:: 0.7.9

         scheme_id - The scheme_id to check for the security schemes

         level - The level to be checked

         level_id - The id of the level, used for security level update

         attr - Returns the security level endpoint

        :return: A string of the url
        """
        if level is True:
            if scheme_id:
                return "{}/rest/api/{}/issuesecurityschemes/{}/level/{}/member".format(
                    LOGIN.base_url,
                    "3" if LOGIN.api is True else "latest",
                    scheme_id,
                    level_id,
                )
            else:
                return "{}/rest/api/{}/issuesecurityschemes/level".format(
                    LOGIN.base_url, "3" if LOGIN.api is True else "latest"
                )
        else:
            if attr:
                return "{}/rest/api/{}/securitylevel".format(
                    LOGIN.base_url, "3" if LOGIN.api is True else "latest"
                )
            return "{}/rest/api/{}/issuesecurityschemes".format(
                LOGIN.base_url, "3" if LOGIN.api is True else "latest"
            )

    @classmethod
    def get_all_priorities(cls) -> str:
        """Returns the list of all issue priorities.

        :return: A string of the url
        """
        return "{}/rest/api/{}/priority".format(
            LOGIN.base_url, "3" if LOGIN.api is True else "latest"
        )

    @classmethod
    def search_all_notification_schemes(
        cls,
        query: Optional[str] = None,
        start_at=0,
        max_results=50,
        attr: bool = False,
    ) -> str:
        """Returns a paginated list of notification schemes ordered by
        display name.

        :param query:  1st String value for expand= {all, field, group, user,
                       projectRole, notificationSchemeEvents}

        :param start_at: has default value of 0

        :param max_results: has default value of 50

        :param attr: A bool value

        .. versionchanged:: 0.7.9

        attr - An indicator to switch endpoint

        :return: A string of the url
        """
        if query is not None:
            return (
                "{}/rest/api/{}/notificationscheme?{}&startAt={}&maxResults={}".format(
                    LOGIN.base_url,
                    "3" if LOGIN.api is True else "latest",
                    query,
                    start_at,
                    max_results,
                )
            )
        else:
            if attr is True:
                return "{}/rest/api/{}/notificationscheme".format(
                    LOGIN.base_url, "3" if LOGIN.api is True else "latest"
                )
            return "{}/rest/api/{}/notificationscheme?startAt={}&maxResults={}".format(
                LOGIN.base_url,
                "3" if LOGIN.api is True else "latest",
                start_at,
                max_results,
            )

    @classmethod
    def get_field(
        cls,
        query: Optional[str] = None,
        start_at: int = 0,
        max_results: int = 50,
        system: str = None,
    ) -> str:
        """Returns a paginated list of fields for Classic Jira projects.
        The list can include:

        *  all fields.

        *  specific fields, by defining id.

        *  fields that contain a string in the field name or description,
         by defining query.

         For example::

          query = "type=custom"

        *  specific fields that contain a string in the field name or
        description, by defining id and query.
        Only custom fields can be queried, type must be set to custom.

        **Find system fields**

        *  Fields that cannot be added to the issue navigator are
        always returned.

        *  Fields that cannot be placed on an issue screen are always returned.

        *  Fields that depend on global Jira settings are only returned
        if the setting is enabled. That is, timetracking fields, subtasks,
        votes, and watches.

        *  For all other fields, this operation only returns the fields that
        the user has permission to view (i.e. The field is use, in at
        least one project that the user has Browse Projects
        project permission for.)


        :param query: accepted options -> string type=custom
                     (use to search for custom fields)


        :param start_at: defaults to 0

        :param max_results: defaults to 50

        :param system: string accepts any string e.g.
                       field (use any string to denote as system)

         :return: A string of the url
        """
        if query is not None and system is None:
            return "{}/rest/api/{}/field/search?{}&startAt={}&maxResults={}".format(
                LOGIN.base_url,
                "3" if LOGIN.api is True else "latest",
                query,
                start_at,
                max_results,
            )
        elif query is None and system is not None:
            return "{}/rest/api/{}/field".format(
                LOGIN.base_url, "3" if LOGIN.api is True else "latest"
            )
        else:
            return "{}/rest/api/{}/field/search?startAt={}&maxResults={}".format(
                LOGIN.base_url,
                "3" if LOGIN.api is True else "latest",
                start_at,
                max_results,
            )

    @classmethod
    def issue_attachments(
        cls,
        id_or_key: str = None,
        attach_id: str = None,
        uri: Optional[str] = None,
        query: Optional[str] = None,
    ) -> str:
        """Returns the attachment content.

         :request GET: - Get Jira attachment settings
                         Returns the attachment settings, that is,
                         whether attachments.
                         are enabled and the maximum attachment size allowed.

         :request GET: - Get attachment metadata
                         Returns the metadata for an attachment.
                         Note that the attachment itself is not returned.

         :param attach_id: required (id of the attachment), datatype -> string

         :request DELETE: - Deletes an attachment from an issue.
                            attach_id required (id of the attachment),
                            datatype -> string.

        :request GET:  - Get all metadata for an expanded attachment.

        :param query: This argument accepts a string, check the options.

            *available options*

            * expand/human - Returns the metadata for the contents of an
                             attachment, if it is an archive,
                             and metadata for the attachment itself.
                             For example, if the attachment is a ZIP archive,
                             then information about the files in the archive is
                             returned and metadata for the ZIP archive.

            * expand/raw - Returns the metadata for the contents of an
                           attachment, if it is an archive.
                           For example, if the attachment is a ZIP archive,
                           then information about the files in the
                           archive is returned. Currently, only the ZIP archive
                           format is supported.

        :request POST: - Adds one or more attachments to an issue.
                         Attachments are posted as multipart/form-data.

         :request POST: - Adds one or more attachments to an issue.
                          Attachments are posted as multipart/form-data.

         :param id_or_key: (required) The ID or key of
                           the issue that are added to and attachments.

         :param uri: various endpoint to attachment.


         :return: A string of the url
        """
        if uri is not None:
            return "{}/rest/api/{}/attachment/{}".format(
                LOGIN.base_url, "3" if LOGIN.api is True else "latest", uri
            )
        else:
            if query is not None and attach_id is not None and id_or_key is None:
                return "{}/rest/api/{}/attachment/{}/{}".format(
                    LOGIN.base_url,
                    "3" if LOGIN.api is True else "latest",
                    attach_id,
                    query,
                )
            elif query is not None and attach_id is None and id_or_key is not None:
                return "{}/rest/api/{}/issue/{}/{}".format(
                    LOGIN.base_url,
                    "3" if LOGIN.api is True else "latest",
                    id_or_key,
                    query,
                )
            else:
                return "{}/rest/api/{}/attachment/{}".format(
                    LOGIN.base_url,
                    "3" if LOGIN.api is True else "latest",
                    attach_id,
                )

    @classmethod
    def search_issues_jql(
        cls, query: str, start_at: int = 0, max_results: int = 50
    ) -> str:
        """Searches for issues using JQL.

        :param query: A search term.

        :param start_at: A record start row

        :param max_results: A max result to return

        :return: A string of the url
        """
        from warnings import warn

        current_api = LOGIN.api
        if current_api is True:
            warn("This endpoint has been deprecated for Jira Cloud, "
                 "please use the newer endpoint `search_cloud_issues`. "
                 "For more info on this deprecation, "
                 "[see](https://developer.atlassian.com/cloud/jira/platform/changelog/#CHANGE-2046)",
                 category=DeprecationWarning,
                 stacklevel=2)
        return "{}/rest/api/{}/search?jql={}&startAt={}&maxResults={}".format(
            LOGIN.base_url,
            "3" if LOGIN.api is True else "latest",
            query,
            start_at,
            max_results,
        )

    @classmethod
    def search_cloud_issues(cls,
                            query: str,
                            next_page: str = None,
                            max_results: int = 50,
                            **kwargs: Any) -> str:
        """
            Searches for cloud issues using JQL. In order to send a POST request,
            you must send a payload in the request body.
            `See <https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/#api-rest-api-3-search-jql-post>`_


            :param query: A search term using JQL with a bounded query
                         E.g. ``assignee = currentUser() order by key``

            :param next_page: A next page data URL.

            :param max_results: A max result to return, default is 50 and
                                max result is 5000

            :param kwargs: Additional keyword arguments.

                         **Acceptable arguments are**:
                         * method - string values "GET" or "POST"
                         * fields - list[str] defaults to "*all", you can use
                                    "*all,-comment" - return all fields except
                                     comments. Specify fields returned by name
                         * expand - string defaults to None, you can use
                                    "schema,names"
                         * properties - string -A list of up to 5 issue
                                        properties to include in the results
                                        defaults to None
                         * fields_by_keys - bool - Reference fields by their key
                                        (rather than ID)
                         * fail_fast - bool - Fail this request early if we
                                     can't retrieve all field data. Only for GET request.
                         * reconcile_issues - list[int] - Strong consistency
                                          issue ids to be reconciled



            .. _See
            :return: A string of the url
        """
        from jiraone.utils import create_urls, validate_argument_name

        method: str = kwargs.get("method", "GET")
        fields: Union[str, list[str], None] = kwargs.get("fields", "*all")
        expand: Union[str, None] = kwargs.get("expand", "schema,names")
        properties: Union[str, list[str], None] = kwargs.get("properties", None)
        fields_by_keys: bool = kwargs.get("fields_by_keys", False)
        fail_fast: bool = kwargs.get("fail_fast", False)
        reconcile_issues: Union[int, list[int], None] = kwargs.get(
            "reconcile_issues", None)
        field_names: list = ["method", "fields", "expand", "properties",
                             "fields_by_keys", "reconcile_issues", "next_page",
                       "query", "max_results", "fail_fast"]
        for key, value in kwargs.items():
            validate_argument_name(key, field_names)
        if max_results < 1:
            raise JiraOneErrors(
                "error",
                "The `max_results` argument cannot be "
                "lesser than 1 item")
        if max_results > 5000:
            raise JiraOneErrors(
                "error",
                "The `max_results` argument cannot be "
                "greater than 5000")
        return (LOGIN.base_url + create_urls(
            query=query,
            method=method,
            fields=fields,
            expand=expand,
            properties=properties,
            fields_by_keys=fields_by_keys,
            fail_fast=fail_fast,
            reconcile_issues=reconcile_issues,
            max_results=max_results,
            next_page=next_page,
        )
                )


    @property
    def get_issue_search_payload(self) -> dict:
        """
        Returns a dict object of the ``endpoint.search_cloud_issues`` arguments
        """
        return self._issue_payload_

    @get_issue_search_payload.setter
    def get_issue_search_payload(self, payload: dict) -> None:
        """
        Sets the POST request payload of ``endpoint.search_cloud_issues``
        """
        self._issue_payload_ = payload

    @classmethod
    def search_issue_count(cls) -> str:
        """Returns a URL for JQL issue search count.
        :request POST: The endpoint requires that you send a POST request
                      with a payload in the request body.

                  :body param:

                    * jql - A search term using JQL in strings

        :return: A string of the url
        """
        return LOGIN.base_url + "/rest/api/3/search/approximate-count"


    @classmethod
    def search_for_filters(cls, query: Optional[str] = None, start_at: int = 0) -> str:
        """Returns a paginated list of filters. Use this operation to get:

        *  specific filters, by defining id only.

        *  filters that match all the specified attributes. For example,
           all filters

           for a user with a particular word in their name.
           When multiple attributes are
           specified only filters matching all attributes are returned.

        :param query: 1st String value filterName, accountId,
                      owner, groupname, projectId

        :param start_at:  has default value of 0

        :param: filled: - maxResults=50 (default)

        :return: A string of the url
        """
        if query is not None:
            return "{}/rest/api/{}/filter/search?{}&startAt={}&maxResults=50".format(
                LOGIN.base_url,
                "3" if LOGIN.api is True else "latest",
                query,
                start_at,
            )
        else:
            return "{}/rest/api/{}/filter/search?startAt={}&maxResults=50".format(
                LOGIN.base_url,
                "3" if LOGIN.api is True else "latest",
                start_at,
            )

    @classmethod
    def search_for_dashboard(
        cls, query: Optional[str] = None, start_at: int = 0
    ) -> str:
        """Returns a paginated list of dashboards. This operation is similar to

        Get dashboards except that the results can be refined to include
        dashboards that have specific attributes. For example,
        dashboards with a particular name. When multiple attributes are
        specified only filters matching all attributes are returned.

        :param query: 1st String value dashboardName, accountId,
                      owner, groupname, projectId

        :param start_at:  has default value of 0

        :param: filled: - maxResult=20 (default)

        :return: A string of the url
        """
        if query is not None:
            return "{}/rest/api/{}/dashboard/search?{}&startAt={}&maxResults=20".format(
                LOGIN.base_url,
                "3" if LOGIN.api is True else "latest",
                query,
                start_at,
            )
        else:
            return "{}/rest/api/{}/dashboard/search?startAt={}&maxResults=20".format(
                LOGIN.base_url, "3" if LOGIN.api is True else "latest", start_at
            )

    @classmethod
    def get_dashboard(cls, dashboard_id: int) -> str:
        """Gets the dashboard.

        :param dashboard_id: An id for the dashboard

        :return: A string of the url
        """
        return "{}/rest/api/{}/dashboard/{}".format(
            LOGIN.base_url, "3" if LOGIN.api is True else "latest", dashboard_id
        )

    @classmethod
    def get_all_application_role(cls) -> str:
        """
        Returns all application roles.

        In Jira, application roles are managed using the Application
        access configuration page.

        :return: A string of the url
        """
        return "{}/rest/api/{}/applicationrole".format(
            LOGIN.base_url, "3" if LOGIN.api is True else "latest"
        )

    @classmethod
    def search_all_workflows(cls, query: int = 0) -> str:
        """
        Returns a paginated list of published classic workflows.
        When workflow names are specified.

        details of those workflows are returned. Otherwise,
        all published classic workflows are returned.
        This operation does not return next-gen workflows.

        :param query:  has default value of 0

                      * filled - maxResults=50 (default)

        :return: A string of the url
        """
        return "{}/rest/api/{}/workflow/search?startAt={}&maxResults=50".format(
            LOGIN.base_url, "3" if LOGIN.api is True else "latest", query
        )

    @classmethod
    def search_all_workflow_schemes(cls, query: int = 0) -> str:
        """Returns a paginated list of all workflow schemes,
        not including draft workflow schemes.

        :param query: has default value of 0

                    * filled - maxResults=50 (default)

        :return: A string of the url
        """
        return "{}/rest/api/{}/workflowscheme?startAt={}&maxResults=50".format(
            LOGIN.base_url, "3" if LOGIN.api is True else "latest", query
        )

    @classmethod
    def search_all_screens(cls, query: int = 0) -> str:
        """Returns a paginated list of all screens or those
        specified by one or more screen IDs.

        :param query: has default value of 0

        * maxResults=100 (default)

        :return: A string of the url
        """
        return "{}/rest/api/{}/screens?startAt={}&maxResults=100".format(
            LOGIN.base_url, "3" if LOGIN.api is True else "latest", query
        )

    @classmethod
    def search_for_screen_schemes(cls, query: int = 0) -> str:
        """Returns a paginated list of screen schemes.

        Only screen schemes used in classic projects are returned.

        :param query: has default value of 0

        * maxResults=25 (default)

        :return: A string of the url
        """
        return "{}/rest/api/{}/screenscheme?startAt={}&maxResults=25".format(
            LOGIN.base_url, "3" if LOGIN.api is True else "latest", query
        )

    @classmethod
    def get_project_component(
        cls,
        ids: str = None,
        id_or_key: Union[str, int] = None,
        move_to: str = None,
        **kwargs: Any,
    ) -> str:
        """Returns all components in a project.
        See the Get project components paginated resource if you want to
        get a full list of components with pagination. The project ID or
        project key (case-sensitive).

        :param ids: A component id (required for GET, PUT, DEL)
        :param id_or_key: An issue key or id
        :param move_to: An id of a component to replace
        :param kwargs: Any additional arguments to pass

                       **Acceptable options**

                       - issue_count: Count issues of a component

                       - pagination: Allows project component pagination.
                                     For pagination argument, you can combine
                                     the query argument to get more details.

                       - query: A query parameter for pagination argument.
                                e.g. startAt=0&maxResults=50


        :request POST: Creates a component. Use components to provide containers
                     for issues within a project.
            :body param:
               * assignee - Datatype (User) - denoting a user object
               * assigneeType - Datatype (str)
               * description - Datatype (str)
               * id - Datatype(str)
               * isAssigneeTypeValid - Datatype (bool)
               * lead - Datatype (User) - denoting a user object
               * leadAccountId - Datatype (str)
               * leadUserName - Datatype (str)
               * name - Datatype (str)
               * project - Datatype (str)
               * projectId - Datatype (int)
               * realAssignee - Datatype (User)
               * realAssigneeType - Datatype (str)
               * self - Datatype (str)

            Example::

                body = {
                   "assigneeType": "PROJECT_LEAD",
                   "description": "This is a Jira component",
                   "isAssigneeTypeValid": false,
                   "leadAccountId": "5b10a2844cxxxxxx700ede21g",
                   "name": "Component 1",
                   "project": "BAC"
                  }

        :request GET: Returns a component.This operation can be
                      accessed anonymously.

        :request PUT: Updates a component. Any fields included in
                      the request are overwritten

            :body param:
               * assignee - Datatype (User) - denoting a user object
               * assigneeType - Datatype (str)
               * description - Datatype (str)
               * id - Datatype(str)
               * isAssigneeTypeValid - Datatype (bool)
               * lead - Datatype (User) - denoting a user object
               * leadAccountId - Datatype (str)
               * leadUserName - Datatype (str)
               * name - Datatype (str)
               * project - Datatype (str)
               * projectId - Datatype (int)
               * realAssignee - Datatype (User)
               * realAssigneeType - Datatype (str)
               * self - Datatype (str)

        :request DELETE: Deletes a component.
            :query param: moveIssuesTo


        :return: A string of the url
        """
        issue_count: bool = kwargs.get("issue_count", False)
        pagination: bool = kwargs.get("pagination", False)
        query: str = kwargs.get("query") if "query" in kwargs else None
        if ids is not None:
            if move_to is not None:
                return "{}/rest/api/{}/component/{}?moveIssuesTo={}".format(
                    LOGIN.base_url,
                    "3" if LOGIN.api is True else "latest",
                    ids,
                    move_to,
                )
            else:
                if issue_count is True:
                    return "{}/rest/api/{}/component/{}/relatedIssueCounts".format(
                        LOGIN.base_url,
                        "3" if LOGIN.api is True else "latest",
                        ids,
                    )
                else:
                    return "{}/rest/api/{}/component/{}".format(
                        LOGIN.base_url,
                        "3" if LOGIN.api is True else "latest",
                        ids,
                    )
        elif id_or_key is not None:
            if pagination is True:
                if query is not None:
                    return "{}/rest/api/{}/project/{}/component?{}".format(
                        LOGIN.base_url,
                        "3" if LOGIN.api is True else "latest",
                        id_or_key,
                        query,
                    )
                else:
                    return "{}/rest/api/{}/project/{}/component".format(
                        LOGIN.base_url,
                        "3" if LOGIN.api is True else "latest",
                        id_or_key,
                    )
            else:
                return "{}/rest/api/{}/project/{}/components".format(
                    LOGIN.base_url,
                    "3" if LOGIN.api is True else "latest",
                    id_or_key,
                )
        else:
            return "{}/rest/api/{}/component".format(
                LOGIN.base_url, "3" if LOGIN.api is True else "latest"
            )

    @classmethod
    def get_project_versions(
        cls,
        ids: str = None,
        id_or_key: Union[str, int] = None,
        move: bool = False,
        **kwargs: Any,
    ):
        """Returns all versions in a project. See the Get project version
        paginated. Resource if you want to get a full list of versions
        without pagination.

        :param ids: A version id (required for GET, PUT, POST)
        :param id_or_key: An issue key or id
        :param move: Modifies the version's sequence within the project
        :param kwargs: Additional keyword arguments to provide

                       **Acceptable options**

                       - move_to_issue: The ID of the version to merge into.

                       - swap: Deletes a project version. Used with POST method

                       - issue_count: Count issues of a version. Used with
                                      GET method

                       - unresolved_count: Count of a version's unresolved
                                           issues.Used with "GET" method

                       - pagination: Allows project version pagination

                       - query: A query parameter for pagination argument.
                                e.g. startAt=0&maxResults=50

        :request POST: Creates a version.

            :body param:
               * archived - Datatype (bool)
               * expand - Datatype (str)
               * description - Datatype (str)
               * id - Datatype(str)
               * issueStatusForFixVersion - Datatype (VersionIssueStatus)
               * moveUnfixIssuesTo - Datatype (str)
               * name - Datatype (str)
               * operations - Datatype (list)
               * overdue - Datatype (bool)
               * project - Datatype (str)
               * projectId - Datatype (int)
               * releaseDate - Datatype (str)
               * release - Datatype (bool)
               * startDate - Datatype (str)
               * userReleaseDate - Datatype (str)
               * userStateDate - Datatype (str)
               * self - Datatype (str)

            Example::

                body = {
                 "archived": false,
                 "description": "An excellent version",
                  "name": "New Version 1",
                 "projectId": 10000,
                 "releaseDate": "2010-07-06",
                "released": true
                }

        :request GET: Returns all versions in a project.This operation can be
                     accessed anonymously. You can either use a return of
                     all version or use the pagination argument for a paginated
                     list of all versions. Project key required

            :query param: Used for query argument in pagination
                         The query argument is a string and can be
                         constructed as below.

             Example::

             query = "startAt=0&maxResults=50&orderBy=description,name&status=released
             &expand=issuestatus"

        :request PUT: Updates a version. An id must be supplied

            :body param:
               * archived - Datatype (bool)
               * expand - Datatype (str)
               * description - Datatype (str)
               * id - Datatype(str)
               * issueStatusForFixVersion - Datatype (VersionIssueStatus)
               * moveUnfixIssuesTo - Datatype (str)
               * name - Datatype (str)
               * operations - Datatype (list)
               * overdue - Datatype (bool)
               * project - Datatype (str)
               * projectId - Datatype (int)
               * releaseDate - Datatype (str)
               * release - Datatype (bool)
               * startDate - Datatype (str)
               * userReleaseDate - Datatype (str)
               * userStateDate - Datatype (str)
               * self - Datatype (str)

        :request POST: Deletes a version.

            :body param: Used with delete and replace version

                * customFieldReplacementList - Datatype (list)
                * moveAffectedIssuesTo - Datatype (int)
                * moveFixedIssuesTo - Datatype (int)

            Example::

              body = {
                    "customFieldReplacementList": [
                           {
                       "customFieldId": 66,
                      "moveTo": 67
                          }
                               ],
                         "moveAffectedIssuesTo": 97,
                        "moveFixIssuesTo": 92
                         }

            :body param: Moves a version

                 * after - Datatype (str)
                 * position - - Datatype (str)


        :return: A string of the url
        """
        move_to_issue: str = (
            kwargs.get("move_to_issue") if "move_to_issue" in kwargs else None
        )
        issue_count: bool = kwargs.get("issue_count", False)
        unresolved_count: bool = kwargs.get("unresolved_count", False)
        pagination: bool = kwargs.get("pagination", False)
        swap: bool = kwargs.get("swap", False)
        query: str = kwargs.get("query") if "query" in kwargs else None
        if ids is not None:
            if move is True:
                if move_to_issue is not None:
                    return "{}/rest/api/{}/version/{}/mergeto/{}".format(
                        LOGIN.base_url,
                        "3" if LOGIN.api is True else "latest",
                        ids,
                        move,
                    )
                else:
                    return "{}/rest/api/{}/version/{}/move".format(
                        LOGIN.base_url,
                        "3" if LOGIN.api is True else "latest",
                        ids,
                    )

            else:
                if issue_count is True:
                    return "{}/rest/api/{}/version/{}/relatedIssueCounts".format(
                        LOGIN.base_url,
                        "3" if LOGIN.api is True else "latest",
                        ids,
                    )
                elif unresolved_count is True:
                    return "{}/rest/api/{}/version/{}/unresolvedIssueCount".format(
                        LOGIN.base_url,
                        "3" if LOGIN.api is True else "latest",
                        ids,
                    )
                else:
                    if swap is True:
                        return "{}/rest/api/{}/version/{}/removeAndSwap".format(
                            LOGIN.base_url,
                            "3" if LOGIN.api is True else "latest",
                            ids,
                        )
                    else:
                        return "{}/rest/api/{}/version/{}".format(
                            LOGIN.base_url,
                            "3" if LOGIN.api is True else "latest",
                            ids,
                        )
        elif id_or_key is not None:
            if pagination is True:
                if query is not None:
                    return "{}/rest/api/{}/project/{}/version?{}".format(
                        LOGIN.base_url,
                        "3" if LOGIN.api is True else "latest",
                        id_or_key,
                        query,
                    )
                else:
                    return "{}/rest/api/{}/project/{}/version".format(
                        LOGIN.base_url,
                        "3" if LOGIN.api is True else "latest",
                        id_or_key,
                    )
            else:
                return "{}/rest/api/{}/project/{}/versions".format(
                    LOGIN.base_url,
                    "3" if LOGIN.api is True else "latest",
                    id_or_key,
                )
        else:
            return "{}/rest/api/{}/version".format(
                LOGIN.base_url, "3" if LOGIN.api is True else "latest"
            )

    @classmethod
    def get_resolutions(cls) -> str:
        """Returns a list of all issue resolution values.
        :return: A string of the url
        """
        return "{}/rest/api/{}/resolution".format(
            LOGIN.base_url, "3" if LOGIN.api is True else "latest"
        )

    @classmethod
    def remote_links(
        cls, key_or_id: Optional[str] = None, link_id: Optional[str] = None
    ) -> str:
        """Returns the remote issue links for an issue.
        When a remote issue link global ID is provided
        the record with that global ID is returned.

        When using PUT and POST method, the body parameter
        are similar and the object body parameter is
        required.

        When using the DELETE method, you can delete
        remote issue link by globalId or, you can delete
        by id

        :request GET: Gets the remote link
        :param key_or_id: The ID or key of the issue.
           :body param: globalId - datatype(str)
                        The global ID of the remote issue link.

        :request POST: Create or update remote link.
        :body param: globalId - datatype(str)
                        The global ID of the remote issue link.
                     application - datatype(dict)
                     Details of the remote application the
                     linked item is in. For example, trello.
                     relationship - datatype(str)
                     Description of the relationship between
                     the issue and the linked item.
                     object - datatype(dict)
                     Details of the item linked to.

        :request DELETE: Deletes the remote issue link
                from the issue using the link's global ID.


        :param link_id: The ID of the remote issue link.

        :request PUT: Updates a remote issue link for an issue.

        :return: A string construct of the url
        """
        if link_id is None:
            return "{}/rest/api/{}/issue/{}/remotelink".format(
                LOGIN.base_url,
                "3" if LOGIN.api is True else "latest",
                key_or_id,
            )
        else:
            return "{}/rest/api/{}/issue/{}/remotelink/{}".format(
                LOGIN.base_url,
                "3" if LOGIN.api is True else "latest",
                key_or_id,
                link_id,
            )

    @classmethod
    def issue_link(cls, link_id: Optional[str] = None) -> str:
        """
        Use this operation to indicate a relationship between two
        issues and optionally add a comment to the (outward) issue.

        :request GET: Returns an issue link.

        :request POST: Creates a link between two issues.
                       link_id required.

        :request DELETE: Deletes an issue link. link_id required.

        :param link_id: The ID of the issue link.

        :return: str
        """
        if link_id:
            return "{}/rest/api/{}/issueLink/{}".format(
                LOGIN.base_url, "3" if LOGIN.api is True else "latest", link_id
            )
        else:
            return "{}/rest/api/{}/issueLink".format(
                LOGIN.base_url, "3" if LOGIN.api is True else "latest"
            )

    @classmethod
    def issue_link_types(
        cls,
        link_type_id: Optional[str] = None,
    ) -> str:
        """
        Returns a list of all issue link types.

        :request GET: To use this operation, the site must
                      have issue linking enabled.

        :request GET: Get issue link types, this requires the
                      linked type id.

        :request POST: Creates an issue link type. Use this
                       operation to create descriptions of the reasons
                       why issues are linked.

           :body param:
               * id - Datatype (str)
               * inward - Datatype (str)
               * name - Datatype (str)
               * outward - Datatype (str)
               * self - Datatype (str)

           Example::

               payload = {
                       "inward": "Duplicated by",
                       "name": "Duplicate",
                       "outward": "Duplicates"
                        }

        :request DELETE: Deletes an issue link type.
                         This requires the linked type id

        :request PUT: Updates an issue link type.
                      This requires the linked type id

             :body param:
               * id - Datatype (str)
               * inward - Datatype (str)
               * name - Datatype (str)
               * outward - Datatype (str)
               * self - Datatype (str)

           Example::

               payload = {
                       "inward": "Duplicated by",
                       "name": "Duplicate",
                       "outward": "Duplicates"
                        }

        :param link_type_id: The link type id

        :return:
        """
        if link_type_id:
            return "{}/rest/api/{}/issueLinkType/{}".format(
                LOGIN.base_url,
                "3" if LOGIN.api is True else "latest",
                link_type_id,
            )
        else:
            return "{}/rest/api/{}/issueLinkType".format(
                LOGIN.base_url, "3" if LOGIN.api is True else "latest"
            )

    @classmethod
    def work_logs(
        cls,
        key_or_id: Union[str, int] = None,
        start_at: int = 0,
        max_results: int = 1048576,
        **kwargs: Any,
    ) -> str:
        """Returns worklogs for an issue, starting from
        the oldest worklog or from the worklog started on or
        after a date and time.

        :request GET: Returns worklogs for an issue

        :request GET: Returns a worklog. When a worklog_id is specified

        :param key_or_id: The ID or key of the issue.


        :param start_at: The index of the first item to
                        return in a page of results (page offset).


        :param max_results: The maximum number of items to
                            return per page.


        :param kwargs: Additional keyword

                       **Acceptable options**

                       - started_after: The worklog start date and time, as a
                                        UNIX timestamp in milliseconds, after
                                        which worklogs are returned.

                       - started_before: The worklog start date and time, as a
                                         UNIX timestamp in milliseconds, before
                                         which worklogs are returned.

                       - worklog_id: The ID of the worklog.

                       - expand: Use expand to include additional information
                                 about worklogs in the response.

                       - notify_users: Whether users watching the issue are
                                       notified by email.

                       - adjust_estimate: Defines how to update the issue's
                                          time estimate, the options are
                                          ``new``  Sets the estimate to a
                                          specific value, defined in newEstimate.
                                          ``leave`` Leaves the estimate
                                          unchanged. ``auto`` Updates the
                                          estimate by the difference between the
                                          original and updated value of
                                          timeSpent or timeSpentSeconds.
                                          Valid values: new, leave, manual, auto

                       - new_estimate: The value to set as the issue's remaining
                                       time estimate, as days (#d),  hours (#h),
                                       or minutes (#m or #).
                                       For example, 2d. Required when
                                       adjustEstimate is new.

                       - override_editable_flag: Whether the worklog should be
                                                 added to the issue even if the
                                                 issue is not editable.

                       - increase_by: The amount to increase the issue's
                                      remaining estimate by, as days (#d),
                                      hours (#h), or minutes (#m or #).
                                       For example, 2d.

                       - reduce_by: The amount to reduce the issue's remaining
                                    estimate by, as days (#d), hours (#h),
                                    or minutes (#m).
                                    For example, 2d.

                       - since: The date and time, as a UNIX timestamp in
                                milliseconds, after which updated worklogs
                                are returned.




        :request POST: Adds a worklog to an issue. Other query parameters
                       can be specified such as ``adjust_estimate`` argument.

        :request PUT: Updates a worklog. When a worklog_id is specified

        :request DELETE: Deletes a worklog from an issue. When a worklog_id
                        is specified. Other query parameters
                        can be specified such as ``adjust_estimate`` argument.

        :return: str

        """
        started_after: int = (
            kwargs.get("started_after") if "started_after" in kwargs else None
        )
        started_before: int = (
            kwargs.get("started_before") if "started_before" in kwargs else None
        )
        worklog_id: Optional[str] = (
            kwargs.get("worklog_id") if "worklog_id" in kwargs else None
        )
        expand: Optional[str] = kwargs.get("expand") if "expand" in kwargs else None
        notify_users: Optional[bool] = kwargs.get("notify_users", True)
        adjust_estimate: Optional[str] = kwargs.get("adjust_estimate", "auto")
        new_estimate: Optional[str] = (
            kwargs.get("new_estimate") if "new_estimate" in kwargs else None
        )
        increase_by: Optional[str] = (
            kwargs.get("increase_by") if "increase_by" in kwargs else None
        )
        override_editable_flag: Optional[bool] = kwargs.get(
            "override_editable_flag", False
        )
        reduce_by: Optional[str] = (
            kwargs.get("reduce_by") if "reduce_by" in kwargs else None
        )
        since: Optional[int] = kwargs.get("since") if "since" in kwargs else None

        if key_or_id is not None and worklog_id is None:
            if started_after is not None and started_before is None:
                if expand is None:
                    return (
                        "{}/rest/api/{}/issue/{}/worklog?startAt={}"
                        "&maxResults={}"
                        "&startedAfter={}".format(
                            LOGIN.base_url,
                            "3" if LOGIN.api is True else "latest",
                            key_or_id,
                            start_at,
                            max_results,
                            started_after,
                        )
                    )
                else:
                    return (
                        "{}/rest/api/{}/issue/{}/worklog?startAt={}"
                        "&maxResults={}&expand={}"
                        "&startedAfter={}".format(
                            LOGIN.base_url,
                            "3" if LOGIN.api is True else "latest",
                            key_or_id,
                            start_at,
                            max_results,
                            expand,
                            started_after,
                        )
                    )
            elif started_after is None and started_before is not None:
                if expand is None:
                    return (
                        "{}/rest/api/{}/issue/{}/worklog?startAt={}"
                        "&maxResults={}"
                        "&startedBefore={}".format(
                            LOGIN.base_url,
                            "3" if LOGIN.api is True else "latest",
                            key_or_id,
                            start_at,
                            max_results,
                            started_before,
                        )
                    )
                else:
                    return (
                        "{}/rest/api/{}/issue/{}/worklog?startAt={}"
                        "&maxResults={}&expand={}"
                        "&startedBefore={}".format(
                            LOGIN.base_url,
                            "3" if LOGIN.api is True else "latest",
                            key_or_id,
                            start_at,
                            max_results,
                            expand,
                            started_before,
                        )
                    )
            elif started_after is not None and started_before is not None:
                if expand is None:
                    return (
                        "{}/rest/api/{}/issue/{}/worklog?startAt={}"
                        "&maxResults={}"
                        "&startedBefore={}&startedAfter={}".format(
                            LOGIN.base_url,
                            "3" if LOGIN.api is True else "latest",
                            key_or_id,
                            start_at,
                            max_results,
                            started_before,
                            started_after,
                        )
                    )
                else:
                    return (
                        "{}/rest/api/{}/issue/{}/worklog?startAt={}"
                        "&maxResults={}&expand={}"
                        "&startedBefore={}&startedAfter={}".format(
                            LOGIN.base_url,
                            "3" if LOGIN.api is True else "latest",
                            key_or_id,
                            start_at,
                            max_results,
                            expand,
                            started_before,
                            started_after,
                        )
                    )
            else:
                if expand is not None:
                    return (
                        "{}/rest/api/{}/issue/{}/worklog?startAt={}"
                        "&maxResults={}&expand={}".format(
                            LOGIN.base_url,
                            "3" if LOGIN.api is True else "latest",
                            key_or_id,
                            start_at,
                            max_results,
                            expand,
                        )
                    )
                elif expand is None:
                    return (
                        "{}/rest/api/{}/issue/{}/worklog?startAt={}"
                        "&maxResults={}".format(
                            LOGIN.base_url,
                            "3" if LOGIN.api is True else "latest",
                            key_or_id,
                            start_at,
                            max_results,
                        )
                    )
                else:
                    if adjust_estimate is not None:
                        if adjust_estimate == "new":
                            return (
                                "{}/rest/api/{}/issue/{}/worklog?"
                                "&adjustEstimate={}"
                                "&newEstimate={}"
                                "&notifyUsers={}"
                                "&overrideEditableFlag={}".format(
                                    LOGIN.base_url,
                                    "3" if LOGIN.api is True else "latest",
                                    key_or_id,
                                    adjust_estimate,
                                    new_estimate,
                                    notify_users,
                                    override_editable_flag,
                                )
                            )
                        elif adjust_estimate == "manual":
                            return (
                                "{}/rest/api/{}/issue/{}/worklog?"
                                "&adjustEstimate={}"
                                "&reduceBy={}"
                                "&notifyUsers={}"
                                "&overrideEditableFlag={}".format(
                                    LOGIN.base_url,
                                    "3" if LOGIN.api is True else "latest",
                                    key_or_id,
                                    adjust_estimate,
                                    reduce_by,
                                    notify_users,
                                    override_editable_flag,
                                )
                            )
                        else:
                            return (
                                "{}/rest/api/{}/issue/{}/worklog?"
                                "&adjustEstimate={}"
                                "&notifyUsers={}"
                                "&overrideEditableFlag={}".format(
                                    LOGIN.base_url,
                                    "3" if LOGIN.api is True else "latest",
                                    key_or_id,
                                    adjust_estimate,
                                    notify_users,
                                    override_editable_flag,
                                )
                            )

        elif key_or_id is not None and worklog_id is not None:
            if expand is None:
                return "{}/rest/api/{}/issue/{}/worklog/{}".format(
                    LOGIN.base_url,
                    "3" if LOGIN.api is True else "latest",
                    key_or_id,
                    worklog_id,
                )
            elif expand is not None:
                return "{}/rest/api/{}/issue/{}/worklog/{}?expand={}".format(
                    LOGIN.base_url,
                    "3" if LOGIN.api is True else "latest",
                    key_or_id,
                    worklog_id,
                    expand,
                )
            elif adjust_estimate is not None:
                if adjust_estimate == "new":
                    return (
                        "{}/rest/api/{}/issue/{}/worklog/{}?"
                        "adjustEstimate={}&newEstimate={}"
                        "&notifyUsers={}&overrideEditableFlag={}".format(
                            LOGIN.base_url,
                            "3" if LOGIN.api is True else "latest",
                            key_or_id,
                            worklog_id,
                            adjust_estimate,
                            new_estimate,
                            notify_users,
                            override_editable_flag,
                        )
                    )
                elif adjust_estimate == "manual":
                    return (
                        "{}/rest/api/{}/issue/{}/worklog/{}?"
                        "adjustEstimate={}&increaseBy={}"
                        "&notifyUsers={}&overrideEditableFlag={}".format(
                            LOGIN.base_url,
                            "3" if LOGIN.api is True else "latest",
                            key_or_id,
                            worklog_id,
                            adjust_estimate,
                            increase_by,
                            notify_users,
                            override_editable_flag,
                        )
                    )

        else:
            if since is not None and expand is not None:
                return "{}/rest/api/{}/worklog/updated?" "expand={}&since={}".format(
                    LOGIN.base_url,
                    "3" if LOGIN.api is True else "latest",
                    expand,
                    since,
                )
            elif since is not None and expand is None:
                return "{}/rest/api/{}/worklog/deleted?since={}".format(
                    LOGIN.base_url,
                    "3" if LOGIN.api is True else "latest",
                    since,
                )
            elif since is None and expand is not None:
                return "{}/rest/api/{}/worklog/list?expand={}".format(
                    LOGIN.base_url,
                    "3" if LOGIN.api is True else "latest",
                    expand,
                )
            else:
                raise JiraOneErrors(
                    "value",
                    "At least one argument " "should be passed" " with this method.",
                )

    @classmethod
    def webhooks(cls, uri: Optional[str] = None) -> str:
        """Makes a call to the webhook API.
        Only connect app or OAuth 2.0 can use this connection.

        :request GET: Returns a paginated list of the webhooks
                      registered by the calling app.

        :request POST: Registers webhooks.

        :request DELETE: Removes webhooks by ID.
            :body param: webhookIds - required List[int]

        :param uri: Url path context

                  *options available*

                  * ``failed`` - Returns webhooks that have recently
                                failed
                  * ``refresh`` - Extends the life of webhook.

        :request GET: After 72 hours the failure may no longer be
                      returned by this operation.

        :request PUT: Webhooks registered through the REST
                      API expire after 30 days

        :return: str
        """
        if uri:
            return "{}/rest/api/{}/webhook/{}".format(
                LOGIN.base_url, "3" if LOGIN.api is True else "latest", uri
            )
        else:
            return "{}/rest/api/{}/webhook".format(
                LOGIN.base_url, "3" if LOGIN.api is True else "latest"
            )

    @classmethod
    def task(cls, task_id: Optional[str] = None, method: Optional[str] = "GET") -> str:
        """When a task has finished, this operation
        returns the JSON blob applicable to the task

        :request GET: Returns the status of a long-running
                      asynchronous task.

        :request POST: Cancels a task.

        :param task_id: The ID of the task.

        :param method: An HTTP request type

        :return: str
        """
        if method.lower() == "get":
            return "{}/rest/api/{}/task/{}".format(
                LOGIN.base_url,
                "3" if LOGIN.api is True else "latest",
                task_id,
            )
        else:
            return "{}/rest/api/{}/task/{}/cancel".format(
                LOGIN.base_url,
                "3" if LOGIN.api is True else "latest",
                task_id,
            )

    @classmethod
    def issue_watchers(
        cls, key_or_id: Union[str, int] = None, account_id: Optional[str] = None
    ) -> str:
        """This operation requires the Allow users
        to watch issues option to be ON.

        :request GET: Returns the watchers for an issue.

        :request POST: Adds a user as a watcher of an issue
                       by passing the account ID of the user.

        :request DELETE: Deletes a user as a watcher of an issue.


        :param key_or_id: The ID or key of the issue.

        :request POST: Returns, for the user, details of the
                       watched status of issues from a list.

            :body param: issueIds - List[int]


        :param account_id: The account ID of the user

        :return: str
        """
        if key_or_id:
            if account_id:
                return "{}/rest/api/{}/issue/{}/watchers?accountId={}".format(
                    LOGIN.base_url,
                    "3" if LOGIN.api is True else "latest",
                    key_or_id,
                    account_id,
                )
            else:
                return "{}/rest/api/{}/issue/{}/watchers".format(
                    LOGIN.base_url,
                    "3" if LOGIN.api is True else "latest",
                    key_or_id,
                )
        else:
            return "{}/rest/api/{}/issue/watching".format(
                LOGIN.base_url, "3" if LOGIN.api is True else "latest"
            )

    @classmethod
    def issue_votes(cls, key_or_id: Union[str, int] = None) -> str:
        """Return the  number of votes on an issue

        :request GET: Returns details about the votes on an issue.

        :request POST: Adds the user's vote to an issue.

        :request DELETE: Deletes a user's vote from an issue.

        :param key_or_id: The ID or key of the issue.

        :return: str
        """
        return "{}/rest/api/{}/issue/{}/votes".format(
            LOGIN.base_url,
            "3" if LOGIN.api is True else "latest",
            key_or_id,
        )

    @classmethod
    def instance_info(cls):
        """Returns licensing information about the Jira instance."""
        return "{}/rest/api/{}/instance/license".format(
            LOGIN.base_url, "3" if LOGIN.api is True else "latest"
        )

    @classmethod
    def worklog_properties(
        cls,
        key_or_id: Union[str, int] = None,
        worklog_id: Optional[str] = None,
        property_key: Optional[str] = None,
    ) -> str:
        """
        Returns the worklog properties of an issue

        :request GET: Returns the keys of all properties for a worklog.

        :param key_or_id: The ID or key of the issue.

        :param worklog_id: The ID of the worklog.

        :request GET: Returns the value of a worklog property.

        :request PUT: Sets the value of a worklog property.

                :body param: The request body can contain any
                             valid application/json.

        :request DELETE: Deletes a worklog property.

        :param property_key: The key of the property.

        :return: str
        """
        if property_key is None:
            return "{}/rest/api/{}/issue/{}/worklog/{}/properties".format(
                LOGIN.base_url,
                "3" if LOGIN.api is True else "latest",
                key_or_id,
                worklog_id,
            )
        else:
            return "{}/rest/api/{}/issue/{}/worklog/{}/properties/{}".format(
                LOGIN.base_url,
                "3" if LOGIN.api is True else "latest",
                key_or_id,
                worklog_id,
                property_key,
            )

    @classmethod
    def server_info(cls) -> str:
        """
        Returns information about the Jira instance.
        This operation can be accessed anonymously.

        :return: strings
        """
        return "{}/rest/api/{}/serverInfo".format(
            LOGIN.base_url, "3" if LOGIN.api is True else "latest"
        )

    @classmethod
    def project_avatar(
        cls,
        key_or_id: Union[str, int] = None,
        avatar_id: Optional[str] = None,
        method: Optional[str] = "get",
        **kwargs,
    ) -> str:
        """
        Performs multiple operations to the avatar displayed for a project.

        :Request PUT: Set the avatar to a project, the project key or id
                      is required and the avatar_id needs to be passed
                      in the body

        Example 1::

          payload = {"id": "10010"}

        :Request DELETE: Deletes a custom avatar from a project.
                         Note that system avatars cannot be deleted.

        :Request POST: Loads an avatar for a project.
                      Specify the avatar's local file location
                      in the body of the request

        Example 2::

          X-Atlassian-Token: no-check
          Content-Type: image/image type Valid image types are JPEG, GIF, or PNG.

        :Request GET: Returns all project avatars, grouped by
                      system and custom avatars.

        :param key_or_id: Required project key or id

        :param avatar_id: Required Avatar id if method argument is a
                          DELETE or PUT request

        :param method: Define an HTTP method of operation
                       options: get, put, post, delete

        :param kwargs: Additional query parameters. The below
                       variables all are in integers

                    - cord_x: The X coordinate of the top-left corner of the
                              crop region.

                    - cord_y: The Y coordinate of the top-left corner of the
                              crop region.

                    - size: The length of each side of the crop region.
                             e.g. 16, 24, 32, and 48

                             The cropped image is then used to create avatars
                             of 16x16, 4x24, 32x32, and 48x48 in size.

        :return: string
        """
        if method.lower() == "get":
            return "{}/rest/api/{}/project/{}/avatars".format(
                LOGIN.base_url,
                "3" if LOGIN.api is True else "latest",
                key_or_id,
            )
        elif method.lower() == "post":
            if "size" not in kwargs:
                raise JiraOneErrors(
                    "value", "size keyword argument is required but missing."
                )
            for key, value in kwargs.items():
                if not isinstance(value, int):
                    raise JiraOneErrors(
                        "value", f"{key} keyword argument is not a number."
                    )
            if "cord_x" in kwargs and "size" in kwargs and "cord_y" not in kwargs:
                return "{}/rest/api/{}/project/{}/avatar2?x={}&size={}".format(
                    LOGIN.base_url,
                    "3" if LOGIN.api is True else "latest",
                    key_or_id,
                    kwargs.get("cord_x"),
                    kwargs.get("size"),
                )
            elif "cord_y" in kwargs and "size" in kwargs and "cord_x" not in kwargs:
                return "{}/rest/api/{}/project/{}/avatar2?y={}&size={}".format(
                    LOGIN.base_url,
                    "3" if LOGIN.api is True else "latest",
                    key_or_id,
                    kwargs.get("cord_y"),
                    kwargs.get("size"),
                )
            elif "cord_x" in kwargs and "cord_y" in kwargs and "size" in kwargs:
                return "{}/rest/api/{}/project/{}/avatar2?x={}&y={}&size={}".format(
                    LOGIN.base_url,
                    "3" if LOGIN.api is True else "latest",
                    key_or_id,
                    kwargs.get("cord_x"),
                    kwargs.get("cord_y"),
                    kwargs.get("size"),
                )
            else:
                raise JiraOneErrors(
                    "value", "Either cord_x or cord_y argument must be provided"
                )
        elif method.lower() == "delete":
            return "{}/rest/api/{}/project/{}/avatar/{}".format(
                LOGIN.base_url,
                "3" if LOGIN.api is True else "latest",
                key_or_id,
                avatar_id,
            )
        elif method.lower() == "put":
            return "{}/rest/api/{}/project/{}/avatar".format(
                LOGIN.base_url,
                "3" if LOGIN.api is True else "latest",
                key_or_id,
            )
        else:
            raise JiraOneErrors("wrong", "No such method exist within this operation")

    ################################################
    # Jira Software Specifics API endpoints
    ################################################
    # BACKLOG -> API for backlog
    @classmethod
    def move_issues_to_backlog(cls) -> str:
        """Move issues to the backlog. This operation is equivalent to
        remove future and active sprints from a given set of issues.
        At most 50 issues may be moved at once.

        :request POST:

        :body param: issues, datatype -> Array<string>

        Send a POST request within API.

        :return: A string of the url
        """
        return "{}/rest/agile/1.0/backlog/issue".format(LOGIN.base_url)

    @classmethod
    def move_issues_to_backlog_from_board(cls, board_id: int) -> str:
        """Move issues to the backlog of a particular board
        (if they are already on that board).

        This operation is equivalent to remove future and active sprints
        from a given set of issues if the board has sprints If the board
        does not have sprints this will put the issues back into the backlog
        from the board. At most 50 issues may be moved at once.

        :request POST:

        :param board_id: required

        :body param: issues, datatype -> Array<string>,

                    rankBeforeIssue, rankAfterIssue, type -> string

                    rankCustomFieldId, type -> integer

        :return: A string of the url
        """
        return "{}/rest/agile/1.0/backlog/{}/issue".format(LOGIN.base_url, board_id)

    # BOARD -> API for Boards

    @classmethod
    def create_board(cls) -> str:
        """Creates a new board. Board name, type and filter ID is required.

        :request GET: returns a list of boards on the instance
                      that's accessible by you.

        :request POST:

        :body param: name, type, datatype -> string

                    filterId, datatype -> integer

                    location, datatype -> object

        :return: A string of the url
        """
        return "{}/rest/agile/1.0/board".format(LOGIN.base_url)

    @classmethod
    def get_board_by_filter_id(
        cls, filter_id: int, start_at: int = 0, max_results: int = 50
    ) -> str:
        """Returns any boards which use the provided filter id.

        This method can be executed by users without a valid software license
        in order to find which boards are using a particular filter.

        :param filter_id:  required - Filters results to boards that are
                        relevant to a filter. Not supported for
                        the team-managed project boards.

        :param start_at: defaults to 0

        :param max_results: defaults to 50

        :return: A string of the url
        """
        return "{}/rest/agile/1.0/board/filter/{}?startAt={}&maxResults={}".format(
            LOGIN.base_url, filter_id, start_at, max_results
        )

    @classmethod
    def get_board(cls, board_id: int) -> str:
        """Returns the board for the given board ID.

        This board will only be returned if the user has permission to view it.
        Admins without the view permission will see the board as a private one,
        so will see only a subset of the board's data
        (board location for instance).

        :param board_id: A board id

        :return: A string of the url
        """
        return "{}/rest/agile/1.0/board/{}".format(LOGIN.base_url, board_id)

    @classmethod
    def get_issues_on_backlog(
        cls,
        board_id: int,
        query: str = None,
        start_at: int = 0,
        max_results: int = 50,
    ) -> str:
        """Returns all issues from the board's backlog, for the given board ID.

        This only includes issues that the user has permission to view.
        The backlog contains incomplete issues that are not assigned
        to any future or active sprint.

        :param board_id: required

        :param start_at: defaults to 0,

        :param max_results: defaults to 50

        :param query: -> includes other query parameters such as

                            Query           Datatypes
                        ----------------------------
                         jql           | string
                         validateQuery | boolean
                         fields        | Array<string>
                         expand        | string


        :return: A string of the url
        """
        if query is not None:
            return (
                "{}/rest/agile/1.0/board/{}/backlog?{}&startAt={}&maxResults={}".format(
                    LOGIN.base_url, board_id, query, start_at, max_results
                )
            )
        else:
            return "{}/rest/agile/1.0/board/{}/backlog?startAt={}&maxResults={}".format(
                LOGIN.base_url, board_id, start_at, max_results
            )

    @classmethod
    def get_issues_on_board(
        cls,
        board_id: int,
        query: str = None,
        start_at: int = 0,
        max_results: int = 50,
    ) -> str:
        """Returns all issues from a board, for a given board ID.

        This only includes issues that the user has permission to view.
        An issue belongs to the board if its status is mapped to the
        board's column.

        :param board_id: required

        :param start_at: defaults to 0,

        :param max_results: defaults to 50

        :param query: -> includes other query parameters such as

                         Query           Datatypes
                        ----------------------------
                         jql           | string
                         validateQuery | boolean
                         fields        | Array<string>
                         expand        | string

        :return: A string of the url
        """
        if query is not None:
            return (
                "{}/rest/agile/1.0/board/{}/issue?{}&startAt={}&maxResults={}".format(
                    LOGIN.base_url, board_id, query, start_at, max_results
                )
            )
        else:
            return "{}/rest/agile/1.0/board/{}/issue?startAt={}&maxResults={}".format(
                LOGIN.base_url, board_id, start_at, max_results
            )

    @classmethod
    def move_issues_to_board(cls, board_id: int) -> str:
        """Move issues from the backog to the board (if they are already
        in the backlog of that board).

        This operation either moves an issue(s) onto a board from the
        backlog (by adding it to the issueList
        for the board) Or transitions the issue(s) to the first column
        for a kanban board with backlog.

        :request POST:

        :param board_id: required

        :body param: rankBeforeIssue, rankAfterIssue, datatype -> string
                   : rankCustomFieldId, datatype -> integer
                   : issues, datatype -> Array<string>

        :return: A string of the url
        """
        return "{}/rest/agile/1.0/board/{}/issue".format(LOGIN.base_url, board_id)

    @classmethod
    def get_projects_on_board(
        cls, board_id: int, start_at: int = 0, max_results: int = 50
    ) -> str:
        """Returns all projects that are associated with the board,
        for the given board ID.

        If the user does not have permission to view the board,
        no projects will be returned at all.
        Returned projects are ordered by the name.

        :param board_id: required

        :param start_at: defaults 0

        :param max_results: defaults 50

        :return: A string of the url
        """
        return "{}/rest/agile/1.0/board/{}/project?startAt={}&maxResults={}".format(
            LOGIN.base_url, board_id, start_at, max_results
        )

    @classmethod
    def get_all_quick_filters(
        cls, board_id: int, start_at: int = 0, max_results: int = 50
    ) -> str:
        """Returns all quick filters from a board, for a given board ID.

        :param board_id: required

        :param start_at: defaults 0

        :param max_results: defaults 50

        :return: A string of the url
        """
        return "{}/rest/agile/1.0/board/{}/quickfilter?startAt={}&maxResults={}".format(
            LOGIN.base_url, board_id, start_at, max_results
        )

    @classmethod
    def get_quick_filter(cls, board_id: int, quick_filter_id: int) -> str:
        """Returns the quick filter for a given quick filter ID.

        The quick filter will only be returned if the user can view the board that the
        quick filter belongs to.

        :param board_id: required,

        :param quick_filter_id: required

        :return: A string of the url
        """
        return "{}/rest/agile/1.0/board/{}/quickfilter/{}".format(
            LOGIN.base_url, board_id, quick_filter_id
        )

    @classmethod
    def get_all_sprints(
        cls,
        board_id: int,
        query: str = None,
        start_at: int = 0,
        max_results: int = 50,
    ) -> str:
        """Get all Sprint on a Board.

        :param board_id: A board id

        :param start_at: defaults to 0

        :param max_results: defaults to 50

        :param query: A search term. Valid values e.g. future, active, or closed
                      Multiple can be separated by comma e.g. active,closed


        :return: A string of the url
        """
        if query is not None:
            return "{}/rest/agile/1.0/board/{}/sprint?state={}&startAt={}&maxResults={}".format(
                LOGIN.base_url, board_id, query, start_at, max_results
            )
        else:
            return "{}/rest/agile/1.0/board/{}/sprint?startAt={}&maxResults={}".format(
                LOGIN.base_url, board_id, start_at, max_results
            )

    # SPRINT -> API for Sprints
    @classmethod
    def create_sprint(cls) -> str:
        """Creates a future sprint. Sprint name and origin board id
        are required. Start date, end date, and goal are optional.

        :request POST:

        :body param: name, startDate, endDate, goal, datatype -> string
                   : originBoardId, datatype -> integer

        :return: A string of the url
        """
        return "{}/rest/agile/1.0/sprint".format(LOGIN.base_url)

    @classmethod
    def get_sprint(cls, sprint_id: int) -> str:
        """Returns the sprint for a given sprint ID.

        The sprint will only be returned if the user can view the board that
        the sprint was created on, or view at least one of the
        issues in the sprint.

        :param sprint_id:  required

        :return: A string of the url
        """
        return "{}/rest/agile/1.0/sprint/{}".format(LOGIN.base_url, sprint_id)

    @classmethod
    def update_sprint(cls, sprint_id: int) -> str:
        """Performs a full update of a sprint.

        A full update means that the result will be exactly the same
        as the request body. Any fields not present in the request
        JSON will be set to null.

        :request PUT:

        :param sprint_id: required

        :body param: name, state, startDate, endDate, goal, self (format: uri),
                     completeDate, datatype -> string
                   : id, originBoardId, datatype -> integer

        :return: A string of the url
        """
        return "{}/rest/agile/1.0/sprint/{}".format(LOGIN.base_url, sprint_id)

    @classmethod
    def delete_sprint(cls, sprint_id: int) -> str:
        """Deletes a sprint.

        Once a sprint is deleted, all open issues in the sprint will be
        moved to the backlog.

        :request DELETE:

        :param sprint_id: required

        :return: A string of the url
        """
        return "{}/rest/agile/1.0/sprint/{}".format(LOGIN.base_url, sprint_id)

    ################################################
    # Jira Service Management Specific API endpoints
    ################################################
    @classmethod
    def create_customer(cls) -> str:
        """This method adds a customer to the Jira Service Management.

        instance by passing a JSON file including an email address
        and display name.

        :request POST:

        :body param: email, displayName, datatype -> string

        :return: A string of the url
        """
        return "{}/rest/servicedeskapi/customer".format(LOGIN.base_url)

    @classmethod
    def get_server_info(cls) -> str:
        """This method retrieves information about the Jira Service Management.

        instance such as software version, builds, and related links.

        :return: A string of the url
        """
        return "{}/rest/servicedeskapi/info".format(LOGIN.base_url)

    @classmethod
    def get_organizations(
        cls, start: int = 0, limit: int = 50, account_id: str = None
    ) -> str:
        """This method returns a list of organizations in the
        Jira Service Management instance. Use this method when you want to
        present a list of organizations or want to locate
        an organization by name.

        :param start: defaults to 0

        :param limit: defaults to 50

        :param account_id: datatype string. e.g. 5b10ac8d82e05b22cc7d4ef5

        :return: A string of the url
        """
        if account_id is not None:
            return "{}/rest/servicedeskapi/organization?accountId={}&start={}&limit={}".format(
                LOGIN.base_url, account_id, start, limit
            )
        else:
            return "{}/rest/servicedeskapi/organization?start={}&limit={}".format(
                LOGIN.base_url, start, limit
            )

    @classmethod
    def create_organization(cls) -> str:
        """This method creates an organization by passing the name
        of the organization.

        :request POST:

        :body param: name, datatype -> string

        :return: A string of the url
        """
        return "{}/rest/servicedeskapi/organization".format(LOGIN.base_url)

    @classmethod
    def get_organization(cls, org_id: int) -> str:
        """This method returns details of an organization.

        Use this method to get organization details whenever your
        application component is passed an organization ID
        but needs to display other organization details.

        :param org_id: required

        :return: A string of the url
        """
        return "{}/rest/servicedeskapi/organization/{}".format(LOGIN.base_url, org_id)

    @classmethod
    def get_service_desks(cls, start: int = 0, limit: int = 100) -> str:
        """This method returns all the service desks in the
        Jira Service Management instance that the user has permission to access.
        Use this method where you need a list of service desks
        or need to locate a service desk by name or keyword.

        :param start: integer - pagination row

        :param limit: integer - limit to each pagination


        :return: string
        """
        return "{}/rest/servicedeskapi/servicedesk?start={}&limit={}".format(
            LOGIN.base_url, start, limit
        )

    @classmethod
    def get_sd_by_id(cls, service_desk_id: int) -> str:
        """
        This method returns a service desk. Use this method to get
        service desk details whenever your application component is passed
        a service desk ID but needs to display other service desk details.

        :param service_desk_id: The ID of the service desk to return. Required

        :return: string
        """
        return "{}/rest/servicedeskapi/servicedesk/{}".format(
            LOGIN.base_url, service_desk_id
        )

    @classmethod
    def delete_organization(cls, org_id: int) -> str:
        """This method deletes an organization.

        Note that the organization is deleted regardless of other
        associations it may have.
        For example, associations with service desks.

        :request DELETE:

        :param org_id: required

        :return: A string of the url
        """
        return "{}/rest/servicedeskapi/organization/{}".format(LOGIN.base_url, org_id)

    @classmethod
    def get_users_in_organization(
        cls, org_id: int, start: int = 0, limit: int = 50
    ) -> str:
        """This method returns all the users associated with an organization.

        Use this method where you want to provide a list of users
        for an organization
        or determine if a user is associated with an organization.

        :param org_id: required

        :param start: datatype integer

        :param limit: datatype integer

        :return: A string of the url
        """
        return "{}/rest/servicedeskapi/organization/{}/user?start={}&limit={}".format(
            LOGIN.base_url, org_id, start, limit
        )

    @classmethod
    def add_users_to_organization(cls, org_id: int) -> str:
        """This method adds users to an organization.

        :request POST:

        :param org_id: required

        :body param: usernames, accountIds, datatypes -> Array<string>

        :return: A string of the url
        """
        return "{}/rest/servicedeskapi/organization/{}/user".format(
            LOGIN.base_url, org_id
        )

    @classmethod
    def remove_users_from_organization(cls, org_id: int) -> str:
        """This method removes users from an organization.

        :request DELETE:

        :param org_id: required

        :body param: usernames, accountIds, datatypes -> Array<string>

        :return: A string of the url
        """
        return "{}/rest/servicedeskapi/organization/{}/user".format(
            LOGIN.base_url, org_id
        )

    @classmethod
    def get_sd_organizations(
        cls,
        service_desk_id: int,
        start: int = 0,
        limit: int = 50,
        account_id: str = None,
    ) -> str:
        """This method returns a list of all organizations associated
        with a service desk.

        :param service_desk_id: required

        :param start: defaults to 0

        :param limit: defaults to 50

        :param account_id: datatype string. e.g. 5b10ac8d82e05b22cc7d4ef5

        :return: A string of the url
        """
        if account_id is not None:
            return "{}/rest/servicedeskapi/servicedesk/{}/organization?accountId={}&start={}&limit={}".format(
                LOGIN.base_url, service_desk_id, account_id, start, limit
            )
        else:
            return "{}/rest/servicedeskapi/servicedesk/{}/organization?start={}&limit={}".format(
                LOGIN.base_url, service_desk_id, start, limit
            )

    @classmethod
    def add_sd_organization(cls, service_desk_id: int) -> str:
        """This method adds an organization to a service desk.

        If the organization ID is already associated with the service desk,
        no change is made and the resource returns a 204 success code.

        :request POST:

        :param service_desk_id: required

        :body param: organizationId, datatype -> integer

        :return: A string of the url
        """
        return "{}/rest/servicedeskapi/servicedesk/{}/organization".format(
            LOGIN.base_url, service_desk_id
        )

    @classmethod
    def remove_sd_organization(cls, service_desk_id: int) -> str:
        """This method removes an organization from a service desk.

        If the organization ID does not match an organization associated
        with the service desk, no change is made and the resource
        returns a 204 success code.

        :request DELETE:

        :param service_desk_id: required

        :body param: organizationId, datatype -> integer

        :return: A string of the url
        """
        return "{}/rest/servicedeskapi/servicedesk/{}/organization".format(
            LOGIN.base_url, service_desk_id
        )

    @classmethod
    def get_customers(
        cls,
        service_desk_id: int,
        start: int = 0,
        limit: int = 50,
        query: str = None,
    ) -> str:
        """This method returns a list of the customers on a service desk.

        The returned list of customers can be filtered using the query parameter.
        The parameter is matched against customers' displayName, name, or email.
        This API is experimental

        :param service_desk_id: required

        :param start: defaults to 0

        :param limit: defaults to 50

        :param query: datatype string.

        :return: A string of the url
        """
        if query is not None:
            return "{}/rest/servicedeskapi/servicedesk/{}/customer?{}&start={}&limit={}".format(
                LOGIN.base_url, query, service_desk_id, start, limit
            )
        else:
            return "{}/rest/servicedeskapi/servicedesk/{}/customer?start={}&limit={}".format(
                LOGIN.base_url, service_desk_id, start, limit
            )

    @classmethod
    def add_customers(cls, service_desk_id: int) -> str:
        """Adds one or more customers to a service desk.

        If any of the passed customers are associated with the service desk,
        no changes will be made for those customers and the resource returns
        a 204 success code.

        :request POST:

        :param service_desk_id: required

        :body param: usernames, accountIds,  datatype -> Array<string>


        :return: A string of the url
        """
        return "{}/rest/servicedeskapi/servicedesk/{}/customer".format(
            LOGIN.base_url, service_desk_id
        )

    @classmethod
    def remove_customers(cls, service_desk_id: int) -> str:
        """This method removes one or more customers from a service desk.

        The service desk must have closed access. If any of the passed
        customers are not associated with the service desk, no changes
        will be made for those customers and the resource
        returns a 204 success code.

        :request DELETE:

        :param service_desk_id: required

        :body param: usernames, accountIds,  datatype -> Array<string>

        :return: A string of the url
        """
        return "{}/rest/servicedeskapi/servicedesk/{}/customer".format(
            LOGIN.base_url, service_desk_id
        )

    ################################################
    # Jira Specific API endpoints
    ################################################
    @classmethod
    def jira_user(cls, account_id: str = None) -> str:
        """API for User creation, deletion and retrieval.

        :request POST: - Creates a user. This resource is retained for
                         legacy compatibility. As soon as a more suitable
                         alternative is available this resource
                         will be deprecated

        :body param: key, name, password, emailAddress, displayName,
                     notification, datatypes -> string
                    : applicationKeys, datatype -> Array<string>
                    : Additional Properties, datatypes -> Any
                     returns 201 for successful creation

        :request DELETE: - Deletes a user.

        :body param: accountId, datatype -> string required
                          returns 204 for successful deletion

        :request GET: - Returns a user.

        :body param: accountId, expand, datatypes -> string

        :param account_id: - string for a user account

        :return: A string of the url
        """
        if account_id is not None:
            return "{}/rest/api/{}/user?accountId={}".format(
                LOGIN.base_url,
                "3" if LOGIN.api is True else "latest",
                account_id,
            )
        else:
            return "{}/rest/api/{}/user".format(
                LOGIN.base_url, "3" if LOGIN.api is True else "latest"
            )

    @classmethod
    def jira_group(cls, group_name: str = None, swap_group: str = None) -> str:
        """Used for Creation and deletion of Jira groups.

        :request  POST: - Creates a group.

         :body param: name required, datatype -> string
            returns 201 if successful

        :request DELETE: - Deletes a group.

         The group to transfer restrictions to. Only comments and
         worklogs are transferred. If restrictions are not transferred,
         comments and worklogs are inaccessible after the deletion.

         :query param: group_name required, swap_group,  datatype -> string
                       returns 200 if successful

        :param group_name: name of group

        :param swap_group: group name to swap

        :return: A string of the url
        """
        if group_name is not None and swap_group is None:
            return "{}/rest/api/{}/group?groupname={}".format(
                LOGIN.base_url,
                "3" if LOGIN.api is True else "latest",
                group_name,
            )
        elif group_name is not None and swap_group is not None:
            return "{}/rest/api/{}/group?groupname={}&swapGroup={}".format(
                LOGIN.base_url,
                "3" if LOGIN.api is True else "latest",
                group_name,
                swap_group,
            )
        else:
            return "{}/rest/api/{}/group".format(
                LOGIN.base_url, "3" if LOGIN.api is True else "latest"
            )

    @classmethod
    def group_jira_users(cls, group_name: str, account_id: str = None) -> str:
        """Used for addition and removal of users to and from groups.

         :request POST: - Adds a user to a group.

         :query param: groupname required, datatype -> string

         :body param: name, accountId, datatype -> string
                      returns 201 if successful

         :request DELETE: - Removes a user from a group.

         :query param: group_name required, account_id required,
                       datatype -> string returns 200 if successful

        :param group_name: name of group

        :param account_id: string of a user account

         :return: A string of the url
        """
        if account_id is not None:
            return "{}/rest/api/{}/group/user?groupname={}&accountId={}".format(
                LOGIN.base_url,
                "3" if LOGIN.api is True else "latest",
                group_name,
                account_id,
            )
        else:
            return "{}/rest/api/{}/group/user?groupname={}".format(
                LOGIN.base_url,
                "3" if LOGIN.api is True else "latest",
                group_name,
            )

    @classmethod
    def projects(
        cls,
        id_or_key: Union[str, int] = None,
        query: Optional[str] = None,
        uri: Optional[str] = None,
        enable_undo: Optional[bool] = None,
    ) -> str:
        """Create, delete, update, archive, get status.

               :request POST: - for project creations.
               The project types are available according to the installed
               Jira features as `follows
               <https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-projects/#api-rest-api-3-project-post>`_

               :param id_or_key: required

               :param uri: optional for accessing other project
                           endpoints -> string

                           Example::

                          endpoint: /rest/api/3/project/{projectIdOrKey}/{archive}

                          available options [archive, delete, restore, statuses]

                                * archive - Archives a project. Archived
                                 projects cannot be deleted.

                                * delete - Deletes a project asynchronously.

                                * restore - Restores a project from the
                                 Jira recycle bin.

                                * statuses - Returns the valid statuses
                                 for a project.

        .. _follows:

             :body param: projectTypeKey and projectTemplateKey required
                    for creation, datatype -> string
                   : name, key, description, leadAccountId, url,
                    assigneeType, datatype -> string
                   : avatarId, issueSecurityScheme, permissionScheme,
                    notificationScheme, categoryId,
                    datatype -> integer

             :request GET: - Returns the project details for a project.
                            This operation can be accessed anonymously.

             :query param: expand, datatype -> string
                           properties, datatype -> Array<string>

              :request PUT: - Updates the project details for a project.

               :param query:  expand, datatype -> string

               :body param:  datatype -> string
                  : name, key, description, leadAccountId, url,
                   assigneeType, datatype -> string
                  : avatarId, issueSecurityScheme, permissionScheme,
                   notificationScheme, categoryId,
                   datatype -> integer

               :request DELETE: - Deletes a project.

               :param enable_undo:  datatype -> boolean

               :return: A string of the url
        """
        if uri is not None:
            return "{}/rest/api/{}/project/{}/{}".format(
                LOGIN.base_url,
                "3" if LOGIN.api is True else "latest",
                id_or_key,
                uri,
            )
        else:
            if query is not None:
                return "{}/rest/api/{}/project/{}?{}".format(
                    LOGIN.base_url,
                    "3" if LOGIN.api is True else "latest",
                    id_or_key,
                    query,
                )
            else:
                if enable_undo is not None:
                    return "{}/rest/api/{}/project/{}?enableUndo={}".format(
                        LOGIN.base_url,
                        "3" if LOGIN.api is True else "latest",
                        id_or_key,
                        enable_undo,
                    )
                else:
                    if id_or_key is not None:
                        return "{}/rest/api/{}/project/{}".format(
                            LOGIN.base_url,
                            "3" if LOGIN.api is True else "latest",
                            id_or_key,
                        )
                    else:
                        return "{}/rest/api/{}/project".format(
                            LOGIN.base_url,
                            "3" if LOGIN.api is True else "latest",
                        )

    @classmethod
    def issues(
        cls,
        issue_key_or_id: Union[str, int] = None,
        query: Optional[Any] = None,
        uri: Optional[str] = None,
        event: bool = False,
    ) -> str:
        """Creates issues, delete issues,  bulk create issue, transitions.

        A transition may be applied, to move the issue or subtask to a
        workflow step other than the default start step, and issue
        properties set.

        :request POST: - Creates an issue or, where the option to
                         create subtasks is enabled in Jira, a subtask.

        :param uri: available options [bulk, createmeta]

                   * e.g. endpoint: ``/rest/api/3/issue/bulk``
                   * e.g. endpoint ``/rest/api/3/issue/createmeta``

        :param query: Use the query keyword argument
                     and structure a parameter

                    * e.g. query="notifyUsers=false"
                    OR in the case of changelog the endpoint of "changelog"
                    ``/rest/api/3/issue/{issueIdOrKey}/changelog``

        :param event: datatype -> boolean

                 * determine if you can get a changelog from the issue.
                 default is false. if True required parameters are:

        :param issue_key_or_id:

        :param issue_key_or_id: -> The body parameter has to be a bundled
                                data that should be posted to the desired
                                endpoint.


        :query param: updateHistory, datatype -> boolean

        :body param: transition, fields, update, historyMetadata, datatype -> object
                              : properties, datatype -> Array<EntityProperty>
                              : Additional Properties, datatype -> Any

        :request POST:  Bulk create issue
                        Creates an issues and, where the option to
                        create subtasks is enabled in Jira, subtasks.

        :body param: issueUpdates, datatype -> Array<IssueUpdateDetails>
                                 : Additional Properties, datatype -> Any

        :request GET: - Create issue metadata
                     Returns a details of projects, issue types within
                     projects, and, when requested,
                     the create screen fields for each issue type for the user.

        :query param: projectIds, projectKeys, issuetypeIds, issuetypeNames,
                    datatype -> Array<string>
                   : expand, datatype -> string

        :request GET:  Get issue. Return the details of an issue

                  Example::

                  endpoint  ``/rest/api/3/issue/{issueIdOrKey}``

        :query param: issue_key_or_id required
                    fields, properties, datatype -> Array<string>
                    fieldsByKeys, updateHistory,  datatype -> boolean
                    expand, datatype -> string


        :request PUT: - Edits an issue. A transition may be applied
                    and issue properties
                    updated as part of the edit.

                    Example::

                    endpoint  /rest/api/3/issue/{issueIdOrKey}

        :query param: issue_key_or_id required
                    : notifyUsers, overrideScreenSecurity,
                    overrideEditableFlag, datatype -> boolean

        :body param: transition, fields, update, historyMetadata,
                     properties, Additional Properties,
                    datatype -> object

        :request DELETE: Deletes an issue.

                      Example::

                      endpoint  ``/rest/api/3/issue/{issueIdOrKey}``

        :query param: issue_key_or_id required
                      : deleteSubtasks, datatype -> string,
                      values = (true | false)

        :return: A string of the url
        """
        if uri is not None and query is None:
            return "{}/rest/api/{}/issue/{}".format(
                LOGIN.base_url, "3" if LOGIN.api is True else "latest", uri
            )
        elif uri is not None and query is not None:
            return "{}/rest/api/{}/issue/{}?{}".format(
                LOGIN.base_url,
                "3" if LOGIN.api is True else "latest",
                uri,
                query,
            )
        else:
            if issue_key_or_id is not None and query is None:
                return "{}/rest/api/{}/issue/{}".format(
                    LOGIN.base_url,
                    "3" if LOGIN.api is True else "latest",
                    issue_key_or_id,
                )

            elif issue_key_or_id is not None and query is not None:
                return (
                    "{}/rest/api/{}/issue/{}?{}".format(
                        LOGIN.base_url,
                        "3" if LOGIN.api is True else "latest",
                        issue_key_or_id,
                        query,
                    )
                    if event is False
                    else "{}/rest/api/{}/issue/{}/{}".format(
                        LOGIN.base_url,
                        "3" if LOGIN.api is True else "latest",
                        issue_key_or_id,
                        query,
                    )
                )
            else:
                return "{}/rest/api/{}/issue".format(
                    LOGIN.base_url, "3" if LOGIN.api is True else "latest"
                )

    @classmethod
    def comment(
        cls,
        query: str = None,
        key_or_id: Union[str, int] = None,
        start_at: int = 0,
        **kwargs: Any,
    ) -> str:
        """Create, update, delete or get a comment.

        :request POST: - Returns a paginated list of just the comments
                     for a list of comments specified by comment IDs.

        :param query: datatype -> string

        :query param: expand datatype -> string

               available options below

               renderedBody Returns the comment body rendered in HTML.

               properties, returns the comment's properties.

        :body param - ids: datatype -> Array<integer>

           The list of comment IDs. A maximum of 1000 IDs can be specified.

        :request GET: - Returns all comments for an issue.

        :param key_or_id: datatype -> string required

        :param start_at: datatype -> integer defaults to 0

        :param kwargs: Additional arguments

                       **Acceptable options**

                       - max_results: datatype -> integer defaults to 50

                            :query param: orderBy datatype -> string
                                          Valid values: created,
                                          -created, +created

                       - event: defaults to false, set to true to

                            :query param: expand

                            :body param:  body datatype -> Anything
                                          visibility -> The group or role to
                                          which this comment is visible.
                                          Optional on create and update.

                                          properties datatype -> Array<EntityProperty>

                                          A list of comment properties.
                                          Optional on create and update.
                                          Additional Properties
                                          datatype ->anything

                       - ids: datatype integers - The ID of the comment.

                              :query param: expand

        :request POST:  Adds a comment to an issue.
                      key_or_id required

        :request GET: - Returns a comment.

        :request PUT: - Updates a comment.
                       key_or_id required
                       ids The ID of the comment.

        :request DELETE: - Deletes a comment.
                        key_or_id required
                        ids required


        :return: A string of the url
        """
        max_results: int = kwargs.get("max_results", 50)
        ids: int = kwargs.get("ids") if "ids" in kwargs else None
        event: bool = kwargs.get("event", False)
        if key_or_id is not None and ids is None:
            return (
                f"{LOGIN.base_url}/rest/api/{'3' if LOGIN.api is True else 'latest'}/issue/{key_or_id}/comment"
                if event is False
                else f"{LOGIN.base_url}/rest/api/{'3' if LOGIN.api is True else 'latest'}/issue/{key_or_id}/comment?"
                f"startAt={start_at}&maxResults={max_results}&{query}"
            )

        elif key_or_id is not None and ids is not None:
            return "{}/rest/api/{}/issue/{}/comment/{}".format(
                LOGIN.base_url,
                "3" if LOGIN.api is True else "latest",
                key_or_id,
                ids,
            )
        else:
            return "{}/rest/api/{}/comment/list?{}".format(
                LOGIN.base_url, "3" if LOGIN.api is True else "latest", query
            )

    @classmethod
    def issue_export(
        cls,
        query: Optional[str] = None,
        start: int = 0,
        limit: int = 1000,
        fields: str = "all",
    ) -> str:
        """
        Generate an export of Jira issues using a JQL.

        :param query: A JQL of the issues to be exported
        :param start: A start counter
        :param limit: Max limit allowed for export
        :param fields: Determine if export is current fields or all fields.

        .. versionchanged:: 0.7.6

        fields - added a keyword argument for transition between current and all
                fields

        query - Renamed "url" parameter into "query" for better clarity of names.

        :return: A string of the export URL
        """
        return (
            "{}/sr/jira.issueviews:searchrequest-csv-{}-fields/temp/"
            "SearchRequest.csv?jqlQuery={}&tempMax={}&pager/start={}".format(
                LOGIN.base_url, fields, query, limit, start
            )
        )

    @classmethod
    def project_validate(cls, key_or_name: str, check: str = None) -> str:
        """
        Validates a project key by confirming the key is a valid
        string and not in use. If checking for project key or name,
        and it is in use, an auto generated project key or name is returned

        When the project does not exist, the below result is
        gotten.

        Example 1::

         {"errorMessages":[],"errors":{}}

        When the project exist, the below result is gotten

        Example 2::

          {"errorMessages":[],"errors":{"projectKey":
          "Project 'Test Project 1' uses this project key."}}

        :param key_or_name: A project key to search or name when check
                          argument is not None

        :param check: Validates a project key or name

                     *options*
                     * key
                     * name

        :return: A string
        """
        if check is None:
            return "{}/rest/api/{}/projectvalidate/key?{}".format(
                LOGIN.base_url,
                "3" if LOGIN.api is True else "latest",
                f"key={key_or_name}",
            )
        else:
            if check.lower() == "key":
                return "{}/rest/api/{}/projectvalidate/validProjectKey?{}".format(
                    LOGIN.base_url,
                    "3" if LOGIN.api is True else "latest",
                    f"key={key_or_name}",
                )
            elif check.lower() == "name":
                return "{}/rest/api/{}/projectvalidate/validProjectName?{}".format(
                    LOGIN.base_url,
                    "3" if LOGIN.api is True else "latest",
                    f"name={key_or_name}",
                )
            else:
                raise JiraOneErrors(
                    "name",
                    "Invalid value provided for check argument"
                    ". See jiraone docs for more info.",
                )

    @classmethod
    def runbackup(cls):
        """Runs a backup process for the environment

        Example 1::
        # send a POST request with the payload
        payload_data = {"cbAttachments": "false", "exportToCloud": "true"}
        # changing "cbAttachments" to "true" will enable backup with attachments

        """
        return "{}/rest/backup/1/export/runbackup".format(LOGIN.base_url)


class For:
    """A Class to show the implementation of a 'for' loop.

    It calls the __iter__ magic method then the __next__ method
    and raises a StopIteration once it reaches the end of the loop.
    Datatype expected are list, dict, tuple, str, set or int.

    Example 1::

     from jiraone import For

     data = {"work": "home", "house": 2}
     result = For(data)
     print(list(result))
     # [{'work': 'home'}, {'house': 2}]

    accessing dictionary index using private method `__dictionary__`

    Example 2::

      # previous expression
      print(result.__dictionary__(1))
      # {'house': 2}

    The above shows how you can call an index of a dictionary object.

    Example 3::

       from jiraone import For

       data = "Summary"
       result = For(data)
       print(list(result))
       # ['S', 'u', 'm', 'm', 'a', 'r', 'y']

    Basically you can get a list of any data structure used. For integers, it
    creates a range of those numbers

    """

    def __init__(
        self, data: Union[list, tuple, dict, set, str, int], limit: int = 0
    ) -> None:
        self.data = data
        if isinstance(self.data, int):
            self.data = range(1, data + 1)
        if isinstance(self.data, set):
            self.data = list(data)
        self.index = len(self.data)
        self.limit = limit

    def __iter__(self) -> Any:
        return self

    def __next__(self) -> Any:
        if self.limit == self.index:
            raise StopIteration
        marker = self.limit
        self.limit += 1
        return (
            self.data[marker]
            if not isinstance(self.data, dict)
            else self.__dictionary__(marker)
        )

    def __dictionary__(self, index: int = 0) -> Dict:
        """A method that converts a dictionary into an item list."""
        keys = self.data.keys()
        values = self.data.values()
        return {list(keys)[index]: list(values)[index]}


class Field:
    """Field class helps with Jira fields.

    It helps with posting, putting and getting various fields or field type.

    * It comes with two attributes

      * field_type

      * field_search_key

    """

    # field type listing
    field_type = {
        "cascadingselect": "com.atlassian.jira.plugin.system.customfieldtypes:cascadingselect",
        "datepicker": "com.atlassian.jira.plugin.system.customfieldtypes:datepicker",
        "datetime": "com.atlassian.jira.plugin.system.customfieldtypes:datetime",
        "float": "com.atlassian.jira.plugin.system.customfieldtypes:float",
        "grouppicker": "com.atlassian.jira.plugin.system.customfieldtypes:grouppicker",
        "importid": "com.atlassian.jira.plugin.system.customfieldtypes:importid",
        "labels": "com.atlassian.jira.plugin.system.customfieldtypes:labels",
        "multicheckboxes": "com.atlassian.jira.plugin.system.customfieldtypes:multicheckboxes",
        "multigrouppicker": "com.atlassian.jira.plugin.system.customfieldtypes:multigrouppicker",
        "multiselect": "com.atlassian.jira.plugin.system.customfieldtypes:multiselect",
        "multiuserpicker": "com.atlassian.jira.plugin.system.customfieldtypes:multiuserpicker",
        "multiversion": "com.atlassian.jira.plugin.system.customfieldtypes:multiversion",
        "project": "com.atlassian.jira.plugin.system.customfieldtypes:project",
        "radiobuttons": "com.atlassian.jira.plugin.system.customfieldtypes:radiobuttons",
        "readonlyfield": "com.atlassian.jira.plugin.system.customfieldtypes:readonlyfield",
        "select": "com.atlassian.jira.plugin.system.customfieldtypes:select",
        "textarea": "com.atlassian.jira.plugin.system.customfieldtypes:textarea",
        "textfield": "com.atlassian.jira.plugin.system.customfieldtypes:textfield",
        "url": "com.atlassian.jira.plugin.system.customfieldtypes:url",
        "userpicker": "com.atlassian.jira.plugin.system.customfieldtypes:userpicker",
        "version": "com.atlassian.jira.plugin.system.customfieldtypes:version",
        "sprint": "com.pyxis.greenhopper.jira:gh-sprint",
        "epiclink": "com.pyxis.greenhopper.jira:gh-epic-link",
        "components": "components",
        "fixversions": "fixVersions",
        "originalestimate": "timeoriginalestimate",
        "timetracking": "timetracking",
        "reporter": "reporter",
        "assignee": "assignee",
        "description": "description",
        "Epic Status": "com.pyxis.greenhopper.jira:gh-epic-status",
        "Epic Name": "com.pyxis.greenhopper.jira:gh-epic-label",
        "versions": "versions",
    }
    # field search key listing
    field_search_key = {
        "cascadingselectsearcher": "com.atlassian.jira.plugin.system.customfieldtypes:cascadingselectsearcher",
        "daterange": "com.atlassian.jira.plugin.system.customfieldtypes:daterange",
        "datetimerange": "com.atlassian.jira.plugin.system.customfieldtypes:datetimerange",
        "exactnumber": "com.atlassian.jira.plugin.system.customfieldtypes:exactnumber",
        "exacttextsearcher": "com.atlassian.jira.plugin.system.customfieldtypes:exacttextsearcher",
        "grouppickersearcher": "com.atlassian.jira.plugin.system.customfieldtypes:grouppickersearcher",
        "labelsearcher": "com.atlassian.jira.plugin.system.customfieldtypes:labelsearcher",
        "multiselectsearcher": "com.atlassian.jira.plugin.system.customfieldtypes:multiselectsearcher",
        "numberrange": "com.atlassian.jira.plugin.system.customfieldtypes:numberrange",
        "projectsearcher": "com.atlassian.jira.plugin.system.customfieldtypes:projectsearcher",
        "textsearcher": "com.atlassian.jira.plugin.system.customfieldtypes:textsearcher",
        "userpickergroupsearcher": "com.atlassian.jira.plugin.system.customfieldtypes:userpickergroupsearcher",
        "versionsearcher": "com.atlassian.jira.plugin.system.customfieldtypes:versionsearcher",
    }

    @staticmethod
    def search_field(find_field: str = None) -> Any:
        """Search for custom fields.

        .. note::

         When using on Jira Server or DC, this method will return
         all fields.

        :param find_field: A field name to search.

        :return: A dictionary if field is found else None
        """
        fields = (
            find_field
            if find_field is not None
            else sys.exit("You must enter a field name")
        )
        count_start_at = 0
        while True:
            load = (
                LOGIN.get(
                    endpoint.get_field(query="type=custom", start_at=count_start_at)
                )
                if LOGIN.api is True
                else LOGIN.get(endpoint.get_field(system="all"))
            )

            if load.status_code < 300:
                data = load.json().get("values") if LOGIN.api is True else load.json()
                break_out = count_start_at > (
                    load.json().get("total") if LOGIN.api is True else len(data)
                )
                for value in data:
                    if value["name"] == fields:
                        return {
                            "id": value.get("id"),
                            "name": value.get("name"),
                            "customType": value.get("schema").get("custom"),
                            "customId": value.get("schema").get("customId"),
                            "type": value.get("schema").get("type"),
                        }
                count_start_at += 50
                if break_out:
                    break
            else:
                # if the request failed, quietly stop the loop
                break

    @staticmethod
    def get_field(find_field: str = None) -> Any:
        """Search for system fields or custom fields.

        :param find_field: A field name to search.

        :return: A dictionary if field is found else None
        """
        fields = (
            find_field
            if find_field is not None
            else sys.exit("You must enter a field name")
        )
        load = LOGIN.get(endpoint.get_field(system="type=system"))
        if load.status_code < 300:
            data = load.json()
            for value in data:
                if fields in value["name"]:
                    if fields == value["name"]:
                        if "schema" in value:
                            if "customId" not in value["schema"]:
                                return {
                                    "name": value.get("name"),
                                    "id": value.get("id"),
                                    "custom": value.get("custom"),
                                    "key": value.get("key"),
                                    "searchable": value.get("searchable"),
                                    "type": value.get("schema").get("type"),
                                    "system": value.get("schema").get("system"),
                                }
                            return {
                                "name": value.get("name"),
                                "id": value.get("id"),
                                "key": value.get("key"),
                                "searchable": value.get("searchable"),
                                "customType": value.get("schema").get("custom"),
                                "customId": value.get("schema").get("customId"),
                                "type": value.get("schema").get("type"),
                                "custom": value.get("custom"),
                            }
                        if "schema" not in value["name"]:
                            return {
                                "name": value.get("name"),
                                "id": value.get("id"),
                                "key": value.get("key"),
                                "searchable": value.get("searchable"),
                                "custom": value.get("custom"),
                            }

    def update_field_data(
        self,
        data: Any = None,
        find_field: str = None,
        field_type: str = "custom",
        key_or_id: Union[str, int] = None,
        show: bool = True,
        **kwargs,
    ) -> Any:
        """Field works for.

        All field types mentioned on the Field class attributes.

        :request PUT:

        :param data: The data you're trying to process,
                     depending on what field it could be any object.

        :param find_field: Name of the custom field or
                          system field to find in strings.

        :param field_type: Available options - system or custom.

        :param key_or_id: Issue key or id of an issue.

        :param show: Allows you to print out a formatted
                   field that was searched.

        :param kwargs: Perform other operations with keyword args

                   * options arg is a string and has two values
                   "add" or "remove".

                   * query arg is a string, and it can have any value
                    that is stated on the endpoint.issue() method
                         e.g. query="notifyUsers=false"

        :return: Any
        """
        search = None
        options = None if "options" not in kwargs else kwargs["options"]
        query = None if "query" not in kwargs else kwargs["query"]
        if field_type == "custom":
            search = self.search_field(find_field)
        elif field_type == "system":
            search = self.get_field(find_field)
        echo({"Field data returned": search}) if show is True else ""
        response = None
        payload = None

        def separated(pull: Any = Any) -> Any:
            """Check if the value is a string or list."""
            if isinstance(pull, str):
                if "," in pull:
                    manipulate = pull.split(",")
                else:
                    manipulate = [pull]
                return manipulate
            elif isinstance(pull, list):
                return pull
            else:
                raise JiraOneErrors(
                    "wrong",
                    "You are using the wrong data type. " "Please check again.",
                )

        if data == "" or data is None:
            if "customType" in search:
                if search["customType"] in [
                    self.field_type["multicheckboxes"],
                    self.field_type["multiselect"],
                    self.field_type["labels"],
                    self.field_type["version"],
                ]:
                    attr = {search["id"]: []}
                    payload = self.data_load(attr)
                elif search["customType"] in [
                    self.field_type["select"],
                    self.field_type["cascadingselect"],
                    self.field_type["radiobuttons"],
                ]:
                    attr = {search["id"]: None}
                    payload = self.data_load(attr)
                else:
                    attr = {search["id"]: None}
                    payload = self.data_load(attr)
            elif "customType" not in search:
                if search["key"] in [
                    self.field_type["components"],
                    self.field_type["fixversions"],
                ]:
                    attr = {search["id"]: []}
                    payload = self.data_load(attr)
                elif search["key"] in [
                    "assignee",
                    "reporter",
                    self.field_type["userpicker"],
                ]:
                    attr = {search["id"]: {"accountId": None}}
                    payload = self.data_load(attr)
                else:
                    attr = {search["id"]: None}
                    payload = self.data_load(attr)
            response = LOGIN.put(
                endpoint.issues(issue_key_or_id=key_or_id, query=query),
                payload=payload,
            )
        elif data != "" or data is not None:
            if "customType" in search:
                if search["customType"] in [
                    self.field_type["multiselect"],
                    self.field_type["multicheckboxes"],
                ]:
                    if options is None:
                        if not isinstance(data, str):
                            raise JiraOneErrors(
                                "wrong",
                                "Expecting a string value "
                                "or a string of values separated by"
                                " comma.",
                            )
                        else:
                            attr = {search["id"]: self.multi_field(data)}
                            payload = self.data_load(attr)
                    elif options == "add" or options == "remove":
                        for f in separated(data):
                            get_data = self.extract_issue_field_options(
                                key_or_id=key_or_id,
                                search=search,
                                amend=options,
                                data=f,
                            )
                            if len(get_data) == 0:
                                attr = {search["id"]: None}
                                payload = self.data_load(attr)
                            else:
                                concat = ",".join(get_data)
                                attr = {search["id"]: self.multi_field(concat)}
                                payload = self.data_load(attr)
                            LOGIN.put(
                                endpoint.issues(issue_key_or_id=key_or_id, query=query),
                                payload=payload,
                            )
                    else:
                        raise JiraOneErrors(
                            "value",
                            'Excepting string value as "add" or "remove" '
                            "from the options keyword argument "
                            'got value: "{}" instead.'.format(options),
                        )
                    response = LOGIN.put(
                        endpoint.issues(issue_key_or_id=key_or_id, query=query),
                        payload=payload,
                    )
                elif search["customType"] == self.field_type["cascadingselect"]:
                    cass = self.cascading(data)
                    if len(cass) > 3:
                        attr = {
                            search["id"]: {
                                "value": cass.__getitem__(1).lstrip(),
                                "child": {"value": cass.__getitem__(3).lstrip()},
                            }
                        }
                        payload = self.data_load(attr)
                        response = LOGIN.put(
                            endpoint.issues(issue_key_or_id=key_or_id, query=query),
                            payload=payload,
                        )
                    elif len(cass) <= 3:
                        attr = {search["id"]: {"value": cass.__getitem__(1).lstrip()}}
                        payload = self.data_load(attr)
                        response = LOGIN.put(
                            endpoint.issues(issue_key_or_id=key_or_id, query=query),
                            payload=payload,
                        )
                elif search["customType"] in [
                    self.field_type["radiobuttons"],
                    self.field_type["select"],
                ]:
                    attr = {search["id"]: {"value": data}}
                    payload = self.data_load(attr)
                    response = LOGIN.put(
                        endpoint.issues(issue_key_or_id=key_or_id, query=query),
                        payload=payload,
                    )
                elif search["customType"] in [
                    self.field_type["labels"],
                    self.field_type["version"],
                ]:
                    # add a list of values in the form of a list
                    # or string for single value
                    if options is None:
                        if not isinstance(data, list):
                            raise JiraOneErrors("wrong", "Expecting a list of values")
                        else:
                            if len(data) > 1:
                                raise JiraOneErrors(
                                    "value",
                                    "Expecting 1 value got {}. Use the "
                                    "update parameter for "
                                    "multiple values".format(len(data)),
                                )
                            else:
                                attr = {search["id"]: data}
                                payload = self.data_load(attr)
                    elif (
                        options == "add" or options == "remove"
                    ):  # update the field with the desired value
                        if not isinstance(data, list):
                            raise JiraOneErrors("wrong", "Expecting a list of values")
                        else:
                            if len(data) == 1:
                                attr = {search["id"]: [{options: data[0]}]}
                                payload = self.data_load(attr, s="update")
                            elif len(data) > 1:
                                for q in data:
                                    attr = {search["id"]: [{options: q}]}
                                    payload = self.data_load(attr, s="update")
                                    LOGIN.put(
                                        endpoint.issues(
                                            issue_key_or_id=key_or_id,
                                            query=query,
                                        ),
                                        payload=payload,
                                    )
                    else:
                        raise JiraOneErrors(
                            "value",
                            'Excepting string value as "add" or "remove" from '
                            "the options keyword argument "
                            'got value: "{}" instead.'.format(options),
                        )
                    response = LOGIN.put(
                        endpoint.issues(issue_key_or_id=key_or_id, query=query),
                        payload=payload,
                    )
                elif search["customType"] in [
                    self.field_type["multiuserpicker"],
                    self.field_type["userpicker"],
                ]:
                    # add a list of values in the form of a
                    # list or string for single value
                    if options is None:
                        if not isinstance(data, str):
                            raise JiraOneErrors("wrong")
                        else:
                            if search["type"] == "user":
                                attr = {search["id"]: {"accountId": data}}
                                payload = self.data_load(attr)
                            else:
                                attr = {
                                    search["id"]: self.multi_field(data, s="accountId")
                                }
                                payload = self.data_load(attr)
                    elif options == "add" or options == "remove":
                        # update the field with the desired value
                        if not isinstance(data, list):
                            raise JiraOneErrors("wrong", "Excepting a list value")
                        else:
                            if search["type"] == "user":
                                raise JiraOneErrors(
                                    "wrong",
                                    "You cannot post "
                                    "multiple values to this user field.",
                                )
                            else:
                                for f in separated(data):
                                    get_data = self.extract_issue_field_options(
                                        key_or_id=key_or_id,
                                        search=search,
                                        amend=options,
                                        data=f,
                                    )
                                    if len(get_data) == 0:
                                        attr = {search["id"]: None}
                                        payload = self.data_load(attr)
                                    else:
                                        concat = ",".join(get_data)
                                        attr = {
                                            search["id"]: self.multi_field(
                                                concat, s="accountId"
                                            )
                                        }
                                        payload = self.data_load(attr)
                                    LOGIN.put(
                                        endpoint.issues(
                                            issue_key_or_id=key_or_id,
                                            query=query,
                                        ),
                                        payload=payload,
                                    )
                    else:
                        raise JiraOneErrors(
                            "value",
                            'Excepting string value as "add" or "remove" '
                            "from the options keyword argument "
                            'got value: "{}" instead.'.format(options),
                        )
                    response = LOGIN.put(
                        endpoint.issues(issue_key_or_id=key_or_id, query=query),
                        payload=payload,
                    )
                else:
                    if options is None:
                        attr = {search["id"]: data}
                        payload = self.data_load(attr)
                    response = LOGIN.put(
                        endpoint.issues(issue_key_or_id=key_or_id, query=query),
                        payload=payload,
                    )
            elif "customType" not in search:
                if search["key"] in [
                    self.field_type["components"],
                    self.field_type["fixversions"],
                    self.field_type["versions"],
                ]:
                    # add a list of values in the form of a list
                    # or string for single value
                    if options is None:
                        if not isinstance(data, str):
                            raise JiraOneErrors(
                                "value",
                                "Expecting a string value or "
                                "a string of values, separated"
                                " by comma.",
                            )
                        else:
                            attr = {search["id"]: self.multi_field(data, s="name")}
                            payload = self.data_load(attr)
                    elif options == "add" or options == "remove":
                        # update the field with the desired value
                        for f in separated(data):
                            get_data = self.extract_issue_field_options(
                                key_or_id=key_or_id,
                                search=search,
                                amend=options,
                                data=f,
                            )
                            if len(get_data) == 0:
                                attr = {search["id"]: []}
                                payload = self.data_load(attr)
                            else:
                                concat = ",".join(get_data)
                                attr = {
                                    search["id"]: self.multi_field(concat, s="name")
                                }
                                payload = self.data_load(attr)
                            LOGIN.put(
                                endpoint.issues(issue_key_or_id=key_or_id, query=query),
                                payload=payload,
                            )

                    else:
                        raise JiraOneErrors(
                            "value",
                            'Excepting string value as "add" or "remove" '
                            "from the options keyword argument got "
                            'value: "{}" instead.'.format(options),
                        )
                elif search["key"] in ["labels"]:
                    if options is None:
                        if not isinstance(data, list):
                            raise JiraOneErrors("wrong")
                        else:
                            attr = {search["id"]: data}
                            payload = self.data_load(attr)
                    elif (
                        options == "add" or options == "remove"
                    ):  # update the field with the desired value
                        if not isinstance(data, list):
                            raise JiraOneErrors("wrong")
                        else:
                            if len(data) == 1:
                                attr = {search["id"]: [{options: data[0]}]}
                                payload = self.data_load(attr, s="update")
                            # add multiple values to a labels system field
                            elif len(data) > 1:
                                for q in data:
                                    attr = {search["id"]: [{options: q}]}
                                    payload = self.data_load(attr, s="update")
                                    LOGIN.put(
                                        endpoint.issues(
                                            issue_key_or_id=key_or_id,
                                            query=query,
                                        ),
                                        payload=payload,
                                    )
                else:
                    if options is None:
                        if not isinstance(data, (str, dict)):
                            raise JiraOneErrors("wrong")
                        else:
                            if search["key"] in ["assignee", "reporter"]:
                                attr = {search["id"]: {"accountId": data}}
                                payload = self.data_load(attr)
                            elif search["key"] in ["watches"]:
                                payload = data
                            elif search["key"] in ["priority"]:
                                attr = {search["id"]: {"name": data}}
                                payload = self.data_load(attr)
                            elif search["key"] in ["parent"]:
                                attr = {search["id"]: {"key": data}}
                                payload = self.data_load(attr)
                            else:
                                attr = {search["id"]: data}
                                payload = self.data_load(attr)
                    else:
                        raise JiraOneErrors(
                            "wrong" "You cannot post multiple values with these fields."
                        )
                response = (
                    LOGIN.put(
                        endpoint.issues(issue_key_or_id=key_or_id, query=query),
                        payload=payload,
                    )
                    if search["key"] != "watches"
                    else LOGIN.post(
                        endpoint.issues(
                            issue_key_or_id=key_or_id,
                            query="watchers",
                            event=True,
                        ),
                        payload=payload,
                    )
                )
        return response

    @staticmethod
    def data_load(data: Any = Any, s: Any = None) -> Dict:
        """Process the received data into a dict.

        :param s: Any object to change s to not None

        :param data: any object

        :return: A dictionary content
        """
        if s is None:
            payload = {"fields": data}
        else:
            payload = {"update": data}
        return payload

    @staticmethod
    def multi_field(data: Any = Any, s: str = "value") -> List:
        """Transform any given string separated by comma into an
        acceptable multi value string.

        :param data: any string object data.

        :param s: is a placeholder to determine the object key.

               * e.g. required payload [{"value": "hello"}] -> for
                      Multicheckboxes type of field.
               * e.g. required payload [{"name": "hello"}] -> for
                      Components or Fix versions type of field.

        :return: A list of data
        """
        m = data
        f = s
        c = []
        if m.split(",").__len__() == 1:
            k = [{f: m}]
            return k
        elif m.split(",").__len__() > 1:
            for u in m.split(","):
                r = {f: u}
                c.append(r)
            return c

    @staticmethod
    def cascading(data: Any = Any) -> Any:
        """Transform a string or a list into a cascading select type.

        :param data: A string or list content

        :return: A list object or none.
        """
        m = str(data)
        if isinstance(data, list):
            if len(data) == 1:
                m = f"Parent values: {data[0]}(10059)"
            elif 1 < len(data) <= 2:
                m = f"Parent values: {data[0]}(10059)Level 1 values: {data[1]}(10060)"
            elif len(data) > 2:
                raise JiraOneErrors(
                    "value", "Too many values received, expecting 2 only."
                )

        if m.__len__() > 0:
            k = m.split(")", maxsplit=5)
            d = m.split(")", maxsplit=5)
            z = k.__getitem__(0).split("(")
            e = d.__getitem__(1).split("(")
            b = z.__getitem__(0).split(":")
            i = e.__getitem__(0).split(":")
            vec = [b, i]
            var = [val for elem in vec for val in elem]
            return var

    @staticmethod
    def extract_issue_field_options(
        key_or_id: Union[str, int] = None,
        search: Dict = None,
        amend: str = None,
        data: Any = Any,
    ) -> Any:
        """Get the option from an issue.

        Use this method to extract and amend changes to system fields such as
        Components or fix versions, labels or custom fields
        such a multicheckboxes or multiselect.

        :param key_or_id: Issue key or id of an issue.

        :param search: Issue data of an issue or issue payload.

        :param amend: Available option "add" or "remove"
                      condition to decide action for appending.

        :param data: Our object data that will be processed.

        :return: List or None
        """
        collect = []
        field_type = False if "customType" not in search else True
        value = field.get_field_value(search["name"], key_or_id)

        def determine(content: Any = None) -> None:
            """Determine the type of value to query depending on the data type.

            :param content: A List or Dict data content

            :return: None
            """
            if isinstance(content, list):
                for x in content:
                    if "value" in x:
                        i = x["value"]
                        collect.append(i)
                    if "name" in x:
                        i = x["name"]
                        collect.append(i)
                    if "accountId" in x:
                        i = x["accountId"]
                        collect.append(i)
            if isinstance(content, dict):
                if "value" in content:
                    i = content["value"]
                    collect.append(i)
                if "name" in content:
                    i = content["name"]
                    collect.append(i)
                if "accountId" in content:
                    i = content["accountId"]
                    collect.append(i)

        if field_type is False:
            determine(value)
        if field_type is True:
            if search["type"] == "option-with-child":
                raise JiraOneErrors(
                    "value",
                    "Use the `field.update_field_data()` "
                    "method instead to update "
                    "values to a cascading select field. Exiting...",
                )
            determine(value)

        if amend == "add":
            if data in collect:
                raise JiraOneErrors(
                    "wrong", 'Value "{}" already exist in list'.format(data)
                )
            else:
                collect.append(data)
        elif amend == "remove":
            collect.remove(data)
        else:
            raise JiraOneErrors(
                "value",
                "The amend option cannot be processed "
                'because the value "{}" doesn\'t exist.'
                "Please check your input.".format(amend),
            )

        return collect

    def get_field_value(self, name: str, keys: Union[str, int]) -> Any:
        """Return the value of a field on an issue.

        :param name: The name of a field.

        :param keys: The issue key or issue id of an issue.

        :return: Any datatype is returned
        """
        var = self.get_field(name)
        get_value = LOGIN.get(endpoint.issues(keys)).json()
        try:
            if "errorMessages" in get_value:
                return "It seems you don't have access to this issue {}".format(keys)
            return get_value["fields"][var.get("id")]
        except (AttributeError, KeyError) as i:
            if isinstance(i, AttributeError):
                return (
                    f"<Error: {i} - options: Most probably "
                    f"the field '{name}' cannot be found >"
                )
            if isinstance(i, KeyError):
                return (
                    f"<Error: KeyError on {i} - options: "
                    f"It seems that the field '{name}' "
                    f"doesn't exist within {keys}>"
                )


def echo(obj) -> Any:
    """A Call to the Echo Class.

    :param obj: Any data type to process

    :return: Any
    """
    e = Echo()
    return e.echo(raw=obj)


endpoint = EndPoints()
field = Field()
