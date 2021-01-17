#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Example methods of Generating reports

Provided herein are Report Generator Classes and Methods,
Easily generate report for the various endpoints
"""
from typing import Any, Optional, List, Iterable, Tuple, Union
from collections import deque
from jiraone import LOGIN, endpoint, add_log, WORK_PATH
import json
import csv
import sys
import os

CsvData = List[List[str]]


class Projects:
    """Get report on a Project based on user or user's attributes or groups."""

    @staticmethod
    def projects_accessible_by_users(*args: Any, project_folder: str = "Project",
                                     project_file_name: str = "project_file.csv",
                                     user_extraction_file: str = "project_extract.csv",
                                     permission: str = "BROWSE", **kwargs):
        """
        Send an argument as String equal to a value, example: status=live.

        Multiple arguments separate by comma as the first argument in the function, all other arguments should
        be keyword args that follows. This API helps to generate full user accessibility to Projects on Jira.
        It checks the users access and commits the finding to a report file. You can tweak the permission argument
        with the options mention here
        https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-user-search
        for endpoint /rest/api/3/user/permission/search
        """
        count_start_at = 0
        headers = ["Project Key", "Project Name", "Issue Count", "Last Issue Update"]
        file_writer(folder=project_folder, file_name=project_file_name, data=headers)

        def project():
            file_writer(project_folder, project_file_name, data=raw)
            read_users = file_reader(folder=project_folder, file_name=file_name)
            for user in read_users:
                account_id = user[0]
                display_name = user[2]
                active_status = user[3]
                project_key = keys
                find = LOGIN.get(endpoint.find_users_with_permission(account_id, project_key, permission))
                data = json.loads(find.content)
                if str(data) == "[]":
                    raw_vision = [display_name, f"Has {permission} Permission: False",
                                  f"Project: {name}", f"User Status: {active_status}"]
                    file_writer(project_folder, project_file_name, data=raw_vision)
                else:
                    for d in data:
                        d_name = d["displayName"]
                        active = d["active"]
                        raw_vision = [d_name, f"Has {permission} Permission: {active}",
                                      f"Project: {name}", f"User Status: {active_status}"]

                        file_writer(project_folder, project_file_name, data=raw_vision)

        file_name = user_extraction_file
        USER.get_all_users(file=file_name, folder=project_folder, **kwargs)
        print("Project User List Extracted")
        add_log("Project User List Extracted", "info")
        while True:
            load = LOGIN.get(endpoint.get_projects(*args, start_at=count_start_at))
            count_start_at += 50
            if load.status_code == 200:
                results = json.loads(load.content)
                for key in results["values"]:
                    keys = key["key"]
                    name = key["name"]
                    if "insight" in key:
                        insight = key["insight"]
                        if "totalIssueCount" and "lastIssueUpdateTime" in insight:
                            raw = [keys, name, f"{insight['totalIssueCount']}",
                                   f"{insight['lastIssueUpdateTime']}"]
                            project()
                        elif "totalIssueCount" in insight and "lastIssueUpdateTime" not in insight:
                            raw = [keys, name, f"{insight['totalIssueCount']}",
                                   "No data available"]
                            project()
                    else:
                        raw = [keys, name, "No data available", "No data available"]
                        project()

                if count_start_at > results["total"]:
                    print("Project Reporting Completed")
                    print("File extraction completed. Your file is located at {}"
                          .format(path_builder(path=project_folder, file_name=project_file_name)))
                    add_log("Project Reporting Completed", "info")
                    break
            else:
                sys.stderr.write("Unable to fetch data status {} ".format(load.status_code))
                add_log(f"Data retrieval failure due to {load.reason}", "error")
                sys.exit(1)

    @staticmethod
    def dashboards_shared_with(dashboard_folder: str = "Dashboard",
                               dashboard_file_name: str = "dashboard_file.csv",
                               **kwargs):
        """
        Retrieve the Dashboard Id/Name/owner and who it is shared with.

        The only requirement is that the user querying this API should have access to all
        the Dashboard available else it will only return dashboard where the user's view access is allowed.
        """
        count_start_at = 0
        dash_list = deque()  # get the id of dashboard search
        put_list = deque()  # arrange the different values associated with dashboard
        dump_list = deque()  # dump the results into our csv writer
        headers = ["Dashboard Id", "Dashboard Name", "Owner", "Shared Permission"]
        file_writer(folder=dashboard_folder, file_name=dashboard_file_name, data=headers, **kwargs)

        while True:
            load = LOGIN.get(endpoint.search_for_dashboard(start_at=count_start_at))
            count_start_at += 50
            if load.status_code == 200:
                results = json.loads(load.content)
                for value in results["values"]:
                    valid = value["id"]
                    name = value["name"]
                    raw = [valid, name]
                    dash_list.append(raw)

                print("Dashboard List Extracted")
                add_log("Dashboard List Extracted", "info")

                def dash_run():
                    for pem in shared_permission:
                        if "role" in pem:
                            role = f"Role: {pem['role']['name']}"
                            put_list.append(role)
                        if "group" in pem:
                            group = f"Group: {pem['group']['name']}"
                            put_list.append(group)
                        if "type" in pem:
                            types = pem["type"]
                            if types == "project":
                                project = f"Project Name: {pem['project']['name']}"
                                put_list.append(project)
                            if types == "loggedin" or types == "global":
                                put_list.append(types)

                    extract = [d for d in put_list]
                    raw = [value[0], names, owner, extract]
                    dump_list.append(raw)

                for value in dash_list:
                    init = LOGIN.get(endpoint.get_dashboard(value[0]))
                    if init.status_code == 200:
                        expanse = json.loads(init.content)
                        names = expanse["name"]
                        if "owner" in expanse:
                            owner = expanse["owner"]["displayName"]
                        shared_permission = expanse["sharePermissions"]
                        dash_run()
                        put_list = deque()

                file_writer(dashboard_folder, dashboard_file_name, data=dump_list, mark="many")

                if count_start_at > results["total"]:
                    print("Dashboard Reporting Completed")
                    print("File extraction completed. Your file is located at {}"
                          .format(path_builder(path=dashboard_folder, file_name=dashboard_file_name)))
                    add_log("Dashboard Reporting Completed", "info")
                    break

    @staticmethod
    def get_all_roles_for_projects(roles_folder: str = "Roles",
                                   roles_file_name: str = "roles_file.csv",
                                   user_extraction: str = "role_users.csv",
                                   **kwargs):
        """Get the roles available in a project and which user is assigned to which
        role within the project"""
        count_start_at = 0
        headers = ["Project Id ", "Project Key", "Project Name", "Project roles", "User AccountId", "User DisplayName",
                   "User role in Project"]
        file_writer(folder=roles_folder, file_name=roles_file_name, data=headers, **kwargs)

        # get extraction of projects data
        def role_on() -> Any:
            project_role_list = deque()
            for keys in results["values"]:
                role_list = deque()
                key = keys["key"]
                pid = keys["id"]
                name = keys["name"]
                roles = LOGIN.get(endpoint.get_roles_for_project(pid))
                print("Extracting Project Keys {}".format(key))
                add_log("Extracting Project Keys {}".format(key), "info")

                # find out what roles exist within each project
                def role_over() -> Tuple:
                    if roles.status_code == 200:
                        extract = json.loads(roles.content)
                        only_keys = extract.keys()
                        casting = list(only_keys)
                        only_values = extract.items()
                        puller = list(only_values)
                        z = [d for d in puller]
                        return casting, z

                caster = role_over()
                raw = [pid, key, name, caster[0]]
                role_list.append(raw)
                add_log("Appending data to List Queue", "info")

                for user in read_users:
                    account_id = user[0]
                    display_name = user[2]

                    # extract the user role using the appropriate accountId
                    def get_user_role(user_data) -> Any:
                        for users in user_data[1]:
                            check = LOGIN.get(users[1])
                            if check.status_code == 200:
                                result_data = json.loads(check.content)
                                actors = result_data["actors"]
                                for act in actors:
                                    if "actorUser" in act:
                                        if account_id == act["actorUser"]["accountId"]:
                                            res = f"Role Name: {result_data['name']}"
                                            project_role_list.append(res)

                        # function to write collected data into a file
                        def pull_data() -> Any:
                            role_puller = [j for j in project_role_list]
                            project_id = data[0]
                            project_key = data[1]
                            project_name = data[2]
                            project_roles = data[3]
                            raw_dump = [project_id, project_key, project_name, project_roles, account_id, display_name,
                                        role_puller]
                            file_writer(folder=roles_folder, file_name=roles_file_name, data=raw_dump)

                        for data in role_list:
                            pull_data()

                    get_user_role(caster)
                    project_role_list = deque()

        USER.get_all_users(folder=roles_folder, file=user_extraction, **kwargs)
        read_users = file_reader(folder=roles_folder, file_name=user_extraction, **kwargs)
        while True:
            init = LOGIN.get(endpoint.get_projects(start_at=count_start_at))
            if init.status_code == 200:
                print("Project Extraction")
                results = json.loads(init.content)
                add_log("Project Extraction Initiated", "info")
                if count_start_at > results["total"]:
                    break
                if results["total"] > 0:
                    role_on()
            count_start_at += 50

        print("File extraction completed. Your file is located at {}".format(path_builder
                                                                             (path=roles_folder,
                                                                              file_name=roles_file_name)))
        add_log("File extraction completed", "info")

    def get_attachments_on_projects(self, attachment_folder: str = "Attachment",
                                    attachment_file_name: str = "attachment_file.csv",
                                    **kwargs):
        """Return all attachments of a Project or Projects

        Get the size of attachments on an Issue, count those attachments collectively and return the total number
        on all Projects searched. JQL is used as a means to search for the project.
        """
        import re
        attach_list = deque()
        count_start_at = 0
        headers = ["Project id", "Project key", "Project name", "Issue key", "Attachment size",
                   "Attachment type", "Name of file", "Created on by user", "Attachment url"]
        file_writer(folder=attachment_folder, file_name=attachment_file_name, data=headers, **kwargs)

        def pull_attachment_sequence() -> Optional:
            nonlocal attach_list
            for issues in result_data["issues"]:
                keys = issues["key"]
                get_issue_keys = LOGIN.get(endpoint.issues(issue_key_or_id=keys))
                if get_issue_keys.status_code == 200:
                    key_data = json.loads(get_issue_keys.content)
                    data = key_data["fields"]
                    if "project" or "attachment" in data:
                        project_id = data["project"]["id"]
                        project_name = data["project"]["name"]
                        project_key = data["project"]["key"]
                        attachment = data["attachment"]
                        if attachment is not None:
                            for attach in attachment:
                                if "author" in attach:
                                    display_name = attach["author"]["displayName"]

                                def pull_attachment() -> Optional:
                                    file_name = attach["filename"]  # name of the file
                                    created = attach["created"]  # datetime need to convert it
                                    attachment_size = attach["size"]  # in bytes, need to convert to mb
                                    mime_type = attach["mimeType"]
                                    attachment_url = attach["content"]

                                    calc_size = self.byte_converter(attachment_size)

                                    def date_converter(val) -> str:
                                        """split the datetime value and output a string."""
                                        get_date_time = val.split("T")
                                        get_am_pm = get_date_time[1].split(".")
                                        return f"Created on {get_date_time[0]} {get_am_pm[0]}"

                                    calc_date = date_converter(created)
                                    pull = [project_id, project_key, project_name, keys, calc_size, mime_type,
                                            file_name, f"{calc_date} by {display_name}", attachment_url]
                                    attach_list.append(pull)

                                pull_attachment()

            raw_data = [x for x in attach_list]
            file_writer(attachment_folder, attachment_file_name, data=raw_data, mark="many")
            attach_list.clear()

        while True:
            get_issue = LOGIN.get(endpoint.search_issues_jql(start_at=count_start_at, **kwargs))
            if get_issue.status_code == 200:
                result_data = json.loads(get_issue.content)
                if count_start_at > result_data["total"]:
                    print("Attachment extraction completed")
                    add_log("Attachment extraction completed", "info")
                    break

                print("Attachment extraction processing")
                add_log("Attachment extraction processing", "info")
                pull_attachment_sequence()

            count_start_at += 50

        def grade_and_sort() -> Union[float, int]:
            for node in read_file:
                pattern = re.compile(r"(\d*?[0-9]\.[0-9]*)", re.I)
                if pattern is not None:
                    if pattern.search(node[4]):
                        attach_list.append(pattern.search(node[4]).group())

            retain = [float(s) for s in attach_list]
            calc_sum = sum(retain)
            return calc_sum

        def re_write():
            calc_made = grade_and_sort()
            attach_list.clear()
            rd_file = read_file
            # sort the file using the issue_key column
            sorts = sorted(rd_file, key=lambda row: row[3], reverse=False)
            for i in sorts:
                _project_id = i[0]
                _project_key = i[1]
                _project_name = i[2]
                _issue_key = i[3]
                _attach_size = i[4]
                _file_name = i[5]
                _attach_type = i[6]
                _created_by = i[7]
                _attach_url = i[8]
                raw_data_file = [_project_id, _project_key, _project_name, _issue_key,
                                 _attach_size, _file_name, _attach_type, _created_by, _attach_url]
                file_writer(attachment_folder, attachment_file_name, data=raw_data_file)

            # lastly we want to append the total sum of attachment size.
            raw_data_file = ["", "", "", "", "Total Size: {:.2f} MB".format(calc_made), "", "", "", ""]
            file_writer(attachment_folder, attachment_file_name, data=raw_data_file)

        read_file = file_reader(attachment_folder, attachment_file_name, skip=True)
        file_writer(attachment_folder, attachment_file_name, data=headers, mode="w")
        re_write()

        print("File extraction completed. Your file is located at {}".format(path_builder
                                                                             (path=attachment_folder,
                                                                              file_name=attachment_file_name)))
        add_log("File extraction completed", "info")

    @staticmethod
    def byte_converter(val) -> str:
        """1 Byte = 8 Bits.

        using megabyte MB, value is 1000^2
        mebibyte MiB, value is 1024^2
        Therefore val = val / MB
        """
        byte_size = val
        mega_byte = 1000 * 1000
        visor = byte_size / mega_byte
        return "Size: {:.2f} MB".format(visor)

    @staticmethod
    def move_attachments_across_instances(attach_folder: str = "Attachment",
                                          attach_file: str = "attachment_file.csv",
                                          key: int = 3,
                                          attach: int = 6,
                                          file: int = 8,
                                          **kwargs):
        """Ability to post an attachment into another Instance.

        given the data is extracted from a csv file which contains the below information
        * Issue key
        * file name
        * attachment url
        we assumes you're getting this from `def get_attachments_on_project()`
        :param: key, attach, file - integers to specify the index of the columns
              e.g key: 3,
                  attach: 6,
                file: 8
              the above example corresponds with the index if using the `def get_attachments_on_project()`
              otherwise, specify your value in each key args.
        """
        read = file_reader(folder=attach_folder, file_name=attach_file, skip=True, **kwargs)
        for r in read:
            keys = r[key]
            attachment = r[attach]
            _file_name = r[file]
            fetch = LOGIN.get(attachment).content
            # use the files keyword args to send multipart/form-data in the post request of LOGIN.post
            payload = {"file": (_file_name, fetch)}
            # modified our initial headers to accept X-Atlassian-Token to avoid (CSRF/XSRF)
            new_headers = {"Accept": "application/json",
                           "X-Atlassian-Token": "no-check"}
            LOGIN.headers = new_headers
            run = LOGIN.post(endpoint.issue_attachments(keys, query="attachments"), files=payload)
            print("Attachment added to {}".format(keys), "Status code: {}".format(run.status_code))

    @staticmethod
    def download_attachments(file_folder: str = None, file_name: str = None,
                             download_path: str = "Downloads",
                             attach: int = 6,
                             file: int = 8,
                             **kwargs):
        """Download the attachments to your local device read from a csv file.

        we assumes you're getting this from `def get_attachments_on_project()` method.
        :param: cols - list of integers to specify the index of the file columns
              :param: key, attach, file - integers to specify the index of the columns
              e.g key: 3,
                  attach: 6,
                file: 8
              the above example corresponds with the index if using the `def get_attachments_on_project()`
              otherwise, specify your value in each key args.
        """
        read = file_reader(folder=file_folder, file_name=file_name, **kwargs)
        for r in read:
            attachment = r[attach]
            _file_name = r[file]
            fetch = LOGIN.get(attachment).content
            file_writer(download_path, file_name=_file_name, mode="wb", content=fetch, mark="file")
            file_reader(download_path, file_name=_file_name, content=True, mode="rb")
            print("Attachment downloaded to {}".format(download_path), "Status code: {}".format(fetch.status_code))


