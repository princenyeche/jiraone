#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Get access to Atlassian User management REST API.
You can use the same API key for the organizations REST API and the user management REST API.
Create an API key from this URL https://confluence.atlassian.com/x/jPnJOQ
This API provides all the access to the User management REST API.
"""
import typing as t
import requests
import threading
import re
from jiraone.exceptions import JiraOneErrors
from collections import deque


# Define APIs
class UserManagement:
    """
    The UserManagement API is used to access organization profiles on Atlassian sites.
    The alias to this class is called ``manage``

    It comes with the below attributes and methods.

    .. code-block:: python

        token = "YUISNxxx"
        manage.api_token(token)
        manage.LINK  # attribute
        manage.AUTH  # attribute

    """
    # Define constants
    LINK = "https://api.atlassian.com"
    AUTH = {"Accept": "application/json"}

    def __init__(self) -> None:
        """
        An initializer which also helps with property initialization.
        """
        # Property entry point.
        self._org_id_ = None
        self._org_ids_ = None
        self._domain_id_ = None
        self._policy_id_ = None
        self._event_id_ = None

    def get_user_permission(self, account_id: str, query: list = None) -> t.Any:
        """Returns the set of permissions you have for managing the specified Atlassian account.

        :param account_id:  A user string value for Atlassian accounts

        :param query:  A query parameter of Array<string>

                      *Valid options*

                       Valid values: profile, profile.write, profile.read, email.set, lifecycle.enablement,
                       apiToken.read, apiToken.delete

        :return: Any

        """
        if "Authorization" not in self.AUTH:
            raise JiraOneErrors("login", "You need to authenticate to use this resource")
        url = f"{self.LINK}/users/{account_id}/manage" if query is None else \
            f"{self.LINK}/users/{account_id}/manage?{query}"
        return requests.get(url, headers=self.AUTH)

    def manage_profile(self, account_id: str, method: str = "GET", **kwargs: t.Any) -> t.Any:
        """Returns information about a single Atlassian account by ID by using a "GET" request.

        :request PATCH: Updates fields in a user account.
        The profile.write privilege details which fields you can change.

        :request PUT: Sets the specified user's email address.
        Before using this endpoint, you must verify the target domain

        :param account_id:  A user string value for Atlassian accounts

        :param method:  A response method condition

                      *Available options*

                       :request GET:  Get the return request

                       :request PATCH:  Updates a given set of data

                               :body parameter: Any or all user object this is value

                               e.g. {"name": "Lila User", "nickname": "marshmallow"}

                       :request PUT: Change the email account of the user

        :body parameter: email - string
                        e.g. {"email": "prince.nyeche@elfapp.website"}

        :param kwargs: - Contains other options passed to the requests.<patch>

        .. code-block:: python

            # previous expression
            # json=<variable_name>
            payload = {"email": "prince.nyeche@elfapp.website"}
            manage.manage_profile("account_id", "<method>", json=payload)

        :return: Any

        """
        if "Authorization" not in self.AUTH:
            raise JiraOneErrors("login", "You need to authenticate to use this resource")
        url = f"{self.LINK}/users/{account_id}/manage/profile" if method.lower() == "get" or method.lower() == "patch" \
            else f"{self.LINK}/users/{account_id}/manage/email"
        if method.lower() == "get":
            return requests.get(url, headers=self.AUTH)
        if method.lower() == "patch":
            return requests.patch(url, **kwargs, headers=self.AUTH)
        if method.lower() == "put":
            return requests.put(url, **kwargs, headers=self.AUTH)
        else:
            raise JiraOneErrors("wrong", "The method you posted is not available for this operation.")

    def api_token(self, account_id: str, method: str = "GET", token_id: str = None) -> t.Any:
        """Gets the API tokens owned by the specified user
        or Deletes a specified API token by ID.

        :param account_id:  A user string value for Atlassian accounts


        :param method:  A response method condition

        :param token_id: A user token id to be deleted.

        :return: Any
        """
        if "Authorization" not in self.AUTH:
            raise JiraOneErrors("login", "You need to authenticate to use this resource")
        url = f"{self.LINK}/users/{account_id}/manage/api-tokens" if token_id is None else \
            f"{self.LINK}/users/{account_id}/manage/api-tokens/{token_id}"
        if method.lower() == "get":
            return requests.get(url, headers=self.AUTH)
        elif method.lower() == "delete":
            return requests.delete(url, headers=self.AUTH)
        else:
            raise JiraOneErrors("wrong", "Unexpected method received. Only \"GET\" or \"DELETE\" methods allowed")

    def manage_user(self, account_id: str, disable: bool = True, **kwargs) -> t.Any:
        """Disables the specified user account.
        The permission to make use of this resource is exposed by the lifecycle.enablement privilege.

        OR

        Enables the specified user account.

        The permission to make use of this resource is exposed by the lifecycle.enablement privilege.

        :param account_id:  A user string value for Atlassian accounts


        :param disable: A bool option, if True this API url is set to disabled

        :param kwargs: Additional keyword argument to pass body data

                     *Options available when disable is False*

        .. code-block:: python

            # previous expression

            payload = {"message": "On 6-month suspension"}
            manage.manage_user("account_id", json=payload)

        :return: Any
        """
        if "Authorization" not in self.AUTH:
            raise JiraOneErrors("login", "You need to authenticate to use this resource")
        url = f"{self.LINK}/users/{account_id}/manage/lifecycle/disable" if disable is True else \
            f"{self.LINK}/users/{account_id}/manage/lifecycle/enable"
        return requests.post(url, **kwargs, headers=self.AUTH)

    def get_organization(self, org_id: t.Optional[str] = None,
                         filter_by: t.Optional[str] = None,
                         domain_id: t.Optional[str] = None,
                         event_id: t.Optional[str] = None,
                         action: t.Optional[bool] = True,
                         policy_id: t.Optional[str] = None,
                         **kwargs: t.Any) -> t.Any:
        """GET request for the organization API.

        Returns a list of your organizations (based on your API key).

        Returns information about a single organization by ID.

        Returns a list of users in an organization.

        Returns a list of domains in an organization one page at a time.

        Returns information about a single verified domain by ID.

        Returns information about a single event by ID.

        Returns information about org policies

        Returns information about a single policy by ID

        :param org_id: Retrieve the organization id from the API key

        :param domain_id: Retrieve domain details

        :param filter_by: Use to determine the endpoint to return

                   *Valid options*

                     * users - return the users in an organization

                     * domains - list of domains in an organization

                     * events - list of events in an audit log

                     * policies - get the policy of the organization

        :param event_id: Use to determine the events in the audit log

        :param action:  Additional positional argument for events. True sets events-actions

                       * action - Sets the event actions, true to enable by default set to true.
                                  e.g action=True

        :param policy_id: An id of the policy

        :param kwargs: Optional arguments

                     *Valid options*

                     Any response argument

                     e.g json=payload
                         data=payload



        :return: Any
        """
        if "Authorization" not in self.AUTH:
            raise JiraOneErrors("login", "You need to authenticate to use this resource")
        org_id = self._org_id_ if org_id is None else org_id

        if filter_by is None:
            if org_id is None and domain_id is None:
                url = f"{self.LINK}/admin/v1/orgs"
                resp = requests.get(url, headers=self.AUTH, **kwargs)
                self._parse_data_obj(resp, types="org")
                return resp
            elif org_id is not None and domain_id is None:
                url = f"{self.LINK}/admin/v1/orgs/{org_id}"
                return requests.get(url, headers=self.AUTH, **kwargs)
        else:
            if filter_by == "users":
                if org_id is not None and domain_id is None:
                    url = f"{self.LINK}/admin/v1/orgs/{org_id}/users"
                    return requests.get(url, headers=self.AUTH, **kwargs)
            elif filter_by == "domains":
                if org_id is not None and domain_id is None:
                    url = f"{self.LINK}/admin/v1/orgs/{org_id}/domains"
                    resp = requests.get(url, headers=self.AUTH, **kwargs)
                    self._parse_data_obj(resp, types="domain")
                    return resp
                elif org_id is not None and domain_id is not None:
                    url = f"{self.LINK}/admin/v1/orgs/{org_id}/domains/{domain_id}"
                    return requests.get(url, headers=self.AUTH, **kwargs)
            elif filter_by == "events":
                if org_id is not None:
                    if action is False and event_id is None:
                        url = f"{self.LINK}/admin/v1/orgs/{org_id}/events"
                        resp = requests.get(url, headers=self.AUTH, **kwargs)
                        self._parse_data_obj(resp, types="event")
                        return resp
                    elif action is False and event_id is not None:
                        url = f"{self.LINK}/admin/v1/orgs/{org_id}/events/{event_id}"
                        return requests.get(url, headers=self.AUTH, **kwargs)
                    elif action is True and event_id is None or event_id is not None:
                        url = f"{self.LINK}/admin/v1/orgs/{org_id}/event-actions"
                        return requests.get(url, headers=self.AUTH, **kwargs)
            elif filter_by == "policies":
                if org_id is not None:
                    if policy_id is None:
                        url = f"{self.LINK}/admin/v1/orgs/{org_id}/policies"
                        resp = requests.get(url, headers=self.AUTH, **kwargs)
                        self._parse_data_obj(resp, types="policy")
                        return resp
                    elif policy_id is not None:
                        url = f"{self.LINK}/admin/v1/orgs/{org_id}/policies/{policy_id}"
                        return requests.get(url, headers=self.AUTH, **kwargs)
            else:
                raise JiraOneErrors("wrong", "Unexpected error - unable to determine parameter value")

    def manage_organization(self, org_id: str, method: str = "POST",
                            policy_id: t.Optional[str] = None,
                            resource_id: t.Optional[str] = None,
                            **kwargs: t.Any) -> t.Any:
        """Create, put and delete organization data

        Create a policy for an org
        Send a post request by using method="post" as keyword args

        Update a policy for an org.
        Send a put request by using method="put" as keyword args
           You will need to send a payload for the body using the example shown below

        .. code-block:: json

            {
                  "id": "<string>",
                  "type": "policy",
                   "attributes": {
                    "type": "ip-allowlist",
                     "name": "<string>",
                      "status": "enabled",
                      "rule": {},
                       "resources": [
                                       {
                                     "id": "<string>",
                                      "meta": {
                                        "scheduledDate": "<string>",
                                        "migrationStartDateTime": "<string>",
                                          "migrationEndDataTime": "<string>",
                                           "atlassianAccountId": "<string>"
                                   },
                                   "links": {
                                    "ticket": "<string>"
                                        }
                                 }
                      ]
                    }
            }

        Delete a policy for an org


        :param org_id: ID of the organization to create policy for

        :param method: A response method to set

                        *Valid options*

                         * PUT - updates resource

                         * POST - creates resource

                         * DELETE - removes resources

        :param policy_id: ID of the policy

        :param resource_id: Resource ID

        :param kwargs: Additional data to sent in request body

        :return: Any
        """
        if "Authorization" not in self.AUTH:
            raise JiraOneErrors("login", "You need to authenticate to use this resource")
        if method.lower() == "post":
            if org_id is not None and policy_id is None:
                url = f"{self.LINK}/admin/v1/orgs/{org_id}/policies"
                return requests.post(url, headers=self.AUTH, **kwargs)
            elif org_id is not None and policy_id is not None:
                url = f"{self.LINK}/admin/v1/orgs/{org_id}/policies/{policy_id}/resources"
                return requests.post(url, headers=self.AUTH, **kwargs)
        elif method.lower() == "put":
            if org_id is not None and policy_id is not None and resource_id is None:
                url = f"{self.LINK}/admin/v1/orgs/{org_id}/policies/{policy_id}"
                return requests.put(url, headers=self.AUTH, **kwargs)
            elif org_id is not None and policy_id is not None and resource_id is not None:
                url = f"{self.LINK}/admin/v1/orgs/{org_id}/policies/{policy_id}/resources/{resource_id}"
                return requests.put(url, headers=self.AUTH, **kwargs)
        elif method.lower() == "delete":
            if org_id is not None and policy_id is not None and resource_id is None:
                url = f"{self.LINK}/admin/v1/orgs/{org_id}/policies/{policy_id}"
                return requests.delete(url, headers=self.AUTH, **kwargs)
            elif org_id is not None and policy_id is not None and resource_id is not None:
                url = f"{self.LINK}/admin/v1/orgs/{org_id}/policies/{policy_id}/resources/{resource_id}"
                return requests.delete(url, headers=self.AUTH, **kwargs)
        else:
            raise JiraOneErrors("wrong", "Method is not allowed - unexpected option entered method argument.")

    @property
    def org_id(self):
        """Get property of organization id"""
        return self._org_id_

    @org_id.setter
    def org_id(self, content):
        """Sets the value property of organization id"""
        self._org_id_ = content

    @property
    def org_ids(self):
        """Get property of organization ids"""
        return self._org_ids_

    @org_ids.setter
    def org_ids(self, content):
        """Sets the value property of organization ids"""
        self._org_ids_ = content

    @property
    def domain_id(self):
        """Get property of organization domain id"""
        return self._domain_id_

    @domain_id.setter
    def domain_id(self, content):
        """Sets the value property of organization domain id"""
        self._domain_id_ = content

    @property
    def policy_id(self):
        """Get property of organization  policy id"""
        return self._policy_id_

    @policy_id.setter
    def policy_id(self, content):
        """Sets the value property of organization policy id"""
        self._policy_id_ = content

    @property
    def event_id(self):
        """Get property of organization  event id"""
        return self._event_id_

    @event_id.setter
    def event_id(self, content):
        """Sets the value property of organization event id"""
        self._event_id_ = content

    def __repr__(self):

        return f"<JiraOne: {self.LINK} \n" \
               f"This API is accessible>"

    def _parse_data_obj(self, data: requests.Response, types: str = "org") -> None:
        """Parse JSON response object for organization properties.

        :param data: A response object

        :param types: A string of available attributes

        :return: None
        """
        many = []
        total = -1 if types == "org" or types == "domain" else data.json()['meta']['total']
        count = 0
        for ids in data.json()['data']:
            many.append(ids['id']) if 'id' in ids and total == -1 else 0
            while count < total:
                count += 1
                many.append(ids['id'])
                if count >= total:
                    break

        if len(many) == 1:
            if types == "org":
                self._org_id_ = many[0]
            elif types == "policy":
                self._policy_id_ = many[0]
            elif types == "domain":
                self._domain_id_ = many[0]
            elif types == "event":
                self._event_id_ = many[0]
        if len(many) > 1:
            if types == "org":
                self._org_ids_ = many
            elif types == "policy":
                self._policy_id_ = many
            elif types == "domain":
                self._domain_id_ = many
            elif types == "event":
                self._event_id_ = many

    def add_token(self, token: str) -> None:
        """Adds a Bearer token to authenticate the API.

        :param token: An API key

        :return: None
        """
        if not isinstance(token, str):
            raise JiraOneErrors("value", "An API token of type string is required")
        if token == "":
            raise JiraOneErrors("value", "Your API token cannot be an empty string.")
        self.AUTH.update({"Authorization": f"Bearer {token}"})
        # Make a request to get the organization id, domain_id and policy_id and store it as a <property.name_id>
        try:
            # Get access to property values
            threading.Thread(target=self.get_organization).run()
            threading.Thread(target=self.get_organization, kwargs={"filter_by": "policies"}).run()
            threading.Thread(target=self.get_organization, kwargs={"filter_by": "domains"}).run()
            # This property is accessible to premium / enterprise users, so turning off this feature by default,
            # You can still call this from the events request.
            # threading.Thread(target=self.get_organization, kwargs={"filter_by": "events", "action": False}).run()
        except KeyError:
            raise JiraOneErrors("warning", "Your connection has failed. Please check the response to see the reason!")

    def get_all_users(self, source, detail: bool = False) -> deque:
        """Store all user list from organization, so we can search them by email.

        .. code-block:: python

           from jiraone import manage as org

           token = "VGHxxxxx"
           org.add_token(token)
           get_users = org.get_organization(org.org_id, filter_by="users").json()
           all_users = org.get_all_users(get_users)
           # output is a deque list, which can be accessed like a regular list.
           print(all_users)

        :param source: A JSON response payload

        :param detail: Bool defaults to False

        :return: Deque List
        """
        exit("Your source data isn't a valid JSON object.") if not isinstance(source, t.Mapping) else ""
        user_collection = deque()
        exit(f"Incorrect data type {type(detail)} for keyword argument 'detail'. "
             f"Expecting bool type") \
            if not isinstance(detail, bool) else True if detail is True else False
        print("Checking organization users...")
        while True:
            next_item_data = source['links']['next'] if 'links' in source \
                                                        and len(source['links']) > 1 else {}
            for item in source['data']:
                user_data = {
                    "account_id": item.get('account_id'),
                    "email": item.get('email')
                } if detail is False else \
                    {
                        "account_id": item.get('account_id'),
                        "email": item.get('email'),
                        "account_type": item.get('account_type'),
                        "account_status": item.get('account_status'),
                        "name": item.get('name'),
                        "product_access": item.get('product_access'),
                        "link": item.get('links'),
                        "access_billable": item.get('access_billable'),
                        "picture": item.get('picture'),
                        "last_active": item.get('last_active')
                    }
                user_collection.append(list(user_data.values())) if detail is False else \
                    user_collection.append(user_data)
            # If our next item is an empty dict, we want to stop the loop.
            if isinstance(next_item_data, dict):
                break
            source = requests.get(next_item_data, headers=self.AUTH).json()

        return user_collection

    @staticmethod
    def find_user(query: str, source: t.List = None) -> t.Union[t.Dict, t.List]:
        """Finds a specific user.

        :param query: A search term, could be an email, displayname or accountId if
        the ``source`` data is gotten from ``self.get_all_users`` and parameter ``detail=True``

        :param source: A list of users

        :returns: A dict of the user data or a list of the data
        """
        search = None
        pattern_name = r"[\s]"  # This could be the name of a person
        pattern_email = r"[\@]"  # This could be an email address
        pattern_aaid = r"[{5|6|7|8}[a-z]+"  # This could be the account_id
        for term in source:
            if len(re.findall(pattern_aaid, query)) > 3:
                if 'account_id' in term:
                    if term['account_id'] == query:
                        search = term
                else:
                    if term[0] == query:
                        search = term
            if len(re.findall(pattern_email, query)) == 1:
                if 'email' in term:
                    if term['email'] == query:
                        search = term
                else:
                    if term[1] == query:
                        search = term
            if len(re.findall(pattern_name, query)) == 1:
                if 'name' in term:
                    if term['name'] == query:
                        search = term
                else:
                    raise JiraOneErrors("value", "You cannot search with displayName, received 2 items only.")
        return search


manage = UserManagement()
