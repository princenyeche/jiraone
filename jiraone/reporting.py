#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Example methods of Generating reports

Provided herein are Report Generator Classes and Methods,
Easily generate report for the various endpoints
"""
from typing import Any, List, Iterable, Tuple, Union, Dict, Optional
from collections import deque, namedtuple, OrderedDict
from jiraone import LOGIN, endpoint, add_log, WORK_PATH
import json
import csv
import sys
import os
import re


class Projects:
    """Get report on a Project based on user or user's attributes or groups."""

    @staticmethod
    def projects_accessible_by_users(*args: str, project_folder: str = "Project",
                                     project_file_name: str = "project_file.csv",
                                     user_extraction_file: str = "project_extract.csv",
                                     permission: str = "BROWSE", **kwargs) -> None:
        """
        Send an argument as String equal to a value, example: status=live.

        Multiple arguments separate by comma as the first argument in the function, all other arguments should
        be keyword args that follows. This API helps to generate full user accessibility to Projects on Jira.
        It checks the users access and commits the finding to a report file.

        You can tweak the permission argument with the options mention `here
        <https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-user-search>`_

        for endpoint /rest/api/3/user/permission/search

        :param args: A set of parameter arguments to supply

        :param project_folder: A folder

        :param project_file_name: A file to hold temp data

        :param user_extraction_file: A file to hold user temp data

        :param permission: A permission of Jira to check

        :param kwargs: Additional arguments

        .. _here:

        :return: None
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
                               **kwargs) -> None:
        """
        Retrieve the Dashboard Id/Name/owner and who it is shared with.

        The only requirement is that the user querying this API should have access to all
        the Dashboard available else it will only return dashboard where the user's view access is allowed.

        :param dashboard_folder: A folder

        :param dashboard_file_name: A file to store temp data

        :param kwargs: Additional arguments

        :return: None
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
                                   **kwargs) -> None:
        """
        Get the roles available in a project and which user is assigned to which
        role within the project.

        :param roles_folder: A folder

        :param roles_file_name: A file to store temp data

        :param user_extraction: Data extraction file holder

        :param kwargs: Addition argument

        :return: None
        """
        count_start_at = 0
        headers = ["Project Id ", "Project Key", "Project Name", "Project roles", "User AccountId", "User DisplayName",
                   "User role in Project"]
        file_writer(folder=roles_folder, file_name=roles_file_name, data=headers, **kwargs)

        # get extraction of projects data
        def role_on() -> None:
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
                    def get_user_role(user_data) -> None:
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
                        def pull_data() -> None:
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
                                    **kwargs) -> None:
        """Return all attachments of a Project or Projects

        Get the size of attachments on an Issue, count those attachments collectively and return the total number
        on all Projects searched. JQL is used as a means to search for the project.

        :param attachment_folder: A temp folder

        :param attachment_file_name: A filename for the attachment

        :param kwargs: Addition argument to supply.

        :return: None
        """
        attach_list = deque()
        count_start_at = 0
        headers = ["Project id", "Project key", "Project name", "Issue key", "Attachment size",
                   "Attachment type", "Name of file", "Created on by user", "Attachment url"]
        file_writer(folder=attachment_folder, file_name=attachment_file_name, data=headers, **kwargs)

        def pull_attachment_sequence() -> None:
            """
            Pulls the data and transform into given results.

            :return: None
            """
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

                                def pull_attachment() -> None:
                                    """
                                    Arranges extracts data
                                    :return: None
                                    """
                                    file_name = attach["filename"]  # name of the file
                                    created = attach["created"]  # datetime need to convert it
                                    attachment_size = attach["size"]  # in bytes, need to convert to mb
                                    mime_type = attach["mimeType"]
                                    attachment_url = attach["content"]

                                    calc_size = self.byte_converter(attachment_size)
                                    calc_date = self.date_converter(created)

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

        def re_write() -> None:
            """
            Rewrite and sort the extracted data
            :return: None
            """
            calc_made = self.grade_and_sort(attach_list, read_file)
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

        Therefore total = val / MB

        :param val: A value to supply

        :return: strings
        """
        byte_size = val
        mega_byte = 1000 * 1000
        visor = byte_size / mega_byte  # MB converter
        return "Size: {:.2f} MB".format(visor)

    @staticmethod
    def date_converter(val) -> str:
        """split the datetime value and output a string.

        :param val: A value to be supplied

        :return: string
        """
        get_date_time = val.split("T")
        get_am_pm = get_date_time[1].split(".")
        return f"Created on {get_date_time[0]} {get_am_pm[0]}"

    @staticmethod
    def grade_and_sort(attach_list, read_file) -> Union[float, int]:
        """
        Arranges and sorts the data.

        :param attach_list: A list of data

        :param read_file: A data set

        :return: A union of float and integers
        """
        for node in read_file:
            pattern = re.compile(r"(\d*?[0-9]\.[0-9]*)")
            if pattern is not None:
                if pattern.search(node[4]):
                    attach_list.append(pattern.search(node[4]).group())

        retain = [float(s) for s in attach_list]
        calc_sum = sum(retain)
        return calc_sum

    @staticmethod
    def bytes_converter(val) -> str:
        """Returns unit in KB or MB.

        1 Byte = 8 Bits.

        using megabyte MB, value is 1000^2

        mebibyte MiB, value is 1024^2

        Therefore total = val / MB

        :param val: An integer value

        :return: string

        """
        byte_size = val
        kilo_byte = 1000
        mega_byte = 1000 * 1000
        if byte_size > mega_byte:
            visor = byte_size / mega_byte  # MB converter
            unit = "MB"
        else:
            visor = byte_size / kilo_byte  # KB converter
            unit = "KB"
        return "Size: {:.2f} {}".format(visor, unit)

    @staticmethod
    def move_attachments_across_instances(attach_folder: str = "Attachment",
                                          attach_file: str = "attachment_file.csv",
                                          key: int = 3,
                                          attach: int = 8,
                                          file: int = 6,
                                          last_cell: bool = True,
                                          **kwargs) -> None:
        """Ability to post an attachment into another Instance.

        given the data is extracted from a csv file which contains the below information
         * Issue key
         * file name
         * attachment url

        we assume you're getting this from
        ``def get_attachments_on_project()``

        :param attach_folder: a folder or directory path

        :param attach_file: a file to a file name

        :param key: a row index of the column

        :param attach: a row index of the column

        :param file:  integers to specify the index of the columns

        :param last_cell: is a boolean determines if the last cell should be counted.
             e.g

              * key=3,

              * attach=6,

              * file=8

        the above example corresponds with the index if using the
         ``def get_attachments_on_project()`` otherwise, specify your value in each
         keyword args when calling the method.

         :return: None
        """
        read = file_reader(folder=attach_folder, file_name=attach_file, skip=True, **kwargs)
        add_log("Reading attachment {}".format(attach_file), "info")
        count = 0
        cols = read
        length = len(cols)
        for r in read:
            count += 1
            keys = r[key]
            attachment = r[attach]
            _file_name = r[file]
            fetch = LOGIN.get(attachment).content
            # use the file's keyword args to send multipart/form-data in the post request of LOGIN.post
            payload = {"file": (_file_name, fetch)}
            # modified our initial headers to accept X-Atlassian-Token to avoid (CSRF/XSRF)
            new_headers = {"Accept": "application/json",
                           "X-Atlassian-Token": "no-check"}
            LOGIN.headers = new_headers
            run = LOGIN.post(endpoint.issue_attachments(keys, query="attachments"), files=payload)
            if run.status_code != 200:
                print("Attachment not added to {}".format(keys), "Status code: {}".format(run.status_code))
                add_log("Attachment not added to {} due to {}".format(keys, run.reason), "error")
            else:
                print("Attachment added to {}".format(keys), "Status code: {}".format(run.status_code))
                add_log("Attachment added to {}".format(keys), "info")
            # remove the last column since if it contains empty cells.
            if last_cell is True:
                if count >= (length - 1):
                    break

    @staticmethod
    def download_attachments(file_folder: str = None, file_name: str = None,
                             download_path: str = "Downloads",
                             attach: int = 8,
                             file: int = 6,
                             **kwargs) -> None:
        """Download the attachments to your local device read from a csv file.

        we assume you're getting this from   ``def get_attachments_on_project()`` method.

        :param attach: integers to specify the index of the columns

        :param file_folder: a folder or directory where the file

        :param download_path: a directory where files are stored

        :param file: a row to the index of the column

        :param file_name: a file name to a file

                e.g
                  * attach=6,
                  * file=8

        the above example corresponds with the index if using the ``def get_attachments_on_project()``
        otherwise, specify your value in each keyword args when calling the method.

        :return: None
        """
        read = file_reader(folder=file_folder, file_name=file_name, **kwargs)
        add_log("Reading attachment {}".format(file_name), "info")
        count = 0
        cols = read
        length = len(cols)
        last_cell = kwargs["last_cell"] if "last_cell" in kwargs else False
        for r in read:
            count += 1
            attachment = r[attach]
            _file_name = r[file]
            fetch = LOGIN.get(attachment)
            file_writer(download_path, file_name=_file_name, mode="wb", content=fetch.content, mark="file")
            print("Attachment downloaded to {}".format(download_path), "Status code: {}".format(fetch.status_code))
            add_log("Attachment downloaded to {}".format(download_path), "info")
            if last_cell is True:
                if count >= (length - 1):
                    break

    @staticmethod
    def get_total_comments_on_issues(folder: str = "Comment", file_name: str = "comment_file.csv",
                                     **kwargs) -> None:
        """Return a report with the number of comments sent to or by a reporter (if any).

        This api will return comment count, the total comment sent by a reporter
        per issue and collectively sum up a total.
        It also shows how many comments other users sent on the issue.

        :param folder: The name of a folder

        :param file_name: The name of a file

        :param kwargs: additional argument to supply

        :return: None
        """
        comment_list = deque()
        pull = "active" if "pull" not in kwargs else kwargs["pull"]
        user_type = "atlassian" if "user_type" not in kwargs else kwargs["user_type"]
        file = "user_file.csv" if "file" not in kwargs else kwargs["file"]
        find_user = "test user" if "find_user" not in kwargs else kwargs["find_user"]
        duration = "startOfWeek(-1)" if "duration" not in kwargs else kwargs["duration"]
        status = None if "status" not in kwargs else kwargs["status"]
        get_user = ""
        headers = ["Project Id", "Project Key", "Project Name", "Issue Key", "Total Comment",
                   "Reporter accountId", "Display name of Reporter", "Comment by Reporter",
                   "Comment by others"]
        file_writer(folder, file_name, data=headers)
        USER.get_all_users(pull=pull,
                           user_type=user_type,
                           file=file, folder=folder)
        CheckUser = namedtuple("CheckUser", ["accountId", "account_type", "display_name", "active"])
        read = file_reader(folder=folder, file_name=file)
        for _ in read:
            f = CheckUser._make(_)
            if find_user in f._asdict().values():
                get_user = f.accountId
                print("User {} found - accountId: {}".format(find_user, get_user))

        if get_user == "":
            print("User: {}, not found exiting search...".format(find_user))
            sys.exit(1)
        search_issues = "reporter = {} AND updated <= {}".format(get_user, duration) if "status" not in kwargs \
                                                                                        or status is None \
            else "reporter = {} AND updated <= {} AND status in ({})".format(get_user, duration, status)
        print("Searching with JQL:", search_issues)
        count_start_at = 0

        def extract_issue() -> None:
            """Find the comment in each issue and count it.
            :return: None
            """
            comment_by_users = 0
            comment_by_others = 0
            for issues in result_data["issues"]:
                keys = issues["key"]
                get_issue_keys = LOGIN.get(endpoint.issues(issue_key_or_id=keys))
                if get_issue_keys.status_code == 200:
                    key_data = json.loads(get_issue_keys.content)
                    data = key_data["fields"]
                    if "project" or "comment" in data:
                        project_id = data["project"]["id"]
                        project_name = data["project"]["name"]
                        project_key = data["project"]["key"]
                        comments = data["comment"]
                        if comments is not None:
                            comment_total = comments["total"]
                            comment_self = comments["self"]
                            get_comment = LOGIN.get(comment_self)
                            if get_comment.status_code == 200:
                                comment_data = json.loads(get_comment.content)
                                reporter_name = ""
                                reporter_aid = ""
                                for comment in comment_data["comments"]:
                                    if "author" in comment:
                                        display_name = comment["author"]["displayName"]
                                        account_id = comment["author"]["accountId"]
                                        if account_id == get_user:
                                            reporter_name = display_name
                                            reporter_aid = account_id
                                            comment_by_users += 1
                                        if account_id != get_user:
                                            comment_by_others += 1

                                def pull_comments() -> None:
                                    """
                                    Pulls and arranges data
                                    :return: None
                                    """
                                    raw_dump = [project_id, project_key, project_name, keys,
                                                comment_total, reporter_aid, reporter_name,
                                                comment_by_users, comment_by_others]
                                    comment_list.append(raw_dump)

                                pull_comments()
                                comment_by_users = 0
                                comment_by_others = 0

            raw_data = [z for z in comment_list]
            file_writer(folder, file_name, data=raw_data, mark="many")
            comment_list.clear()

        while True:
            get_issues = LOGIN.get(endpoint.search_issues_jql(query=search_issues, start_at=count_start_at))
            if get_issues.status_code == 200:
                result_data = json.loads(get_issues.content)
                if count_start_at > result_data["total"]:
                    print("Issues extraction completed")
                    add_log("Issue extraction completed", "info")
                    break

                print("Extracting Issues...")
                extract_issue()

            count_start_at += 50

        def count_and_total() -> Tuple[int, int, int]:
            """
            Sorts and arranges the extracted data

            :return: A tuple of integers
            """
            for row in read_file:
                comment_list.append(row)

            wid_list = [int(s[4]) for s in comment_list]
            row_list = [int(s[7]) for s in comment_list]
            col_list = [int(s[8]) for s in comment_list]
            calc_list_zero = sum(wid_list)
            calc_list_one = sum(row_list)
            calc_list_two = sum(col_list)
            return calc_list_zero, calc_list_one, calc_list_two

        def write_result() -> None:
            """
            Sorts the result data

            :return: None
            """
            list_data = count_and_total()
            comment_list.clear()
            sorts = sorted(read_file, key=lambda rows: rows[3], reverse=False)
            for c in sorts:
                _project_id = c[0]
                _project_key = c[1]
                _project_name = c[2]
                _issue_key = c[3]
                _comment_total = c[4]
                _get_user = c[5]
                _reporter_name = c[6]
                _comm_by_reporter = c[7]
                _comm_by_others = c[8]

                raw_data_file = [_project_id, _project_key, _project_name, _issue_key, _comment_total,
                                 _get_user, _reporter_name, _comm_by_reporter, _comm_by_others]
                file_writer(folder, file_name, data=raw_data_file)

            # arranging the file last row
            raw_data_file = ["", "", "", "", "Total comments: {}".format(list_data[0]),
                             "", "", "Total comments by Reporter: {}".format(list_data[1]),
                             "Total comments by others: {}".format(list_data[2])]
            file_writer(folder, file_name, data=raw_data_file)

        read_file = file_reader(folder, file_name, skip=True)
        file_writer(folder, file_name, mode="w", data=headers)
        write_result()

        print("File extraction for comments completed. Your file is located at {}".format(path_builder
                                                                                          (path=folder,
                                                                                           file_name=file_name)))
        add_log("File extraction for comments completed", "info")

    @staticmethod
    def change_log(folder: str = "ChangeLog", file: str = "change_log.csv",
                   back_up: bool = False,
                   allow_cp: bool = True,
                   **kwargs: Union[str, bool]) -> None:
        """Extract the issue history of an issue.

        Query the changelog endpoint if using cloud instance or straight away define access to it on server.
        Extract the histories and export it to a CSV file.

        :param folder:  A name of a folder datatype String

        :param file:  A name of a file datatype String

        :param back_up: A boolean to check whether a history file is exist or not.

        :param allow_cp: Allow or deny the ability to have a checkpoint.

        :param kwargs: The other kwargs that can be passed as below.

               * jql: (required) A valid JQL query for projects or issues.  datatype -> string

               * saved_file: The name of the file which saves the iteration. datatype -> string

               * show_output: Show a printable output on terminal. datatype -> boolean

               * field_name: Target a field name to render. datatype -> string

        :return: None
        """
        from jiraone.exceptions import JiraOneErrors
        if LOGIN.get(endpoint.myself()).status_code > 300:
            raise JiraOneErrors("login", "Authentication failed. Please check your credentials.")
        changes = deque()
        item_list = deque()
        jql: str = kwargs["jql"] if "jql" in kwargs else exit("A JQL query is required.")
        saved_file: str = "iter_saves.json" if "saved_file" not in kwargs else kwargs["saved_file"]
        field_name = kwargs["field_name"] if "field_name" in kwargs else None
        show_output: bool = False if "show_output" in kwargs else True
        print("Extracting issue histories...")
        add_log("Extracting issue histories...", "info")
        # Indicates the first iteration in the main loop sequence.
        attempt: int = 1
        _fix_status_: bool = True if "fix" in kwargs else False

        def blank_data(key_val: str, sums: str, item_val: Any, name_: str) -> None:
            """
            Write the created date of an issue to a file.
            This is used for ``time_in_status()`` to accurately calculate the difference in status time.

            :param key_val: An issue key

            :param sums: A summary of an issue

            :param item_val: An dictionary of values

            :param name_: displayName of the user

            :return: None
            """
            nonlocal attempt

            if _fix_status_ is True and attempt == 1:
                create = LOGIN.get(endpoint.issues(key_val))
                if create.status_code < 300:
                    adjust = create.json().get("fields").get("created")
                    raw_ = [key_val, sums, name_, adjust, "", item_val.field,
                            item_val.from_, item_val.fromString, item_val.to, item_val.toString] if LOGIN.api is \
                                                                                                    False else [
                        key_val, sums, name_, adjust, "", item_val.field,
                        item_val.field_id, item_val.from_, item_val.fromString, item_val.to, item_val.toString,
                        item_val.tmpFromAccountId, item_val.tmpToAccountId]
                    file_writer(folder, file, data=raw_, mode="a+")
                    attempt += 2

        def changelog_search() -> None:
            """Search the change history endpoint and extract data if existed.
            :return: None
            """
            nonlocal loop, attempt
            infinity_counter = count if back_up is False else data_brick["iter"]
            for issue in data["issues"]:
                keys = issue["key"]
                attempt = 1

                def re_instantiate(val: str) -> None:
                    """
                    Evaluate the issue key to run
                    :param val: An issue key variable
                    :return: None
                    """
                    nonlocal attempt
                    # reach the changelog endpoint and extract the data of history for servers.
                    # https://docs.atlassian.com/software/jira/docs/api/REST/7.13.11/#api/2/issue-getIssue
                    get_issue_keys = LOGIN.get(endpoint.issues(issue_key_or_id=val,
                                                               query="expand=renderedFields,names,schema,operations,"
                                                                     "editmeta,changelog,versionedRepresentations"))
                    if get_issue_keys.status_code == 200:
                        key_data = json.loads(get_issue_keys.content)
                        # Bug Fix to "Extraction Of Jira History Error #47" return value of None in some issue keys.
                        # https://github.com/princenyeche/atlassian-cloud-api/issues/47
                        load_summary = LOGIN.get(endpoint.issues(issue_key_or_id=val))
                        _summary = None
                        if load_summary.status_code < 300:
                            _summary = json.loads(load_summary.content).get('fields').get('summary')
                        if LOGIN.api is False:
                            if "changelog" in key_data:
                                _data = key_data["changelog"]
                                # grab the change_histories on an issue
                                print(f"Getting history from issue: {val}")
                                add_log(f"Getting history from issue: {val}", "info")
                                changelog_history(_data, proj=(val, project_key, _summary))
                                print("*" * 100)
                        else:
                            starter = 0
                            while True:
                                key_data = LOGIN.get(endpoint.issues(issue_key_or_id=val,
                                                                     query="changelog?startAt={}".format(starter),
                                                                     event=True))
                                loads = json.loads(key_data.content)
                                if starter >= loads["total"]:
                                    break
                                print(f"Getting history from issue: {val}")
                                add_log(f"Getting history from issue: {val}", "info")
                                changelog_history(loads, proj=(val, project_key, _summary))
                                print("*" * 100)
                                starter += 100

                infinity_counter += 1
                data_brick.update({"iter": infinity_counter, "key": keys})
                project_key = keys.split("-")[0]
                json.dump(data_brick, open(f"{path_builder(path=folder, file_name=saved_file)}",
                                           encoding='utf-8', mode='w+'), indent=4) if allow_cp is True else None
                if back_up is True and keys != set_up["key"] and loop is False:
                    re_instantiate(set_up["key"])

                loop = True
                re_instantiate(keys)

        def changelog_history(history: Any = Any, proj: tuple = (str, str, str)) -> None:
            """Structure the change history data after being retrieved.

            :return: None
            """
            _keys = proj[0]
            _summary = proj[2]

            def render_history(past):
                created = ""
                name = ""
                if "author" in past:
                    name = past["author"]["name"] if "name" in past["author"] else past["author"]["displayName"]
                if "created" in past:
                    created = past["created"]
                if "items" in past:
                    items = past["items"]
                    for item in items:
                        _field_id = ""
                        _tmpFromAccountId = ""
                        _tmpToAccountId = ""
                        if LOGIN.api is False:
                            _field_id = item.get("fieldId")
                            _tmpFromAccountId = item.get("tmpFromAccountId")
                            _tmpToAccountId = item.get("tmpToAccountId")
                        _field = item.get("field")
                        _field_type = item.get("fieldtype")
                        _from = item.get("from")
                        _fromString = item.get("fromString")
                        _to = item.get("to")
                        _toString = item.get("toString")
                        if field_name == _field:
                            raw = [_field, _field_type, _from, _fromString, _to, _toString] if LOGIN.api is False \
                                else [_field, _field_type, _field_id, _from, _fromString, _to, _toString,
                                      _tmpFromAccountId, _tmpToAccountId]
                            item_list.append(raw)
                        elif field_name is None:
                            raw = [_field, _field_type, _from, _fromString, _to, _toString] if LOGIN.api is False \
                                else [_field, _field_type, _field_id, _from, _fromString, _to, _toString,
                                      _tmpFromAccountId, _tmpToAccountId]
                            item_list.append(raw)

                        ItemList = namedtuple("ItemList", ["field", "field_type", "from_", "fromString",
                                                           "to", "toString"]) if LOGIN.api is False else \
                            namedtuple("ItemList", ["field", "field_type", "field_id", "from_", "fromString",
                                                    "to", "toString", "tmpFromAccountId", "tmpToAccountId"])

                        for _ in item_list:
                            issue = ItemList._make(_)
                            # Fix for time in status
                            blank_data(_keys, _summary, issue, name)
                            raw_vision = [_keys, _summary, name, created, issue.field_type, issue.field,
                                          issue.from_, issue.fromString, issue.to, issue.toString] if LOGIN.api is \
                                                                                                      False else [
                                _keys, _summary, name, created, issue.field_type, issue.field,
                                issue.field_id, issue.from_, issue.fromString, issue.to, issue.toString,
                                issue.tmpFromAccountId, issue.tmpToAccountId]
                            changes.append(raw_vision)
                        item_list.clear()

                for case in changes:
                    file_writer(folder, file, data=case, mode="a+")
                changes.clear()
                add_log(f"Clearing history from queue: {_keys}", "info")

            if "histories" in history:
                for change in history["histories"]:
                    render_history(change)
            else:
                if "values" in history:
                    if history["values"] is not None:
                        for change in history["values"]:
                            render_history(change)

        count = 0  # get a counter of the issue record
        headers = ["Issue Key", "Summary", "Author", "Created", "Field Type",
                   "Field", "From", "From String", "To", "To String"] if LOGIN.api is False else \
            ["Issue Key", "Summary", "Author", "Created", "Field Type",
             "Field", "Field Id", "From", "From String", "To", "To String", "From AccountId", "To AccountId"]
        cycle: int = 0
        # stores our iteration here
        data_brick = {}
        set_up = None
        loop: bool = False
        if allow_cp is True:
            if os.path.isfile(path_builder(folder, file_name=saved_file)) and \
                    os.stat(path_builder(folder, file_name=saved_file)).st_size != 0:
                user_input = input("An existing save point exist from your last extraction, "
                                   "do you want to use it? (Y/N) \n")
                set_up = json.load(open(path_builder(path=folder, file_name=saved_file)))
                if user_input.lower() in ["y", "yes"]:
                    back_up = True
                else:
                    print("Starting extraction from scratch.")
                    set_up = None
        os.open(path_builder(path=folder, file_name=saved_file), flags=os.O_CREAT) if allow_cp is True else None
        file_writer(folder=folder, file_name=file, data=headers, mode="w+") if set_up is None else None
        depth = 1
        while True:
            load = LOGIN.get(endpoint.search_issues_jql(query=set_up["jql"], start_at=set_up["iter"],
                                                        max_results=100)) if back_up is True and depth == 1 else \
                LOGIN.get(endpoint.search_issues_jql(query=jql, start_at=count, max_results=100))
            if load.status_code == 200:
                data = json.loads(load.content)
                cycle = 0
                data_brick.update({
                    "jql": jql,
                    "iter": set_up["iter"] if back_up is True and depth == 1 else count,
                    "save": set_up["save"] if back_up is True and depth == 1 else attempt
                })
                if count > data["total"]:
                    break
                changelog_search()
                depth += 1
            count += 100
            if depth == 2 and back_up is True:
                count = data_brick["iter"]
            if load.status_code > 300:
                cycle += 1
                if cycle > 99:
                    raise JiraOneErrors("value", "It seems that the search \"{}\" cannot be "
                                                 "retrieved as we've attempted it {} times".format(jql, cycle))

        if show_output is True:
            print("A CSV file has been written to disk, find it here {}".format(
                path_builder(folder, file_name=file)))
        add_log("File extraction for change log completed", "info")
        os.remove(path_builder(path=folder, file_name=saved_file)) if allow_cp is True else None

    def comment_on(self, key_or_id: str = None, comment_id: int = None, method: str = "GET", **kwargs) -> Any:
        """Comment on a ticket or write on a description field.

        :request GET: comments

        :request POST: comments by id

        :request PUT: update a comment

        :request POST: add a comment

        :request DELETE: delete a comment

        Do the same thing you do via the UI.

        :return: Any
        """
        result_data = deque()
        start_at = kwargs["start_at"] if "start_at" in kwargs else 0
        max_results = kwargs["max_results"] if "max_results" in kwargs else 50
        event = kwargs["event"] if "event" in kwargs else False
        query = kwargs["query"] if "query" in kwargs else None
        mention = kwargs["mention"] if "mention" in kwargs else None
        text_block = kwargs["text_block"] if "text_block" in kwargs else None
        placer = kwargs["placer"] if "placer" in kwargs else None
        visible = kwargs["visible"] if "visible" in kwargs else None
        if method.upper() == "GET":
            load = LOGIN.get(endpoint.comment(key_or_id=key_or_id, ids=comment_id,
                                              start_at=start_at, max_results=max_results,
                                              event=event, query=query))
            data = load.json()

            class ReturnCommentData:
                """Get a list of the data in one chunk."""

                def __init__(self, results) -> None:
                    """Get all data from a comment field.

                This calls the comment endpoint and returns a list of the data.
                Depending on what method you're calling. It is either you call the
                method ``comment()`` or you call a property within the method.

                .. code-block:: python

                    iss_key = "COM-42"
                    get_com = comment(iss_key).comment("body").result
                    echo(get_com)
                    # This will return the data of the body content

                OR
                .. code-block:: python

                    iss_key = "COM-42"
                    get_com = comment(iss_key).data
                    echo(get_com)
                    # This will simply return the comment endpoint data

                @properties that can be called

                i) body - returns the body content of the comment.
                ii) mention - returns the users mentioned on a comment.
                iii) text - returns an array of strings of the text in the comment.
                iv) author - returns the author who triggered the comment.

                .. code-block:: python

                    iss_key = "COM-42"
                    get_com = comment(iss_key).comment("body").text
                    echo(get_com)
                    # This will simply return the comment text separated by comma

                :param results: A dict object that loads the result of comments.

                """
                    self.data = results
                    self._author = None
                    self._body = None
                    self._update_author = None
                    self._other_fields = None

                def comment(self, type_field: str) -> Any:
                    """Return a comment field data.

                    :param type_field: A string used to determine which data to pull

                    options available

                     i) author - the user which triggered the comment
                     ii) body - a comment body
                     iii) updateAuthor - gets the updated author details
                    """
                    for f in self.data["comments"]:
                        if type_field in f:
                            if type_field == "author":
                                self._author = f.get("author")
                                self._other_fields = {"created": f.get("created"), "id": f.get("id"),
                                                      "jsdPublic": f.get("jsdPublic"), "self": f.get("self"),
                                                      "updated": f.get("updated")}
                                result_data.append({"author": self._author, "fieldset": self._other_fields})

                            if type_field == "body":
                                self._body = f.get("body")
                                self._other_fields = {"created": f.get("created"), "id": f.get("id"),
                                                      "jsdPublic": f.get("jsdPublic"), "self": f.get("self"),
                                                      "updated": f.get("updated")}
                                result_data.append({"body": self._body, "fieldset": self._other_fields})

                            if type_field == "updateAuthor":
                                self._update_author = f.get("updateAuthor")
                                self._other_fields = {"created": f.get("created"), "id": f.get("id"),
                                                      "jsdPublic": f.get("jsdPublic"), "self": f.get("self"),
                                                      "updated": f.get("updated")}
                                result_data.append(
                                    {"updateAuthor": self._update_author, "fieldset": self._other_fields})

                    class Text:
                        """Return the text of data."""
                        pull = deque()

                        def __init__(self):
                            """Return the data value when a property is used."""
                            self.result = result_data
                            self._body_ = None
                            self._author_ = None
                            self._text_ = None
                            self._mention_ = None
                            for d in self.result:
                                if "author" in d:
                                    if self._author_ is None:
                                        self.author = [{"author": j["author"]["displayName"],
                                                        "accountId": j["author"]["accountId"],
                                                        "active": j["author"]["active"],
                                                        "accountType": j["author"]["accountType"]} for j in
                                                       self.result]
                                if "body" in d:
                                    if self._body_ is None:
                                        self.body = [j.get("body") for j in self.result]
                                        first_comm, *_, last_comm = self.body
                                        self.last_comment = last_comm
                                        self.first_comment = first_comm

                        @property
                        def author(self):
                            """Property of author field.

                            Returns some data set of the author, extracted from the comment.
                            """
                            return self._author_

                        @author.setter
                        def author(self, user):
                            """Sets the author field of an object with the dataset."""
                            self._author_ = user

                        @property
                        def body(self):
                            """Property of body field.

                            Returns some data set of the body, extracted from the comment.
                            """
                            return self._body_

                        @body.setter
                        def body(self, content):
                            """Sets the body field of an object with the dataset."""
                            self._body_ = content
                            for enter in self._body_:
                                if "content" in enter:
                                    for context in enter["content"]:
                                        if "content" in context:
                                            for value in context["content"]:
                                                if self._text_ is None:
                                                    if "text" in value:
                                                        if value["type"] == "mention":
                                                            self.pull.append({"mention": value["attrs"],
                                                                              "type": value["type"],
                                                                              "text_type": value["text"]})
                                                        self.pull.append({"text": value["text"], "type": value["type"]})

                                                if self._mention_ is None:
                                                    if "type" in value:
                                                        if value["type"] == "mention":
                                                            self.pull.append({"mention": value["attrs"],
                                                                              "type": value["type"]})
                            # will only show value on API v3.
                            self.text = [OrderedDict({"text": a.get("text"), "type": a.get("type")})
                                         for a in self.pull if "text" in a]
                            # will only show value on API v3.
                            self.mention = [OrderedDict({"mention": a.get("mention"),
                                                         "type": a.get("type")}) for a in self.pull if "mention" in a]

                        @property
                        def text(self):
                            """Property of text field.

                            Returns some data set of the body text, extracted from the comment.
                            """
                            return self._text_

                        @text.setter
                        def text(self, content):
                            """Sets the text field of a body comment with the dataset."""
                            self._text_ = content

                        @property
                        def mention(self):
                            """Property of mention field.

                            Returns some data set of the body @mention of a user, extracted from the comment.
                            """
                            return self._mention_

                        @mention.setter
                        def mention(self, content):
                            """Sets the text field of a body comment with @mention user with the dataset."""
                            self._mention_ = content

                    comm = Text()
                    return comm

            row = ReturnCommentData(data)
            return row

        if method.upper() == "POST":
            block = [text_block]
            text = None
            if block is not None:
                if len(mention) > 0:
                    text = replacement_placeholder(placer, block, mention, 0)
            # change REST endpoint from 3 to latest, so we can easily post a comment.
            LOGIN.api = kwargs["api"] if "api" in kwargs else False
            body_content = {
                "body": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "text": text[0],
                                    "type": "text"
                                }

                            ]
                        }
                    ]
                }
            }
            field_text = {
                "body": text[0]
            } if visible is None and LOGIN.api is False else body_content if visible is None and LOGIN.api is True \
                else {
                "visibility": {
                    "type": "role",
                    "value": visible
                },
                "body": text[0]
            }
            result = LOGIN.post(endpoint.comment(key_or_id=key_or_id, event=event), payload=field_text)
            if result.status_code < 300:
                print("Comment added to {}".format(key_or_id))
            else:
                print("Comment not added to {}, error: {}".format(key_or_id, result.status_code))
            block.clear()


class Users:
    """
    This class helps to Generate the No of Users on Jira Cloud

    You can customize it to determine which user you're looking for.

    * It's method such as ``get_all_users`` displays active or inactive users, so you'll be getting all users

    """
    user_list = deque()

    def get_all_users(self, pull: str = "both", user_type: str = "atlassian",
                      file: str = None, folder: str = Any, **kwargs) -> Any:
        """Generates a list of users.

        :param pull: (options) for the argument

            * both: pulls out inactive and active users

            * active: pulls out only active users

            * inactive: pulls out inactive users

       :param user_type: (options) for the argument

            * atlassian: a normal Jira Cloud user

            * customer: this will be your JSM customers

            * app: this will be the bot users for any Cloud App

            * unknown: as the name suggest unknown user type probably from oAuth

       :param file: String of the filename

       :param folder: String of the folder name

       :param kwargs: Additional keyword argument for the method.

        :return: Any
        """
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
            self.report(category=folder, filename=file, **kwargs)

    def report(self, category: str = Any, filename: str = "users_report.csv", **kwargs) -> None:
        """Creates a user report file in CSV format.
        :return: None
        """
        read = [d for d in self.user_list]
        file_writer(folder=category, file_name=filename, data=read, mark="many", **kwargs)
        add_log(f"Generating report file on {filename}", "info")

    def user_activity(self, status: str = Any, account_type: str = Any, results: List = Any) -> Any:
        """Determines users activity.

        :return: None
        """

        # get both active and inactive users
        def stack(c: Any, f: List, s: Any) -> Any:
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
                            user_extraction_file: str = "group_extraction.csv", **kwargs) -> None:
        """Get all users and the groups associated to them on the Instance.
        :return: None
        """
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

    def search_user(self, find_user: Union[str, list] = None,
                    folder: str = "Users", **kwargs) -> Union[deque, int]:
        """Get a list of all cloud users and search for them by using the displayName.

        :param find_user: A list of user's displayName or a string of the displayName

        :param folder: A name to the folder

        :param kwargs: Additional arguments

                   *options*
                   skip (bool) - allows you to skip the header of ``file_reader``
                   delimiter (str) - allows a delimiter to the ``file_reader`` function
                   pull (str) - determines which user is available e.g. "active", "inactive"
                   user_type (str) - searches for user type
                   file (str) - Name of the file

        """
        pull = kwargs["pull"] if "pull" in kwargs else "both"
        user_type = kwargs["user_type"] if "user_type" in kwargs else "atlassian"
        file = kwargs["file"] if "file" in kwargs else "user_file.csv"
        build = path_builder(folder, file)

        if not os.path.isfile(build):
            open(build, mode="a").close()

        def get_users():
            if os.stat(build).st_size != 0:
                print(f"The file \"{file}\" exist...", end="")
                os.remove(build)
                print("Updating extracted user...\n", end="")
                self.get_all_users(pull=pull, user_type=user_type, file=file, folder=folder)
            else:
                print("Extracting users...")
                self.get_all_users(pull=pull, user_type=user_type, file=file, folder=folder)

        if len(self.user_list) == 0:
            get_users()
        CheckUser = namedtuple("CheckUser", ["accountId", "account_type", "display_name", "active"])
        list_user = file_reader(file_name=file, folder=folder, **kwargs)
        checker = []
        for _ in list_user:
            f = CheckUser._make(_)
            if isinstance(find_user, str):
                if find_user in f._asdict().values():
                    get_user = f.accountId
                    display_name = f.display_name
                    status = f.active
                    checker.append(OrderedDict({"accountId": get_user,
                                                "displayName": display_name, "active": status}))
            if isinstance(find_user, list):
                for i in find_user:
                    if i in f._asdict().values():
                        get_user = f.accountId
                        display_name = f.display_name
                        status = f.active
                        checker.append(OrderedDict({"accountId": get_user,
                                                    "displayName": display_name, "active": status}))

        return checker if len(checker) != 0 else 0

    def mention_user(self, name) -> List[str]:
        """Return a format that you can use to mention users on cloud.
        :param name: The name of a user.

        :return: List[str]
        """
        data = []
        if "," in name:
            s = name.split(",")
        else:
            s = name
        for u in self.search_user(s):
            data.append(f"[~accountId:{u.get('accountId')}]")

        return data


def path_builder(path: str = "Report", file_name: str = Any, **kwargs) -> str:
    """Builds a dir path and file path in a directory.

    :param path: A path to declare absolute to where the script is executed.

    :param file_name: The name of the file being created

    :return: A string of the directory path or file path
    """
    base_dir = os.path.join(WORK_PATH, path)
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
        add_log(f"Building Path {path}", "info")
    base_file = os.path.join(base_dir, file_name)
    return base_file


def file_writer(folder: str = WORK_PATH, file_name: str = None, data: Iterable = object,
                mark: str = "single", mode: str = "a+", content: str = None, **kwargs) -> Any:
    """Reads and writes to a file, single or multiple rows or write as byte files.

    :param folder: A path to the name of the folder

    :param file_name: The name of the file being created.

    :param data: Iterable - an iterable data, usually in form of a list.

    :param mark:  Helps evaluates how data is created, available options [“single”, “many”, “file”],
              by default mark is set to “single”

    :param mode: File mode, available options [“a”, “w”, “a+”, “w+”, “wb”],
                   by default the mode is set to “a+”.

    :param content: string - outputs the file in bytes.

    :param kwargs: Additional parameters

               *options*

               delimiter: defaults to comma - datatype (strings)

               encoding: defaults to utf-8 - datatype (strings)

    .. versionchanged:: 0.6.3

    encoding - added keyword argument encoding to handle encoding issues on Windows
    like device.

    :return: Any
    """
    from platform import system
    delimiter = kwargs["delimiter"] if "delimiter" in kwargs else ","
    file = path_builder(path=folder, file_name=file_name)
    encoding = kwargs["encoding"] if "encoding" in kwargs else "utf-8"
    # Bug:fix:JIR-8 on https://github.com/princenyeche/jiraone/issues/89
    windows = open(file, mode, encoding=encoding, newline="") \
        if system() == "Windows" and mark != "file" else open(file, mode)
    if mode:
        with windows as f:
            write = csv.writer(f, delimiter=delimiter)
            if mark == "single":
                write.writerow(data)
            if mark == "many":
                write.writerows(data)
            if mark == "file":
                f.write(content)
            add_log(f"Writing to file {file_name}", "info")


def file_reader(folder: str = WORK_PATH, file_name: str = None, mode: str = "r",
                skip: bool = False, content: bool = False, **kwargs) -> Union[List[List[str]], str]:
    """Reads a CSV file and returns a list comprehension of the data or reads a byte into strings.

    :param folder: string - a path to the name of the folder

    :param file_name: string - the name of the file being created

    :param mode: string - file mode, available options [“r”, “rb”]

    :param skip: bool - True allows you to skip the header if the file has any. Otherwise, defaults to False

    :param content: bool - True allows you to read a byte file. By default, it is set to False

    :param kwargs: Additional parameters

              *options*

              encoding - standard encoding strings. e.g “utf-8”.

              delimiter: defaults to comma.


    :return: A list comprehension data or binary data
    """
    from platform import system
    file = path_builder(path=folder, file_name=file_name)
    encoding = kwargs["encoding"] if "encoding" in kwargs else "utf-8"
    delimiter = kwargs["delimiter"] if "delimiter" in kwargs else ","
    windows = open(file, mode, encoding=encoding, newline="") \
        if system() == "Windows" and content is False else open(file, mode)
    if mode:
        with windows as f:
            read = csv.reader(f, delimiter=delimiter)
            if skip is True:
                next(read, None)
            if content is True:
                feed = f.read() if "encoding" not in kwargs else f.read().encode(encoding)
            load = [d for d in read]
            add_log(f"Read file {file_name}", "info")
            return load if content is False else feed


def replacement_placeholder(string: str = None, data: List = None,
                            iterable: List = None,
                            row: int = 2) -> Any:
    """Return multiple string replacement.

    :param string:  A string that needs to be checked

    :param data:  A list of strings with one row in the string being checked.

    :param iterable: An iterable data that needs to be replaced with.

    :param row: An indicator of the column to check.

    .. code-block:: python

      # previous statement
      hold = ["Hello", "John doe", "Post mortem"]
      text = ["<name> <name>, welcome to the <name> of what is to come"]
      cb = replacement_placeholder("<name>", text, hold, 0)
      print(cb)

    """
    result = None
    count = 0
    length = len(iterable)
    for _ in iterable:
        if count == 0:
            if string in data[row]:
                result = [lines.replace(string, iterable[count], 1) for lines in data]
        if count > 0:
            if string in result[row]:
                result = [lines.replace(string, iterable[count], 1) for lines in result]
        count += 1
        if count > length:
            break
    return result


def delete_attachments(
        file: Optional[str] = None,
        search: Union[str, Dict, List, int] = None,
        delete: bool = True,
        extension: Union[str, List] = None,
        by_user: Optional[List] = None,
        by_size: Optional[str] = None,
        by_date: Optional[str] = None,
        **kwargs: Union[str, bool]
) -> None:
    """
    A function that helps to delete attachments on Jira issues. You can export a JQL search of issues
    containing the ``Attachment`` column either in CSV or xlsx from your advanced filter search,
    or you can search using a JQL search query to delete attachments.

    .. code-block:: python

       from jiraone LOGIN, delete_attachments
       import json

       config = json.load(open('config.json'))
       LOGIN(**config)

       delete_attachments(file="data_file.csv")

    .. code-block:: python

       from jiraone LOGIN, delete_attachments
       import json

       config = json.load(open('config.json'))
       LOGIN(**config)

       jql = "project in (CT) ORDER BY Rank DESC"
       # search for only these file extensions and delete them
       ext = ["png", "zip", "pdf"]
       # search for attachments done by these users. Please use accountId only
       users = ["557058:5bcedf04-xxxx-4c40-b707-xxxxxd8bd8d", "5bcedf04-XXXXXX"]
       delete_attachments(search=jql, extension=ext, by_user=users)

    :param file: A file export of issues from Jira which includes the ``attachment columns``

    :param search: A search parameter for issues e.g. issue key or JQL query

    :param extension: A file extension to focus on while deleting.

    :param by_user: Search by user accountId and delete attachments. You can also combine the extension parameter.
                    This will only work when using the ``search`` parameter.

    :param by_size: Search by allocated file size and delete the attachment. You can combine the extension and by_user
                    parameter with this argument.


    :param by_date: Search by date_range from when the attachment was created until the initiator's current time.
                    Then delete the attachment. You can combine this argument with all
                    other arguments provided with the search parameter.

    :param delete: A decision to delete or not delete the attachments. defaults to ``True``

    :param kwargs: Additional arguments

                 *Available options*

                 * allow_cp: Allows the ability to trigger and save a checkpoint.

                 * saved_file: Provides a generic name for the checkpoint save file.

                 * delimiter: Allows you to change the delimiter used to read the file used by ``file`` parameter.

    :return: None
    """
    from jiraone.exceptions import JiraOneErrors
    from datetime import datetime, timedelta
    if LOGIN.get(endpoint.myself()).status_code > 300:
        add_log("Authentication failed. Please check your credential data to determine what went wrong.", "error")
        raise JiraOneErrors("login", "Authentication failed. Please check your credentials.")
    search_path = None
    folder: str = "DATA"
    allow_cp: bool = True if "allow_cp" not in kwargs else False
    saved_file: str = "data_block.json" if "saved_file" not in kwargs else kwargs["saved_file"]
    back_up: bool = False
    attach_load = []
    data_file = path_builder(folder, file_name=saved_file)

    def time_share(_time: str, _items=None) -> bool:
        """
        Calculate the time difference it takes with the date and now to determine if deletion is possible.

        :param _time: A string of date range to check

        :param _items: An iterable of available date of attachment creation.

        :return: True or False
        """
        minutes = 1  # defaults to minute
        hours = 1  # defaults to hour
        # defaults to days
        days = 1
        weeks = 7
        months = 30
        years = 365
        selection = None
        time_factor = {}
        time_hold_one = {"minute": minutes, "hour": hours, "day": days,
                         "week": weeks, "month": months, "year": years}
        time_factors = {}
        time_hold_two = {"minutes": minutes, "hours": hours, "days": days,
                         "weeks": weeks, "months": months, "years": years}

        times = []
        if isinstance(_time, str):
            number = re.compile(r"(?:\d+)")
            string_one = re.compile(r"(?:[a-zA-Z]{4,7})")
            if number.search(_time) is not None:
                times.append(number.search(_time).group())
            if string_one.search(_time) is not None:
                times.append(string_one.search(_time).group())
        else:
            add_log("Invalid time parameter received. Expected a string but got \"{}\"".format(type(_time)), "debug")
            raise JiraOneErrors("wrong", "Invalid time parameter received. Expected a string but got \"{}\""
                                .format(type(_time)))

        if times[1]:
            if times[1] in time_hold_one:
                time_factor = time_hold_one
                selection = "time_factor"
            elif times[1] in time_hold_two:
                time_factors = time_hold_two
                selection = "time_factors"
            else:
                add_log("Invalid option \"{}\" detected as `time_info` for \"by_date\" argument".format(by_date),
                        "error")
                raise JiraOneErrors("value", "We're unable to determine your precise date range with \"{}\""
                                    .format(by_date))

        def time_delta(val: int, cet: str) -> tuple:
            """
            Return a tuple to determine what the expected datetime are.

            :param val: An integer of the datetime.

            :param cet: A string denoting the name to time.

            :return: A tuple of probably time factor.
            """
            _time_ = None
            time_check_ = time_factor if selection == "time_factor" else time_factors
            if cet in time_check_:
                _time_ = val * time_check_[cet]
            return _time_, list(time_check_.keys())[list(time_check_.keys()).index(cet)]

        if len(times) > 0:
            issue_time = datetime.strptime(_items.get("created"), "%Y-%m-%dT%H:%M:%S.%f%z")
            present = datetime.strftime(datetime.astimezone(datetime.now()), "%Y-%m-%dT%H:%M:%S.%f%z")
            parse_present = datetime.strptime(present, "%Y-%m-%dT%H:%M:%S.%f%z")
            time_check = time_factor if selection == "time_factor" else time_factors
            if times[1] in time_check:
                ask_time = time_delta(int(times[0]), times[1])
                d_range = ["days", "months", "years", "weeks"] if selection == "time_factors" else \
                    ["day", "month", "year", "week"]
                d_min = "minute" if selection == "time_factor" else "minutes"
                past_time = timedelta(days=ask_time[0]) if ask_time[1] in d_range else \
                    timedelta(minutes=ask_time[0]) if ask_time[1] == d_min \
                        else timedelta(hours=ask_time[0])
                diff = parse_present - past_time
                if diff < issue_time:
                    return True
        return False

    def regulator(size: str, block=None) -> bool:
        """
        Determine the size of an attachment.

        :param size: The size in byte of an attachment.

        :param block: An iterable that contains the attachment data

        :return: Returns a boolean output to determine if an attachment is greater or lesser than size parameter.
        """
        chars = []
        giga_byte = 1000 * 1000 * 1000
        mega_byte = 1000 * 1000
        kilo_byte = 1000
        if isinstance(size, str):
            sign = re.compile(r"(?:[\<|\>])")
            number = re.compile(r"(?:\d+)")
            string_ = re.compile(r"(?:[a-zA-Z]{2})")
            if sign.search(size) is not None:
                chars.append(sign.search(size).group())
            if number.search(size) is not None:
                chars.append(number.search(size).group())
            if string_.search(size) is not None:
                chars.append(string_.search(size).group())
            else:
                chars.append("")
        else:
            add_log("Invalid size parameter received. Expected a string but got \"{}\"".format(type(size)), "debug")
            raise JiraOneErrors("wrong", "Invalid size parameter received. Expected a string but got \"{}\""
                                .format(type(size)))

        if len(chars) > 0:
            symbol = chars[0]
            my_num = int(chars[1])
            this = chars[2].lower()
            if this in ["mb", "kb", "gb"]:
                byte_size = my_num * mega_byte if this == "mb" else my_num * giga_byte \
                    if this == "gb" else my_num * kilo_byte if this == "kb" else my_num
                if symbol == ">":
                    if block.get("size") > byte_size:
                        return True
                elif symbol == "<":
                    if block.get("size") < byte_size:
                        return True
            else:
                byte_size = my_num
                if symbol == ">":
                    if block.get("size") > byte_size:
                        return True
                elif symbol == "<":
                    if block.get("size") < byte_size:
                        return True
        return False

    def get_ext(ex) -> Union[str, List]:
        """
        Determine the extension and cycle through it.

        :param ex: An extension checker

        :return: A string or a list item
        """
        if isinstance(ex, str):
            if "," in ex:
                ex = ex.lower().split(",")
                return ex
            return ex.lower()
        elif isinstance(ex, list):
            return [x.lower() for x in ex]

    def ex_validator(func, _item=None, tp: bool = True) -> bool:
        """
        Determines if an extension supplied is equivalent to what it is all about prior to deletion.

        :param func: A str or list value of extensions

        :param _item: An iterable of a file extension

        :param tp: Changes context between file or search mode parameter for this function.

        :return: True or False for the query
        """
        if isinstance(func, str):
            _ex_name = (f".{_item.get('filename').split('.')[-1].lower()}" if "." in func else
                        _item.get('filename').split('.')[-1].lower()) if tp is True else \
                (f".{_item[-1].split('.')[-1].lower()}" if "." in func else
                 _item[-1].split('.')[-1].lower())
            return _ex_name == func
        elif isinstance(func, list):
            _ex_name = (f".{_item.get('filename').split('.')[-1].lower()}" if [f for f in func if "." in f] else
                        _item.get('filename').split('.')[-1].lower()) if tp is True else \
                (f".{_item[-1].split('.')[-1].lower()}" if [f for f in func if "." in f] else
                 _item[-1].split('.')[-1].lower())
            return _ex_name in func
        return False

    def get_attachments(items: Dict) -> None:
        """
        Helps to get a list of attachments on an issue.

        :param items: A dictionary of search results.

        :return: None
        """
        nonlocal attach_load, count, depth
        infinity_point = data_brick["point"]
        issues = items["issues"][data_brick["point"]:]
        attach_load = data_brick["data_block"] if back_up is True else attach_load
        count = set_up["iter"] if back_up is True and depth == 1 else data_brick["iter"]

        def inf_block(atl: bool = False):
            """
            A function that updates data_brick.

            :param atl: Indicates whether a condition exist that favours search attachment or not.

            :return: None
            """
            data_brick.update({
                "data_block": attach_load,
                "key": keys,
                "status": "in_progress",
                "point": infinity_point
            }) if atl is False else \
                data_brick.update({
                    "key": keys,
                    "status": "in_progress",
                    "point": infinity_point
                })

        for each_issue in issues:
            keys = each_issue["key"]
            _data = LOGIN.get(endpoint.issues(keys))
            if _data.status_code < 300:
                attachments = _data.json()["fields"]["attachment"]
                if len(attachments) > 0:
                    for attach in attachments:
                        attach_item = {
                            "key": keys,
                            "filename": attach.get("filename"),
                            "id": attach.get("id"),
                            "size": attach.get("size"),
                            "content": attach.get("content"),
                            "mimetype": attach.get("mimeType"),
                            "created": attach.get("created"),
                            "author": attach.get("author").get("displayName"),
                            "accountid": attach.get("author").get("accountId")
                        }
                        print("Accessing attachments {} | Key: {}".format(attach.get("filename"), keys))
                        add_log("Accessing attachments {} | Key: {}".format(attach.get("filename"), keys), "info")
                        attach_load.append(attach_item)
                        inf_block()
                else:
                    inf_block(atl=True)
            else:
                inf_block(atl=True)
            json.dump(data_brick, open(data_file, mode="w+", encoding="utf-8"),
                      indent=4) if allow_cp is True else None
            infinity_point += 1

    data_brick = {}
    set_up = {}

    def data_wipe(del_, counts_, usr: bool = False, fl: bool = False, _items_=None) -> None:
        """
        Trigger the delete mode.

        :param del_: The response delete request
        :param counts_: A continuous counter
        :param usr: User entity available or not. Default is false
        :param fl: File entity available or not. Default is false
        :param _items_: An iterable data

        :return: None
        """
        if del_.status_code < 300:
            data_brick.update({"saves" if fl is False else "iter": counts_})
            print("Deleting attachment \"{}\" | Key: {}".format(_items_.get("filename") if fl is False
                                                                else _items_[0],
                                                                _items_.get("key") if fl is False else _items_[1]
                                                                )) if usr is False \
                else print("Deleting attachment by user {} \"{}\" | Key: {}"
                           .format(_items_.get("author"), _items_.get("filename"),
                                   _items_.get("key")))
            add_log("The Attachments \"{}\" has been deleted | Key: {}".format(_items_.get("filename")
                                                                               if fl is False else
                                                                               _items_[0],
                                                                               _items_.get("key") if fl is False
                                                                               else _items_[1]), "info")
        else:
            data_brick.update({"saves" if fl is False else "iter": counts_})
            print("Unable to delete attachment \"{}\" | Key: {}".format(_items_.get("filename") if fl is False else
                                                                        _items_[0],
                                                                        _items_.get("key") if fl is False
                                                                        else _items_[1])) if usr is \
                                                                                             False \
                else print("Unable to delete attachment by user {} \"{}\" | Key: {}"
                           .format(_items_.get("author"), _items_.get("filename"),
                                   _items_.get("key")))
            add_log("Attachment deletion of \"{}\" failed with reason \"{}\" | Key: {}"
                    .format(_items_.get("filename") if fl is False else _items_[0],
                            del_.reason, _items_.get("key") if fl is False else _items_[1]), "info")

    if allow_cp is True:
        if os.path.isfile(data_file) and os.stat(data_file).st_size != 0:
            user_input = input("An existing save point exist from your last search, "
                               "do you want to use it? (Y/N) \n")
            set_up = json.load(open(data_file))
            if user_input.lower() in ["y", "yes"]:
                back_up = True
            else:
                print("Starting search from scratch.")
                add_log("Starting search from scratch, any previous data will be removed", "info")
    os.open(data_file, flags=os.O_CREAT) if allow_cp is True else None
    count, cycle, step = 0, 0, 0
    if file is None:
        if search is None:
            add_log("The search parameter can't be None when you have not provided a file input data.", "debug")
            raise JiraOneErrors("value", "Search parameter can't be None if a file is not provided.")
        search_path = search
    elif file is not None:
        key_index = 0
        attach_index = []
        temp_reader = file_reader(file_name=file, **kwargs)
        loop = 1
        for _row in temp_reader:
            _loop_count = -1
            loop += 1
            for inner_row in _row:
                _loop_count += 1
                if inner_row == "Issue key":
                    key_index = _loop_count
                if inner_row == "Attachment":
                    img_index = _loop_count
                    attach_index.append(img_index)
            if loop > 1:
                break

        reader = file_reader(file_name=file, skip=True, **kwargs)
        new_data_form = deque()
        do_once = 0
        for issue in reader:
            _attach_ = {}
            key = issue[key_index]
            attach_pattern = re.compile(r"(?:\w{4,5}:\/\/\w*\.+\w+.\w+\/[s]\w*\/.\w.+\.\w+)")
            if len(attach_index) > 0:
                attach_loop = 0
                for column in attach_index:
                    attach_loop += 1
                    _attach_.update({
                        "attach_{}".format(attach_loop): issue[column]
                    })
            # Find every attachment in the attachment column to determine the attachments
            for each_attach, attach_ in _attach_.items():
                if ";" in attach_:
                    break_ = attach_.split(";")
                    files_ = break_[-1]
                    new_data_form.append([key, files_])
            do_once += 1
            if len(_attach_) == 0 and do_once == 1:
                print("Attachment not processed, file structure could be empty or not properly formatted.")
                add_log(f"It seems that the attachments URL could not be determined from the {file}", "debug")
            # Use regex to find other attachments links that are in other fields.
            # The below would likely find one or more links or none if it can't.
            for data in issue:
                if attach_pattern.match(data) is not None:
                    _files = attach_pattern.match(data).group()
                    new_data_form.append([key, _files])

        new_list = []
        for arrange_attach in new_data_form:
            if arrange_attach[1] is not None:
                new_list.append([arrange_attach[0], arrange_attach[1]])
        new_data_form.clear()
        split_file = file.split('.')[-2]
        new_file = f"{split_file}_temp.csv"
        file_writer(folder, file_name=new_file, data=new_list, mark="many", mode="w+")
        read_file = file_reader(folder, file_name=new_file)

        step = 0 if back_up is False and os.stat(data_file).st_size == 0 else set_up["iter"]
        count = step
        for item in read_file[step:]:
            attach_ = item[1].split("/")
            attach_id = attach_[-2]
            if delete is True:
                if extension is not None:
                    if ex_validator(get_ext(extension), attach_, tp=False):
                        delete_ = LOGIN.delete(endpoint.issue_attachments(attach_id=attach_id))
                        data_wipe(delete_, count, fl=True, _items_=[attach_[-1], item[0]])
                else:
                    delete_ = LOGIN.delete(endpoint.issue_attachments(attach_id=attach_id))
                    data_wipe(delete_, count, fl=True, _items_=[attach_[-1], item[0]])
            else:
                data_brick.update({"iter": count})
                print("Safe mode on: Attachment will not be deleted \"{}\" | Key: {}".format(attach_[-1], item[0]))
                add_log("Safe mode on: Attachment will not be deleted \"{}\" | Key: {}".format(attach_[-1], item[0]),
                        "info")
            count += 1
            json.dump(data_brick, open(data_file, mode="w+", encoding="utf-8"),
                      indent=4) if allow_cp is True else None
        os.remove(path_builder(folder, file_name=new_file))
    if search_path is not None:
        query = f"key in ({search_path})" if isinstance(search_path, (str, int)) \
            else "key in {}".format(tuple(search_path)) \
            if isinstance(search_path, list) else search_path["jql"] if isinstance(search_path, dict) else \
            sys.stderr.write("Unexpected datatype received. Example on https://jiraone.readthedocs.io ")
        data_brick["status"] = set_up["status"] if "status" in set_up and back_up is True else "in_progress"
        depth: int = 1
        while True:
            load = LOGIN.get(endpoint.search_issues_jql(query=set_up["query"], start_at=set_up["iter"],
                                                        max_results=100)) if back_up is True and depth == 1 else \
                LOGIN.get(endpoint.search_issues_jql(query=query, start_at=count,
                                                     max_results=100))
            if data_brick["status"] == "complete":
                open_ = json.load(open(data_file)) if allow_cp is True else {}
                attach_load = open_["data_block"] if "data_block" in open_ else []
                break
            if load.status_code < 300:
                data_ = load.json()
                cycle = 0
                print("Extracting attachment details on row {}".
                      format(set_up["iter"] if back_up is True and depth == 1 else count))
                print("*" * 100)
                add_log("Extracting attachment details on row {}".
                        format(set_up["iter"] if back_up is True and depth == 1 else count), "info")
                data_brick.update(
                    {
                        "iter": set_up["iter"] if back_up is True and depth == 1 else count,
                        "query": set_up["query"] if back_up is True and depth == 1 else query,
                        "data_block": set_up["data_block"] if back_up is True and depth == 1 else attach_load,
                        "point": set_up["point"] + 1 if back_up is True and depth == 1 else 0
                    }
                )
                if count > data_["total"]:
                    data_brick.update({"status": "complete"})
                    json.dump(data_brick, open(data_file, mode="w+", encoding="utf-8"),
                              indent=4) if allow_cp is True else None
                    add_log("Extraction is completed, deletion of attachments on the next step", "info")
                    break
                get_attachments(data_)
            count += 100
            if back_up is True and depth == 1:
                data_brick["iter"] = count
                back_up = False
            depth += 2
            if load.status_code > 300:
                cycle += 1
                if cycle > 99:
                    add_log("Trying to search for the issues with query \"{}\" returned a \"{}\" "
                            "error with reason \"{}\".".format(query, load.status_code, load.reason), "error")
                    raise JiraOneErrors("value", "It seems that the search \"{}\" cannot be "
                                                 "retrieved as we've attempted it {} times".format(query, cycle))

        length = len(attach_load)
        if length > 0:
            _open_ = json.load(open(data_file)) if allow_cp is True else {}
            data_brick["data_block"] = attach_load
            data_brick["iter"] = _open_["iter"] if "iter" in _open_ else 0
            data_brick["query"] = _open_["query"] if "query" in _open_ else query
            data_brick["saves"] = _open_["saves"] if "saves" in _open_ else 0
            step = 0 if back_up is False else data_brick["saves"]
            count = step
            for each_item in attach_load[step:]:
                if delete is True:
                    if extension is not None:
                        if ex_validator(get_ext(extension), each_item):
                            if by_user is not None:
                                if each_item.get("accountid") in by_user:
                                    if by_size is not None:
                                        if regulator(by_size, each_item):
                                            if by_date is not None:
                                                if time_share(by_date, each_item):
                                                    delete_ = LOGIN.delete(endpoint.issue_attachments
                                                                           (attach_id=each_item.get("id")))
                                                    data_wipe(delete_, count, usr=True, _items_=each_item)
                                            else:
                                                delete_ = LOGIN.delete(endpoint.issue_attachments
                                                                       (attach_id=each_item.get("id")))
                                                data_wipe(delete_, count, usr=True, _items_=each_item)
                                    else:
                                        if by_date is not None:
                                            if time_share(by_date, each_item):
                                                delete_ = LOGIN.delete(endpoint.issue_attachments
                                                                       (attach_id=each_item.get("id")))
                                                data_wipe(delete_, count, usr=True, _items_=each_item)
                                        else:
                                            delete_ = LOGIN.delete(endpoint.issue_attachments
                                                                   (attach_id=each_item.get("id")))
                                            data_wipe(delete_, count, usr=True, _items_=each_item)
                            else:
                                if by_size is not None:
                                    if regulator(by_size, each_item):
                                        if by_date is not None:
                                            if time_share(by_date, each_item):
                                                delete_ = LOGIN.delete(endpoint.issue_attachments
                                                                       (attach_id=each_item.get("id")))
                                                data_wipe(delete_, count, _items_=each_item)
                                        else:
                                            delete_ = LOGIN.delete(endpoint.issue_attachments
                                                                   (attach_id=each_item.get("id")))
                                            data_wipe(delete_, count, _items_=each_item)
                                else:
                                    if by_date is not None:
                                        if time_share(by_date, each_item):
                                            delete_ = LOGIN.delete(endpoint.issue_attachments
                                                                   (attach_id=each_item.get("id")))
                                            data_wipe(delete_, count, _items_=each_item)
                                    else:
                                        delete_ = LOGIN.delete(
                                            endpoint.issue_attachments(attach_id=each_item.get("id")))
                                        data_wipe(delete_, count, _items_=each_item)
                    else:
                        if by_user is not None:
                            if each_item.get("accountid") in by_user:
                                if by_size is not None:
                                    if regulator(by_size, each_item):
                                        if by_date is not None:
                                            if time_share(by_date, each_item):
                                                delete_ = LOGIN.delete(endpoint.issue_attachments
                                                                       (attach_id=each_item.get("id")))
                                                data_wipe(delete_, count, usr=True, _items_=each_item)
                                        else:
                                            delete_ = LOGIN.delete(endpoint.issue_attachments
                                                                   (attach_id=each_item.get("id")))
                                            data_wipe(delete_, count, usr=True, _items_=each_item)
                                else:
                                    if by_date is not None:
                                        if time_share(by_date, each_item):
                                            delete_ = LOGIN.delete(endpoint.issue_attachments
                                                                   (attach_id=each_item.get("id")))
                                            data_wipe(delete_, count, usr=True, _items_=each_item)
                                    else:
                                        delete_ = LOGIN.delete(endpoint.issue_attachments
                                                               (attach_id=each_item.get("id")))
                                        data_wipe(delete_, count, usr=True, _items_=each_item)
                        else:
                            if by_size is not None:
                                if regulator(by_size, each_item):
                                    if by_date is not None:
                                        if time_share(by_date, each_item):
                                            delete_ = LOGIN.delete(endpoint.issue_attachments
                                                                   (attach_id=each_item.get("id")))
                                            data_wipe(delete_, count, _items_=each_item)
                                    else:
                                        delete_ = LOGIN.delete(endpoint.issue_attachments
                                                               (attach_id=each_item.get("id")))
                                        data_wipe(delete_, count, _items_=each_item)
                            elif by_date is not None:
                                if time_share(by_date, each_item):
                                    delete_ = LOGIN.delete(endpoint.issue_attachments
                                                           (attach_id=each_item.get("id")))
                                    data_wipe(delete_, count, _items_=each_item)
                            else:
                                delete_ = LOGIN.delete(endpoint.issue_attachments
                                                       (attach_id=each_item.get("id")))
                                data_wipe(delete_, count, _items_=each_item)
                else:
                    data_brick.update({"saves": count})
                    print("Safe mode on: Attachment will not be deleted \"{}\" | Key: {}".
                          format(each_item.get("filename"), each_item.get("key")))

                count += 1
                json.dump(data_brick, open(data_file, mode="w+", encoding="utf-8"),
                          indent=4) if allow_cp is True else None

        else:
            print("The data search seems to be empty. Please recheck your search criteria.")
            add_log("Searching for attachment did not yield any result. It seems the search criteria"
                    " does not have attachments.", "debug")

    os.remove(data_file) if allow_cp is True else None


USER = Users()
PROJECT = Projects()
comment = PROJECT.comment_on