class Users:
    """
    Below methods helps to Generate the No of Users on Jira Cloud

    You can customize it to determine which user you're looking for.
    >> The below method here displays active or inactive users, so you'll be getting all users
    :param: pull (options)
            -> both: pulls out inactive and active users
            -> active: pulls out only active users
            -> inactive: pulls out inactive users
    :param: user_type (options)
            -> atlassian: a normal Jira Cloud user
            -> customer: this will be your JSM customers
            -> app: this will be the bot users for any Cloud App
            -> unknown: as the name suggest unknown user type probably from oAuth
    """
    user_list = deque()

    def get_all_users(self, pull: str = "both", user_type: str = "atlassian",
                      file: str = None, folder: str = Any, **kwargs) -> Any:
        """Generates a list of users."""
        count_start_at = 0
        validate = LOGIN.get(endpoint.myself())

        while validate.status_code == 200:
            extract = LOGIN.get(endpoint.search_users(count_start_at))
            results = json.loads(extract.content)
            self.user_activity(pull, user_type, results)
            count_start_at += 50
            print("Current Record - At Row", count_start_at)
            add_log(f"Current Record - At Row {count_start_at}", "info")

            if str(results) == "[]":
                break
        else:
            sys.stderr.write("Unable to connect to {} - Login Failed...".format(LOGIN.base_url))
            add_log(f"Login Failure on {LOGIN.base_url}, due to {validate.reason}", "error")
            sys.exit(1)

        if file is not None:
            self.report(category=folder, filename=file)

    def report(self, category: str = Any, filename: str = "users_report.csv") -> Optional:
        """Creates a user report file in CSV format."""
        read = [d for d in self.user_list]
        file_writer(folder=category, file_name=filename, data=read, mark="many")
        add_log(f"Generating report file on {filename}", "info")

    def user_activity(self, status: str = Any, account_type: str = Any, results: List = Any) -> Any:
        """Determines users activity."""

        # get both active and inactive users
        def stack(c: Any, f: Any, s: Any) -> Any:
            if status == "both":
                if s["accountType"] == account_type:
                    return c.user_list.append(f)
            elif status == "active":
                if s["accountType"] == account_type and s["active"] is True:
                    return c.user_list.append(f)
            elif status == "inactive":
                if s["accountType"] == account_type and s["active"] is False:
                    return c.user_list.append(f)

        for each_user in results:
            list_user = [each_user["accountId"], each_user["accountType"], each_user["displayName"],
                         each_user["active"]]
            stack(self, list_user, each_user)

    def get_all_users_group(self, group_folder: str = "Groups", group_file_name: str = "group_file.csv",
                            user_extraction_file: str = "group_extraction.csv", **kwargs):
        """Get all users and the groups associated to them on the Instance."""
        headers = ["Name", "AccountId", "Groups", "User status"]
        file_writer(folder=group_folder, file_name=group_file_name, data=headers, **kwargs)
        file_name = user_extraction_file
        self.get_all_users(file=file_name, folder=group_folder, **kwargs)
        reader = file_reader(file_name=file_name, folder=group_folder, **kwargs)
        for user in reader:
            account_id = user[0]
            display_name = user[2]
            active_status = user[3]
            load = LOGIN.get(endpoint.get_user_group(account_id))
            results = json.loads(load.content)
            get_all = [d["name"] for d in results]
            raw = [display_name, account_id, get_all, active_status]
            file_writer(folder=group_folder, file_name=group_file_name, data=raw)

        print("File extraction completed. Your file is located at {}"
              .format(path_builder(path=group_folder, file_name=group_file_name)))
        add_log("Get Users group Completed", "info")


def path_builder(path: str = "Report", file_name: str = Any, **kwargs):
    """Builds a dir path and file path in a directory."""
    base_dir = os.path.join(WORK_PATH, path)
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
        add_log(f"Building Path {path}", "info")
    base_file = os.path.join(base_dir, file_name)
    return base_file


def file_writer(folder: str = WORK_PATH, file_name: str = Any, data: Iterable = object,
                mark: str = "single", mode: str = "a+", content: str = Any, **kwargs) -> Any:
    """Reads and writes to a file, single or multiple rows or write as byte files."""
    file = path_builder(path=folder, file_name=file_name)
    if mode:
        with open(file, mode) as f:
            write = csv.writer(f, delimiter=",")
            if mark == "single":
                write.writerow(data)
            if mark == "many":
                write.writerows(data)
            if mark == "file":
                f.write(content)
            add_log(f"Writing to file {file_name}", "info")


def file_reader(folder: str = WORK_PATH, file_name: str = Any, mode: str = "r",
                skip: bool = False, content: bool = False, **kwargs) -> Union[CsvData, str]:
    """Reads a CSV file and returns a list comprehension of the data or reads a byte into strings."""
    file = path_builder(path=folder, file_name=file_name)
    if mode:
        with open(file, mode) as f:
            read = csv.reader(f, delimiter=",")
            if skip is True:
                next(read, None)
            if content is True:
                feed = f.read()
            load = [d for d in read]
            add_log(f"Read file {file_name}", "info")
            return load if content is False else feed


USER = Users()
PROJECT = Projects()
