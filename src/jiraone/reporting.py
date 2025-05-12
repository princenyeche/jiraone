#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Example methods of Generating reports

Provided herein are Report Generator Classes and Methods,
Easily generate report for the various endpoints
"""
import json
import csv
import sys
import os
import re
from typing import (
    Any,
    List,
    Iterable,
    Tuple,
    Union,
    Dict,
    Optional,
)
from collections import (
    deque,
    namedtuple,
    OrderedDict,
)
from jiraone import (
    LOGIN,
    endpoint,
    add_log,
    WORK_PATH,
)


class Projects:
    """Get report on a Project based on user or user's attributes or groups."""

    @staticmethod
    def projects_accessible_by_users(
        *args: str,
        project_folder: str = "Project",
        project_file_name: str = "project_file.csv",
        user_extraction_file: str = "project_extract.csv",
        **kwargs,
    ) -> None:
        """
        Send an argument as String equal to a value, example: status=live.

        Multiple arguments separate by comma as the first argument in the
        function, all other arguments should be keyword args that follows.
        This API helps to generate full user accessibility to Projects on Jira.
        It checks the users access and commits the finding to a report file.

        You can tweak the permission argument with the options mention `here
        <https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-user-search>`_

        for endpoint /rest/api/3/user/permission/search

        :param args: A set of parameter arguments to supply

        :param project_folder: A folder

        :param project_file_name: A file to hold temp data

        :param user_extraction_file: A file to hold user temp data

        :param kwargs: Additional arguments

                      **Acceptable options**

                      * permission: A permission of Jira to check

        .. _here:

        :return: None
        """
        permission: str = kwargs.get("permission", "BROWSE")
        count_start_at = 0
        headers = [
            "Project Key",
            "Project Name",
            "Issue Count",
            "Last Issue Update",
        ]
        file_writer(
            folder=project_folder,
            file_name=project_file_name,
            data=headers,
        )

        def project():
            file_writer(
                project_folder,
                project_file_name,
                data=raw,
            )
            read_users = file_reader(
                folder=project_folder,
                file_name=file_name,
            )
            for user in read_users:
                account_id = user[0]
                display_name = user[2]
                active_status = user[3]
                project_key = keys
                find = LOGIN.get(
                    endpoint.find_users_with_permission(
                        account_id,
                        project_key,
                        permission,
                    )
                )
                data = json.loads(find.content)
                if str(data) == "[]":
                    raw_vision = [
                        display_name,
                        f"Has {permission} Permission: False",
                        f"Project: {name}",
                        f"User Status: {active_status}",
                    ]
                    file_writer(
                        project_folder,
                        project_file_name,
                        data=raw_vision,
                    )
                else:
                    for d in data:
                        d_name = d["displayName"]
                        active = d["active"]
                        raw_vision = [
                            d_name,
                            f"Has {permission} Permission: {active}",
                            f"Project: {name}",
                            f"User Status: {active_status}",
                        ]

                        file_writer(
                            project_folder,
                            project_file_name,
                            data=raw_vision,
                        )

        file_name = user_extraction_file
        USER.get_all_users(
            file=file_name,
            folder=project_folder,
            **kwargs,
        )
        print("Project User List Extracted")
        add_log(
            "Project User List Extracted",
            "info",
        )
        while True:
            load = LOGIN.get(
                endpoint.get_projects(
                    *args,
                    start_at=count_start_at,
                )
            )
            count_start_at += 50
            if load.status_code == 200:
                results = json.loads(load.content)
                for key in results["values"]:
                    keys = key["key"]
                    name = key["name"]
                    if "insight" in key:
                        insight = key["insight"]
                        if (
                            "totalIssueCount"
                            and "lastIssueUpdateTime" in insight
                        ):
                            raw = [
                                keys,
                                name,
                                f"{insight['totalIssueCount']}",
                                f"{insight['lastIssueUpdateTime']}",
                            ]
                            project()
                        elif (
                            "totalIssueCount" in insight
                            and "lastIssueUpdateTime" not in insight
                        ):
                            raw = [
                                keys,
                                name,
                                f"{insight['totalIssueCount']}",
                                "No data available",
                            ]
                            project()
                    else:
                        raw = [
                            keys,
                            name,
                            "No data available",
                            "No data available",
                        ]
                        project()

                if count_start_at > results["total"]:
                    print("Project Reporting Completed")
                    print(
                        "File extraction completed. "
                        "Your file is located at {}".format(
                            path_builder(
                                path=project_folder,
                                file_name=project_file_name,
                            )
                        )
                    )
                    add_log(
                        "Project Reporting Completed",
                        "info",
                    )
                    break
            else:
                sys.stderr.write(
                    "Unable to fetch data status {} ".format(load.status_code)
                )
                add_log(
                    f"Data retrieval failure " f"due to {load.reason}",
                    "error",
                )
                sys.exit(1)

    @staticmethod
    def dashboards_shared_with(
        dashboard_folder: str = "Dashboard",
        dashboard_file_name: str = "dashboard_file.csv",
        **kwargs,
    ) -> None:
        """
        Retrieve the Dashboard Id/Name/owner and who it is shared with.

        The only requirement is that the user querying this API should have
        access to all the Dashboard available else it will only return
        dashboard where the user's view access is allowed.

        :param dashboard_folder: A folder

        :param dashboard_file_name: A file to store temp data

        :param kwargs: Additional arguments

        :return: None
        """
        count_start_at = 0
        dash_list = deque()  # get the id of dashboard search
        # arrange the different values associated with dashboard
        put_list = deque()
        dump_list = deque()  # dump the results into our csv writer
        headers = [
            "Dashboard Id",
            "Dashboard Name",
            "Owner",
            "Shared Permission",
        ]
        file_writer(
            folder=dashboard_folder,
            file_name=dashboard_file_name,
            data=headers,
            **kwargs,
        )

        while True:
            load = LOGIN.get(
                endpoint.search_for_dashboard(start_at=count_start_at)
            )
            count_start_at += 50
            if load.status_code == 200:
                results = json.loads(load.content)
                for value in results["values"]:
                    valid = value["id"]
                    name = value["name"]
                    raw = [
                        valid,
                        name,
                    ]
                    dash_list.append(raw)

                print("Dashboard List Extracted")
                add_log(
                    "Dashboard List Extracted",
                    "info",
                )

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
                                project = (
                                    f"Project Name: {pem['project']['name']}"
                                )
                                put_list.append(project)
                            if types == "loggedin" or types == "global":
                                put_list.append(types)

                    extract = [d for d in put_list]
                    raw = [
                        value[0],
                        names,
                        owner,
                        extract,
                    ]
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

                file_writer(
                    dashboard_folder,
                    dashboard_file_name,
                    data=dump_list,
                    mark="many",
                )

                if count_start_at > results["total"]:
                    print("Dashboard Reporting Completed")
                    print(
                        "File extraction completed. "
                        "Your file is located at {}".format(
                            path_builder(
                                path=dashboard_folder,
                                file_name=dashboard_file_name,
                            )
                        )
                    )
                    add_log(
                        "Dashboard Reporting Completed",
                        "info",
                    )
                    break

    @staticmethod
    def get_all_roles_for_projects(
        roles_folder: str = "Roles",
        roles_file_name: str = "roles_file.csv",
        user_extraction: str = "role_users.csv",
        **kwargs,
    ) -> None:
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
        headers = [
            "Project Id ",
            "Project Key",
            "Project Name",
            "Project roles",
            "User AccountId",
            "User DisplayName",
            "User role in Project",
        ]
        file_writer(
            folder=roles_folder,
            file_name=roles_file_name,
            data=headers,
            **kwargs,
        )

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
                add_log(
                    "Extracting Project Keys {}".format(key),
                    "info",
                )

                # find out what roles exist within each project
                def role_over() -> Tuple:
                    if roles.status_code == 200:
                        extract = json.loads(roles.content)
                        only_keys = extract.keys()
                        casting = list(only_keys)
                        only_values = extract.items()
                        puller = list(only_values)
                        z = [d for d in puller]
                        return (
                            casting,
                            z,
                        )

                caster = role_over()
                raw = [
                    pid,
                    key,
                    name,
                    caster[0],
                ]
                role_list.append(raw)
                add_log(
                    "Appending data to List Queue",
                    "info",
                )

                for user in read_users:
                    account_id = user[0]
                    display_name = user[2]

                    # extract the user role using the appropriate accountId
                    def get_user_role(
                        user_data,
                    ) -> None:
                        for users in user_data[1]:
                            check = LOGIN.get(users[1])
                            if check.status_code == 200:
                                result_data = json.loads(check.content)
                                actors = result_data["actors"]
                                for act in actors:
                                    if "actorUser" in act:
                                        if (
                                            account_id
                                            == act["actorUser"]["accountId"]
                                        ):
                                            res = f"Role Name: {result_data['name']}"
                                            project_role_list.append(res)

                        # function to write collected data into a file
                        def pull_data() -> None:
                            role_puller = [j for j in project_role_list]
                            project_id = data[0]
                            project_key = data[1]
                            project_name = data[2]
                            project_roles = data[3]
                            raw_dump = [
                                project_id,
                                project_key,
                                project_name,
                                project_roles,
                                account_id,
                                display_name,
                                role_puller,
                            ]
                            file_writer(
                                folder=roles_folder,
                                file_name=roles_file_name,
                                data=raw_dump,
                            )

                        for data in role_list:
                            pull_data()

                    get_user_role(caster)
                    project_role_list = deque()

        USER.get_all_users(
            folder=roles_folder,
            file=user_extraction,
            **kwargs,
        )
        read_users = file_reader(
            folder=roles_folder,
            file_name=user_extraction,
            **kwargs,
        )
        while True:
            init = LOGIN.get(endpoint.get_projects(start_at=count_start_at))
            if init.status_code == 200:
                print("Project Extraction")
                results = json.loads(init.content)
                add_log(
                    "Project Extraction Initiated",
                    "info",
                )
                if count_start_at > results["total"]:
                    break
                if results["total"] > 0:
                    role_on()
            count_start_at += 50

        print(
            "File extraction completed. Your file is located at {}".format(
                path_builder(
                    path=roles_folder,
                    file_name=roles_file_name,
                )
            )
        )
        add_log(
            "File extraction completed",
            "info",
        )

    def get_attachments_on_projects(
        self,
        attachment_folder: str = "Attachment",
        attachment_file_name: str = "attachment_file.csv",
        mode: str = 'w',
        **kwargs,
    ) -> None:
        """Fetch the list of all the attachments of a Project or Projects
        and write it out to an attachment list CSV file named ``attachment_file_name``
        located in ``attachment_folder``.

        Also, get the size of the attachment for each Issue, sum up the size of all
        attachments, and output the total for all Projects as the last
        row of the output attachment list CSV file.

        JQL is used to search for the attachments.

        :param attachment_folder: Target directory where the attachment list CSV
            file will be written.

        :param attachment_file_name: Filename of the attachment list CSV to be written.

        :param mode: Write mode for attachment list CSV to be written. By default it
            is 'w', which means that any existing file will be overwritten.
            For example, set to 'a' if you want to append to instead of truncating any
            existing file.

        :param kwargs: Additional arguments to specify.
        """
        attach_list = deque()
        count_start_at: Union[str, int] = 0 if LOGIN.api is False else None
        headers = [
            "Project id",
            "Project key",
            "Project name",
            "Issue key",
            "Attachment size",
            "Attachment type",
            "Name of file",
            "Created on by user",
            "Attachment url",
        ]
        file_writer(
            folder=attachment_folder,
            file_name=attachment_file_name,
            data=headers,
            mode=mode,
            **kwargs,
        )

        def pull_attachment_sequence() -> None:
            """
            Pulls the data and transform into given results.

            :return: None
            """
            nonlocal attach_list # noqa: F824
            for issues in result_data["issues"]:
                keys = issues["key"]
                get_issue_keys = LOGIN.get(
                    endpoint.issues(issue_key_or_id=keys)
                )
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
                                    display_name = attach["author"][
                                        "displayName"
                                    ]

                                def pull_attachment() -> None:
                                    """
                                    Arranges extracts data
                                    :return: None
                                    """
                                    file_name = attach[
                                        "filename"
                                    ]  # name of the file
                                    created = attach[
                                        "created"
                                    ]  # datetime need to convert it
                                    attachment_size = attach[
                                        "size"
                                    ]  # in bytes, need to convert to mb
                                    mime_type = attach.get("mimeType")
                                    attachment_url = attach["content"]

                                    calc_size = self.byte_converter(
                                        attachment_size
                                    )
                                    calc_date = self.date_converter(created)

                                    pull = [
                                        project_id,
                                        project_key,
                                        project_name,
                                        keys,
                                        calc_size,
                                        mime_type,
                                        file_name,
                                        f"{calc_date} by {display_name}",
                                        attachment_url,
                                    ]
                                    attach_list.append(pull)

                                pull_attachment()

            raw_data = [x for x in attach_list]
            file_writer(
                attachment_folder,
                attachment_file_name,
                data=raw_data,
                mark="many",
            )
            attach_list.clear()

        while True:
            get_issue = LOGIN.get(
                endpoint.search_issues_jql(
                    start_at=count_start_at,
                    **kwargs,
                ) if LOGIN.api is False else
                endpoint.search_cloud_issues(
                    next_page=count_start_at,
                    **kwargs,
                )
            )
            if get_issue.status_code == 200:
                result_data = json.loads(get_issue.content)
                if LOGIN.api is False:
                    if count_start_at > result_data["total"]:
                        print("Attachment extraction completed")
                        add_log(
                            "Attachment extraction completed",
                            "info",
                        )
                        break

                print("Attachment extraction processing")
                add_log(
                    "Attachment extraction processing",
                    "info",
                )
                pull_attachment_sequence()
                if LOGIN.api is True:
                    if "nextPageToken" not in result_data:
                        print("Attachment extraction completed")
                        add_log(
                            "Attachment extraction completed",
                            "info",
                        )
                        break

            if LOGIN.api is False:
                count_start_at += 50
            elif LOGIN.api is True:
                count_start_at = get_issue.json().get("nextPageToken", None)

        def re_write() -> None:
            """
            Rewrite and sort the extracted data
            :return: None
            """
            nonlocal read_file # noqa: F824
            calc_made = self.grade_and_sort(
                attach_list,
                read_file,
            )
            attach_list.clear()
            rd_file = read_file
            # sort the file using the issue_key column
            sorts = sorted(
                rd_file,
                key=lambda row: row[3],
                reverse=False,
            )
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
                raw_data_file = [
                    _project_id,
                    _project_key,
                    _project_name,
                    _issue_key,
                    _attach_size,
                    _file_name,
                    _attach_type,
                    _created_by,
                    _attach_url,
                ]
                file_writer(
                    attachment_folder,
                    attachment_file_name,
                    data=raw_data_file,
                )

            # lastly we want to append the total sum of attachment size.
            raw_data_file = [
                "",
                "",
                "",
                "",
                "Total Size: {:.2f} MB".format(calc_made),
                "",
                "",
                "",
                "",
            ]
            file_writer(
                attachment_folder,
                attachment_file_name,
                data=raw_data_file,
            )

        read_file = file_reader(
            attachment_folder,
            attachment_file_name,
            skip=True,
        )
        file_writer(
            attachment_folder,
            attachment_file_name,
            data=headers,
            mode="w",
        )
        re_write()

        print(
            "File extraction completed. Your file is located at {}".format(
                path_builder(
                    path=attachment_folder,
                    file_name=attachment_file_name,
                )
            )
        )
        add_log(
            "File extraction completed",
            "info",
        )

    @staticmethod
    def byte_converter(
        val,
    ) -> str:
        """1 Byte = 8 Bits.

        using megabyte MB, value is 1000^2

        mebibyte MiB, value is 1024^2

        total = val / MB

        :param val: A value to supply

        :return: strings
        """
        byte_size = val
        mega_byte = 1000 * 1000
        visor = byte_size / mega_byte  # MB converter
        return "Size: {:.2f} MB".format(visor)

    @staticmethod
    def date_converter(
        val,
    ) -> str:
        """split the datetime value and output a string.

        :param val: A value to be supplied

        :return: string
        """
        get_date_time = val.split("T")
        get_am_pm = get_date_time[1].split(".")
        return f"Created on {get_date_time[0]} {get_am_pm[0]}"

    @staticmethod
    def grade_and_sort(
        attach_list,
        read_file,
    ) -> Union[float, int,]:
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
    def bytes_converter(
        val,
    ) -> str:
        """Returns unit in KB or MB.

        1 Byte = 8 Bits.

        using megabyte MB, value is 1000^2

        mebibyte MiB, value is 1024^2

        total = val / MB

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
        return "Size: {:.2f} {}".format(
            visor,
            unit,
        )

    @staticmethod
    def move_attachments_across_instances(
        attach_folder: str = "Attachment",
        attach_file: str = "attachment_file.csv",
        key: int = 3,
        attach: int = 8,
        **kwargs,
    ) -> None:
        """Ability to post an attachment into another Instance.

        given the data is extracted from a csv file which contains the
        below information
         * Issue key
         * file name
         * attachment url

        we assume you're getting this from ``def get_attachments_on_project()``

        :param attach_folder: a folder or directory path

        :param attach_file: a file to a file name

        :param key: a row index of the column

        :param attach: a row index of the column

        :param kwargs: Additional arguments

                       **Acceptable options**

                       * file:  Specify the index of the columns. Integer
                                datatype expected.

                       * last_cell: Determines if the last cell
                                    should be counted. Bool datatype expected.

             For example::

               e.g.
              * key=3,

              * attach=6,

              * file=8

        the above example corresponds with the index if using the
        ``def get_attachments_on_project()`` otherwise, specify your
        value in each keyword args when calling the method.

         :return: None
        """
        file: int = kwargs.get("file", 6)
        last_cell: bool = kwargs.get("last_cell", True)
        read = file_reader(
            folder=attach_folder,
            file_name=attach_file,
            skip=True,
            **kwargs,
        )
        add_log(
            "Reading attachment {}".format(attach_file),
            "info",
        )
        count = 0
        cols = read
        length = len(cols)
        for r in read:
            count += 1
            keys = r[key]
            attachment = r[attach]
            _file_name = r[file]
            fetch = LOGIN.get(attachment).content
            # use the file's keyword args to send multipart/form-data
            # in the post request of LOGIN.post
            payload = {
                "file": (
                    _file_name,
                    fetch,
                )
            }
            # modified our initial headers to accept X-Atlassian-Token
            # to avoid (CSRF/XSRF)
            new_headers = {
                "Accept": "application/json",
                "X-Atlassian-Token": "no-check",
            }
            LOGIN.headers = new_headers
            run = LOGIN.post(
                endpoint.issue_attachments(
                    keys,
                    query="attachments",
                ),
                files=payload,
            )
            if run.status_code != 200:
                print(
                    "Attachment not added to {}".format(keys),
                    "Status code: {}".format(run.status_code),
                )
                add_log(
                    "Attachment not added to {} due to {}".format(
                        keys,
                        run.reason,
                    ),
                    "error",
                )
            else:
                print(
                    "Attachment added to {}".format(keys),
                    "Status code: {}".format(run.status_code),
                )
                add_log(
                    "Attachment added to {}".format(keys),
                    "info",
                )
            # remove the last column since if it contains empty cells.
            if last_cell is True:
                if count >= (length - 1):
                    break

    @staticmethod
    def download_attachments(
        file_folder: str = 'Attachment',
        file_name: str = 'attachment_file.csv',
        download_path: str = "Downloads",
        attach: int = 8,
        skip_csv_header: bool = True,
        overwrite: bool = True,
        create_html_redirectors: bool = False,
        **kwargs,
    ) -> None:
        """Go through the attachment list CSV file named ``file_name`` and located in the
        ``file_folder``; for each row, download the attachment indicated to your local device.

        Calling this method with default arguments assumes that you've
        previously called the ``def get_attachments_on_project()`` method
        with default arguments.

        To avoid conflicts whenever attachments have the same filename (e.g. ``screenshot-1.png``),
        each downloaded attachment will be placed in a separate directory which corresponds to the
        content ID that Jira gives the attachment.

        :param download_path: the directory where the downloaded attachments are to be stored

        :param file_folder: the directory where the attachment list CSV file can be found
            (Default corresponds to the output of ``def get_attachments_on_project()``
            when called with default arguments)

        :param file_name: file name of the attachment list CSV file
            (Default corresponds to the output of ``def get_attachments_on_project()``
            when called with default arguments)

        :param attach: index of the column that corresponds to 'Attachment URL' in the attachment
            list CSV file.
            (Default is 8, which corresponds to the output of ``def get_attachments_on_project()``)

        :param skip_csv_header: when set to True, skips the first line of the attachment list CSV file; i.e.
            assumes that the first line represents a header row.
            (Default is True, which corresponds to the output of ``def get_attachments_on_project()``)

        :param overwrite: when True, any attachments will be overwritten. When False, downloading
            of the attachment will be skipped. Setting this to False can significantly speed up
            incremental backups by only downloading attachments that have not yet been downloaded.

        :param create_html_redirectors: is used when you want to use the downloaded attachments
            as part of a website to mirror and serve the attachments separately from the
            Jira website. When set to True, an ``index.html`` will be created
            for each attachment so that the original Jira Attachment URL, e.g.
            https://yourorganization.atlassian.net/rest/api/3/attachment/content/112736 ,
            can be more easily rewritten to something like
            https://yourmirrorsite.com/jiraone/MYPROJ/attachment/content/112736 .
            The ``index.html`` will take care of the HTTP redirect that will point to the
            attachment with the original filename.

        :param kwargs: Additional keyword argument

                        **Acceptable options**

                        * file: index of the column 'Name of file' in the attachment list CSV file.
                            (Default is 6, which corresponds to the output of
                            ``def get_attachments_on_project()``)

        :return: None
        """
        HTML_REDIRECTOR_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
  <title>Download File</title>
  <meta http-equiv="refresh" content="0; url={path}">
</head>
<body>
    <p>If you are not redirected automatically, please click <a href="{path}">here</a> to download the file.</p>
</body>
</html>
"""

        file: int = kwargs.get("file", 6)
        read = file_reader(
            folder=file_folder,
            file_name=file_name,
            skip=skip_csv_header,
            **kwargs,
        )
        add_log(
            "Reading attachment {}".format(file_name),
            "info",
        )
        count = 0
        cols = read
        length = len(cols)
        last_cell = kwargs["last_cell"] if "last_cell" in kwargs else False
        for r in read:
            count += 1
            attachment = r[attach]
            _file_name = r[file]
            if attachment == '' or _file_name == '':
                # For example the last line of the attachment list CSV may have:  ,,,,Total Size:
                # 0.09 MB,,,,
                continue
            content_id = attachment.split('/')[-1]
            individual_download_path = os.path.join(download_path, content_id)
            if not os.path.exists(individual_download_path):
                os.makedirs(individual_download_path)
            if overwrite or not os.path.exists(os.path.join(individual_download_path, _file_name)):
                fetch = LOGIN.get(attachment)
                file_writer(
                    folder=individual_download_path,
                    file_name=_file_name,
                    mode="wb",
                    content=fetch.content,
                    mark="file",
                )
                print(
                    "Attachment downloaded to {}".format(individual_download_path),
                    "Status code: {}".format(fetch.status_code),
                )
                add_log(
                    "Attachment downloaded to {}".format(individual_download_path),
                    "info",
                )
            if create_html_redirectors:
                # Create HTML file with a template that
                html_content = HTML_REDIRECTOR_TEMPLATE.format(path=_file_name)
                # Write the content to file
                with open(os.path.join(individual_download_path, 'index.html'), 'w') as html_file:
                    html_file.write(html_content)
                add_log(
                    "Attachment HTML redirector created in {}".format(individual_download_path),
                    "info",
                )
            if last_cell is True:
                if count >= (length - 1):
                    break

    @staticmethod
    def get_total_comments_on_issues(
        folder: str = "Comment",
        file_name: str = "comment_file.csv",
        **kwargs,
    ) -> None:
        """Return a report with the number of comments sent to or by a
        reporter (if any).

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
        user_type = (
            "atlassian" if "user_type" not in kwargs else kwargs["user_type"]
        )
        file = "user_file.csv" if "file" not in kwargs else kwargs["file"]
        find_user = (
            "test user" if "find_user" not in kwargs else kwargs["find_user"]
        )
        duration = (
            "startOfWeek(-1)"
            if "duration" not in kwargs
            else kwargs["duration"]
        )
        status = None if "status" not in kwargs else kwargs["status"]
        get_user = ""
        headers = [
            "Project Id",
            "Project Key",
            "Project Name",
            "Issue Key",
            "Total Comment",
            "Reporter accountId",
            "Display name of Reporter",
            "Comment by Reporter",
            "Comment by others",
        ]
        file_writer(
            folder,
            file_name,
            data=headers,
        )
        USER.get_all_users(
            pull=pull,
            user_type=user_type,
            file=file,
            folder=folder,
        )
        CheckUser = namedtuple(
            "CheckUser",
            [
                "accountId",
                "account_type",
                "display_name",
                "active",
            ],
        )
        read = file_reader(
            folder=folder,
            file_name=file,
        )
        for _ in read:
            f = CheckUser._make(_)
            if find_user in f._asdict().values():
                get_user = f.accountId
                print(
                    "User {} found - accountId: {}".format(
                        find_user,
                        get_user,
                    )
                )

        if get_user == "":
            print("User: {}, not found exiting search...".format(find_user))
            sys.exit(1)
        search_issues = (
            "reporter = {} AND updated <= {}".format(
                get_user,
                duration,
            )
            if "status" not in kwargs or status is None
            else "reporter = {} AND updated <= {} AND status in ({})".format(
                get_user,
                duration,
                status,
            )
        )
        print(
            "Searching with JQL:",
            search_issues,
        )
        count_start_at: Union[str, int] = 0 if LOGIN.api is False else None

        def extract_issue() -> None:
            """Find the comment in each issue and count it.
            :return: None
            """
            comment_by_users = 0
            comment_by_others = 0
            for issues in result_data["issues"]:
                keys = issues["key"]
                get_issue_keys = LOGIN.get(
                    endpoint.issues(issue_key_or_id=keys)
                )
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
                                        display_name = comment["author"][
                                            "displayName"
                                        ]
                                        account_id = comment["author"][
                                            "accountId"
                                        ]
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
                                    raw_dump = [
                                        project_id,
                                        project_key,
                                        project_name,
                                        keys,
                                        comment_total,
                                        reporter_aid,
                                        reporter_name,
                                        comment_by_users,
                                        comment_by_others,
                                    ]
                                    comment_list.append(raw_dump)

                                pull_comments()
                                comment_by_users = 0
                                comment_by_others = 0

            raw_data = [z for z in comment_list]
            file_writer(
                folder,
                file_name,
                data=raw_data,
                mark="many",
            )
            comment_list.clear()

        while True:
            get_issues = LOGIN.get(
                endpoint.search_issues_jql(
                    query=search_issues,
                    start_at=count_start_at,
                ) if LOGIN.api is False else
                endpoint.search_cloud_issues(
                    query=search_issues,
                    next_page=count_start_at,
                )
            )
            if get_issues.status_code == 200:
                result_data = json.loads(get_issues.content)
                if LOGIN.api is False:
                    if count_start_at > result_data["total"]:
                        print("Issues extraction completed")
                        add_log(
                            "Issue extraction completed",
                            "info",
                        )
                        break
                elif LOGIN.api is True:
                    if "nextPageToken" not in result_data:
                        print("Issues extraction completed")
                        add_log(
                            "Issue extraction completed",
                            "info",
                        )
                        break

                print("Extracting Issues...")
                extract_issue()

            if LOGIN.api is False:
                count_start_at += 50
            elif LOGIN.api is True:
                count_start_at = get_issues.json().get("nextPageToken", None)

        def count_and_total() -> (
            Tuple[
                int,
                int,
                int,
            ]
        ):
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
            return (
                calc_list_zero,
                calc_list_one,
                calc_list_two,
            )

        def write_result() -> None:
            """
            Sorts the result data

            :return: None
            """
            list_data = count_and_total()
            comment_list.clear()
            sorts = sorted(
                read_file,
                key=lambda rows: rows[3],
                reverse=False,
            )
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

                raw_data_file = [
                    _project_id,
                    _project_key,
                    _project_name,
                    _issue_key,
                    _comment_total,
                    _get_user,
                    _reporter_name,
                    _comm_by_reporter,
                    _comm_by_others,
                ]
                file_writer(
                    folder,
                    file_name,
                    data=raw_data_file,
                )

            # arranging the file last row
            raw_data_file = [
                "",
                "",
                "",
                "",
                "Total comments: {}".format(list_data[0]),
                "",
                "",
                "Total comments by Reporter: {}".format(list_data[1]),
                "Total comments by others: {}".format(list_data[2]),
            ]
            file_writer(
                folder,
                file_name,
                data=raw_data_file,
            )

        read_file = file_reader(
            folder,
            file_name,
            skip=True,
        )
        file_writer(
            folder,
            file_name,
            mode="w",
            data=headers,
        )
        write_result()

        print(
            "File extraction for comments completed. "
            "Your file is located at {}".format(
                path_builder(
                    path=folder,
                    file_name=file_name,
                )
            )
        )
        add_log(
            "File extraction for comments completed",
            "info",
        )

    @staticmethod
    def change_log(
        folder: str = "ChangeLog",
        file: str = "change_log.csv",
        back_up: bool = False,
        allow_cp: bool = True,
        **kwargs: Union[
            str,
            bool,
        ],
    ) -> None:
        """Extract the issue history of an issue.

        Query the changelog endpoint if using cloud instance or
        straight away define access to it on server.
        Extract the histories and export it to a CSV file.

        :param folder:  A name of a folder datatype String

        :param file:  A name of a file datatype String

        :param back_up: A boolean to check whether a history file
        is exist or not.

        :param allow_cp: Allow or deny the ability to have a checkpoint.

        :param kwargs: The other kwargs that can be passed as below.

               * jql: (required) A valid JQL query for projects or issues.
               datatype -> string

               * saved_file: The name of the file which saves the iteration.
               datatype -> string

               * show_output: Show a printable output on terminal.
               datatype -> boolean

               * field_name: Target a field name to render.
               datatype -> string

        :return: None
        """
        from jiraone.exceptions import (
            JiraOneErrors,
        )

        if LOGIN.get(endpoint.myself()).status_code > 300:
            raise JiraOneErrors(
                "login",
                "Authentication failed. " "Please check your credentials.",
            )
        changes = deque()
        item_list = deque()
        jql: str = (
            kwargs["jql"]
            if "jql" in kwargs
            else exit("A JQL query is required.")
        )
        saved_file: str = (
            "iter_saves.json"
            if "saved_file" not in kwargs
            else kwargs["saved_file"]
        )
        field_name = kwargs["field_name"] if "field_name" in kwargs else None
        show_output: bool = False if "show_output" in kwargs else True
        print("Extracting issue histories...")
        add_log(
            "Extracting issue histories...",
            "info",
        )
        # Indicates the first iteration in the main loop sequence.
        attempt: int = 1
        _fix_status_: bool = True if "fix" in kwargs else False

        def blank_data(
            key_val: str,
            sums: str,
            item_val: Any,
            name_: str,
        ) -> None:
            """
            Write the created date of an issue to a file.
            This is used for ``time_in_status()`` to accurately calculate
            the difference in status time.

            :param key_val: An issue key

            :param sums: A summary of an issue

            :param item_val: A dictionary of values

            :param name_: displayName of the user

            :return: None
            """
            nonlocal attempt

            if _fix_status_ is True and attempt == 1:
                create = LOGIN.get(endpoint.issues(key_val))
                if create.status_code < 300:
                    adjust = create.json().get("fields").get("created")
                    raw_ = (
                        [
                            key_val,
                            sums,
                            name_,
                            adjust,
                            "",
                            item_val.field,
                            item_val.from_,
                            item_val.fromString,
                            item_val.to,
                            item_val.toString,
                        ]
                        if LOGIN.api is False
                        else [
                            key_val,
                            sums,
                            name_,
                            adjust,
                            "",
                            item_val.field,
                            item_val.field_id,
                            item_val.from_,
                            item_val.fromString,
                            item_val.to,
                            item_val.toString,
                            item_val.tmpFromAccountId,
                            item_val.tmpToAccountId,
                        ]
                    )
                    file_writer(
                        folder,
                        file,
                        data=raw_,
                        mode="a+",
                    )
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

                def re_instantiate(
                    val: str,
                ) -> None:
                    """
                    Evaluate the issue key to run
                    :param val: An issue key variable
                    :return: None
                    """
                    # reach the changelog endpoint and extract
                    # the data of history for servers.
                    # https://docs.atlassian.com/software/jira/docs/api/REST/7.13.11/#api/2/issue-getIssue
                    get_issue_keys = LOGIN.get(
                        endpoint.issues(
                            issue_key_or_id=val,
                            query="expand=renderedFields,names,schema,operations,"
                            "editmeta,changelog,versionedRepresentations",
                        )
                    )
                    if get_issue_keys.status_code == 200:
                        key_data = json.loads(get_issue_keys.content)
                        # Bug Fix to "Extraction Of Jira History Error #47"
                        # return value of None in some issue keys.
                        # https://github.com/princenyeche/atlassian-cloud-api/issues/47
                        load_summary = LOGIN.get(
                            endpoint.issues(issue_key_or_id=val)
                        )
                        _summary = None
                        if load_summary.status_code < 300:
                            _summary = (
                                json.loads(load_summary.content)
                                .get("fields")
                                .get("summary")
                            )
                        if LOGIN.api is False:
                            if "changelog" in key_data:
                                _data = key_data["changelog"]
                                # grab the change_histories on an issue
                                print(f"Getting history from issue: {val}")
                                add_log(
                                    "Getting history " f"from issue: {val}",
                                    "info",
                                )
                                changelog_history(
                                    _data,
                                    proj=(
                                        val,
                                        project_key,
                                        _summary,
                                    ),
                                )
                                print("*" * 100)
                        else:
                            starter = 0
                            while True:
                                key_data = LOGIN.get(
                                    endpoint.issues(
                                        issue_key_or_id=val,
                                        query="changelog?startAt={}".format(
                                            starter
                                        ),
                                        event=True,
                                    )
                                )
                                loads = json.loads(key_data.content)
                                if starter >= loads["total"]:
                                    break
                                print(f"Getting history from issue: {val}")
                                add_log(
                                    "Getting history " f"from issue: {val}",
                                    "info",
                                )
                                changelog_history(
                                    loads,
                                    proj=(
                                        val,
                                        project_key,
                                        _summary,
                                    ),
                                )
                                print("*" * 100)
                                starter += 100

                if LOGIN.api is False:
                    infinity_counter += 1
                if LOGIN.api is True:
                    infinity_counter = count
                data_brick.update(
                    {
                        "iter": infinity_counter,
                        "key": keys,
                    }
                )
                project_key = keys.split("-")[0]
                json.dump(
                    data_brick,
                    open(
                        f"{path_builder(path=folder, file_name=saved_file)}",
                        encoding="utf-8",
                        mode="w+",
                    ),
                    indent=4,
                ) if allow_cp is True else None
                if back_up is True and keys != set_up["key"] and loop is False:
                    re_instantiate(set_up["key"])

                loop = True
                re_instantiate(keys)

        def changelog_history(
            history: Any = Any,
            proj: tuple = (
                str,
                str,
                str,
            ),
        ) -> None:
            """Structure the change history data after being retrieved.

            :return: None
            """
            _keys = proj[0]
            _summary = proj[2]

            def render_history(
                past,
            ):
                created = ""
                name = ""
                if "author" in past:
                    name = (
                        past["author"]["name"]
                        if "name" in past["author"]
                        else past["author"]["displayName"]
                    )
                if "created" in past:
                    created = past["created"]
                if "items" in past:
                    items = past["items"]
                    for item in items:
                        _field_id = ""
                        _tmpFromAccountId = ""
                        _tmpToAccountId = ""
                        if LOGIN.api is True:
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
                            raw = (
                                [
                                    _field,
                                    _field_type,
                                    _from,
                                    _fromString,
                                    _to,
                                    _toString,
                                ]
                                if LOGIN.api is False
                                else [
                                    _field,
                                    _field_type,
                                    _field_id,
                                    _from,
                                    _fromString,
                                    _to,
                                    _toString,
                                    _tmpFromAccountId,
                                    _tmpToAccountId,
                                ]
                            )
                            item_list.append(raw)
                        elif field_name is None:
                            raw = (
                                [
                                    _field,
                                    _field_type,
                                    _from,
                                    _fromString,
                                    _to,
                                    _toString,
                                ]
                                if LOGIN.api is False
                                else [
                                    _field,
                                    _field_type,
                                    _field_id,
                                    _from,
                                    _fromString,
                                    _to,
                                    _toString,
                                    _tmpFromAccountId,
                                    _tmpToAccountId,
                                ]
                            )
                            item_list.append(raw)

                        ItemList = ( # noqa
                            namedtuple(
                                "ItemList",
                                [
                                    "field",
                                    "field_type",
                                    "from_",
                                    "fromString",
                                    "to",
                                    "toString",
                                ],
                            )
                            if LOGIN.api is False
                            else namedtuple(
                                "ItemList",
                                [
                                    "field",
                                    "field_type",
                                    "field_id",
                                    "from_",
                                    "fromString",
                                    "to",
                                    "toString",
                                    "tmpFromAccountId",
                                    "tmpToAccountId",
                                ],
                            )
                        )

                        for _ in item_list:
                            issue = ItemList._make(_) # noqa
                            # Fix for time in status
                            blank_data(
                                _keys,
                                _summary,
                                issue,
                                name,
                            )
                            raw_vision = (
                                [
                                    _keys,
                                    _summary,
                                    name,
                                    created,
                                    issue.field_type,
                                    issue.field,
                                    issue.from_,
                                    issue.fromString,
                                    issue.to,
                                    issue.toString,
                                ]
                                if LOGIN.api is False
                                else [
                                    _keys,
                                    _summary,
                                    name,
                                    created,
                                    issue.field_type,
                                    issue.field,
                                    issue.field_id,
                                    issue.from_,
                                    issue.fromString,
                                    issue.to,
                                    issue.toString,
                                    issue.tmpFromAccountId,
                                    issue.tmpToAccountId,
                                ]
                            )
                            changes.append(raw_vision)
                        item_list.clear()

                for case in changes:
                    file_writer(
                        folder,
                        file,
                        data=case,
                        mode="a+",
                    )
                changes.clear()
                add_log(
                    f"Clearing history from queue: {_keys}",
                    "info",
                )

            if "histories" in history:
                for change in history["histories"]:
                    render_history(change)
            else:
                if "values" in history:
                    if history["values"] is not None:
                        for change in history["values"]:
                            render_history(change)

        # get a counter of the issue record
        count: Union[str, int] = 0 if LOGIN.api is False else None
        headers = (
            [
                "Issue Key",
                "Summary",
                "Author",
                "Created",
                "Field Type",
                "Field",
                "From",
                "From String",
                "To",
                "To String",
            ]
            if LOGIN.api is False
            else [
                "Issue Key",
                "Summary",
                "Author",
                "Created",
                "Field Type",
                "Field",
                "Field Id",
                "From",
                "From String",
                "To",
                "To String",
                "From AccountId",
                "To AccountId",
            ]
        )
        cycle: int = 0
        # stores our iteration here
        data_brick = {}
        set_up = None
        loop: bool = False
        if allow_cp is True:
            if (
                os.path.isfile(
                    path_builder(
                        folder,
                        file_name=saved_file,
                    )
                )
                and os.stat(
                    path_builder(
                        folder,
                        file_name=saved_file,
                    )
                ).st_size
                != 0
            ):
                user_input = input(
                    "An existing save point exist from your last extraction, "
                    "do you want to use it? (Y/N) \n"
                )
                set_up = json.load(
                    open(
                        path_builder(
                            path=folder,
                            file_name=saved_file,
                        )
                    )
                )
                if user_input.lower() in [
                    "y",
                    "yes",
                ]:
                    back_up = True
                else:
                    print("Starting extraction from scratch.")
                    set_up = None
        descriptor = (
            os.open(
                path_builder(
                    path=folder,
                    file_name=saved_file,
                ),
                flags=os.O_CREAT,
            )
            if allow_cp is True
            else None
        )
        os.close(descriptor) if allow_cp is True else None
        file_writer(
            folder=folder,
            file_name=file,
            data=headers,
            mode="w+",
        ) if set_up is None else None
        depth = 1
        while True:
            load = (
                LOGIN.get(
                    endpoint.search_issues_jql(
                        query=set_up["jql"],
                        start_at=set_up["iter"],
                        max_results=100,
                    ) if LOGIN.api is False else
                    endpoint.search_cloud_issues(
                        query=set_up["jql"],
                        next_page=set_up["iter"],
                        fields=None,
                        max_results=100,
                    )
                )
                if back_up is True and depth == 1
                else LOGIN.get(
                    endpoint.search_issues_jql(
                        query=jql,
                        start_at=count,
                        max_results=100,
                    ) if LOGIN.api is False else
                endpoint.search_cloud_issues(
                query=jql,
                next_page=count,
                    fields=None,
                max_results=100,
                 )
                )
           )

            if load.status_code < 300:
                data = json.loads(load.content)
                cycle = 0
                data_brick.update(
                    {
                        "jql": jql,
                        "iter": set_up["iter"]
                        if back_up is True and depth == 1
                        else count,
                        "save": set_up["save"]
                        if back_up is True and depth == 1
                        else attempt,
                    }
                )
                if LOGIN.api is False:
                    if count > data["total"]:
                        break
                    changelog_search()
                    depth += 1
                if LOGIN.api is True:
                    changelog_search()
                    if "nextPageToken" not in data:
                        break
                    depth += 1
            if LOGIN.api is False:
                count += 100
            if LOGIN.api is True:
                count = load.json().get("nextPageToken", None)
            if depth == 2 and back_up is True:
                count = data_brick["iter"]
            if load.status_code > 300:
                cycle += 1
                if cycle > 99:
                    raise JiraOneErrors(
                        "value",
                        'It seems that the search "{}" cannot be '
                        "retrieved as we've attempted it {} times".format(
                            jql,
                            cycle,
                        ),
                    )

        if show_output is True:
            print(
                "A CSV file has been written to disk, find it here {}".format(
                    path_builder(
                        folder,
                        file_name=file,
                    )
                )
            )
        add_log(
            "File extraction for change log completed",
            "info",
        )
        os.remove(
            path_builder(
                path=folder,
                file_name=saved_file,
            )
        ) if allow_cp is True else None

    @staticmethod
    def async_change_log(
        jql: str,
        *,
        folder: Optional[str] = "ChangeLog",
        file: Optional[str] = "change_log.csv",
        **kwargs: Any,
    ) -> None:
        """Extract the issue history of an issue asynchronously.

        Query the ``changelog`` endpoint if using cloud instance or
        straight away define access to it on server.
        Extract the histories and export it to a CSV file.

        :param jql: (required) A valid JQL query for projects
                    or issues.

        :param folder: A name to a folder where the history file
                      will be stored.

        :param file: A name to the exported file result.


        :param kwargs: The acceptable kwargs that can be passed to the
                       ``async_change_log`` method are given below.
                       Like your ``change_log`` method, this allows some of
                       the same arguments in the ``change_log`` method with
                       some additional arguments that makes its iteration much
                       faster than your regular ``change_log`` method.

               * workers: Datatype(int) The number of thread processes to
                          begin with.

               * timeout: Datatype(float or int) - A number to denote the thread
                          process timeout.

               * field_name: Datatype(str) - Target a field name to render.

               * flush: Datatype(int) - Delay the time, so any running thread
                        can finish.


        :return: None
        """
        from jiraone.utils import (
            DotNotation,
            process_executor,
            validate_on_error,
            validate_argument_name,
        )
        from time import sleep

        valid_kwargs = {
            "folder": "folder",
            "file": "file",
            "workers": "workers",
            "timeout": "timeout",
            "field_name": "field_name",
            "flush": "flush",
        }
        for name_key in kwargs:
            validate_argument_name(name_key, valid_kwargs)

        field_name: str = (
            kwargs.get("field_name") if "field_name" in kwargs else ""
        )
        workers: int = kwargs.get("workers") if "workers" in kwargs else 4
        timeout: Union[
            float,
            int,
        ] = (
            kwargs.get("timeout") if "timeout" in kwargs else 5
        )
        flush: int = kwargs.get("flush") if "flush" in kwargs else 10
        config = {"history": []}
        if not file.endswith(".csv"):
            file = file + ".csv"

        validate_on_error(
            folder,
            (
                str,
                "folder",
                "a string",
            ),
            "a string of the directory path",
        )
        validate_on_error(
            jql,
            (
                str,
                "jql",
                "a string",
            ),
            "a string of a valid JQL",
        )
        validate_on_error(
            file,
            (
                str,
                "file",
                "a string",
            ),
            "a string of the file path",
        )
        validate_on_error(
            field_name,
            (
                str,
                "field_name",
                "a string",
            ),
            "a string of the field name to filter",
        )
        validate_on_error(
            workers,
            (
                int,
                "workers",
                "an integer",
            ),
            "a number to denote the  number of working "
            "threads to start with",
        )
        validate_on_error(
            timeout,
            (
                (
                    float,
                    int,
                ),
                "timeout",
                "a number",
            ),
            "a number to denote the timeout for working threads",
        )
        validate_on_error(
            flush,
            (
                int,
                "flush",
                "an integer",
            ),
            "a number to delay the time it takes "
            "for any running thread to finish",
        )
        # extract the issues then separate by issue keys
        PROJECT.export_issues(
            folder=folder,
            jql=jql,
            final_file=file,
            show_export_link=False,
        )
        file_path = path_builder(
            folder,
            file_name=file,
        )
        read_file = file_reader(
            folder,
            file_name=file,
        )

        def async_history_data(
            history_key: str = None,
        ):
            """Pass an issue key which can be processed asynchronously.

            :param history_key: A Jira issue key

            :return: None
            """
            query = f"key = {history_key}"
            history_folder = f"{folder}/history"
            history_file = f"history_{history_key}.csv"
            PROJECT.change_log(
                folder=history_folder,
                allow_cp=False,
                file=history_file,
                jql=query,
                show_output=False,
                field_name=field_name if field_name else None,
            )
            read_history = file_reader(
                history_folder,
                history_file,
                skip=True,
            )
            history_data = []
            for _history_ in read_history:
                name_mapper = {
                    "issueKey": _history_[0],
                    "summary": _history_[1],
                    "author": _history_[2],
                    "created": _history_[3],
                    "fieldType": _history_[4],
                    "field": _history_[5],
                    "fieldId": _history_[6],
                    "from_": _history_[7],
                    "fromString": _history_[8],
                    "to_": _history_[9],
                    "toString": _history_[10],
                }
                if LOGIN.api is True:
                    name_mapper.update(
                        {
                            "fromAccountId": _history_[11],
                            "toAccountId": _history_[12],
                        }
                    )
                mapper = DotNotation(name_mapper)
                historical_data = [
                    mapper.issueKey,
                    mapper.summary,
                    mapper.author,
                    mapper.created,
                    mapper.fieldType,
                    mapper.field,
                    mapper.fieldId,
                    mapper.from_,
                    mapper.fromString,
                    mapper.to_,
                    mapper.toString,
                ]
                if LOGIN.api is True:
                    historical_data.append(mapper.fromAccountId)
                    historical_data.append(mapper.toAccountId)

                history_data.append(historical_data)
            config["history"].append(
                {
                    "key": history_key,
                    "value": history_data.copy(),
                }
            )

            os.remove(
                path_builder(
                    history_folder,
                    history_file,
                )
            )

        print("Starting history extraction. Please wait...")
        header = [
            "Issue Key",
            "Summary",
            "Author",
            "Created",
            "Field Type",
            "Field",
            "Field Id",
            "From",
            "From String",
            "To",
            "To String",
        ]
        if LOGIN.api is True:
            header.append("From AccountId")
            header.append("To AccountId")
        issue_key_column, count = None, 0
        for column in read_file:
            if count == 0:
                issue_key_column = column.index("Issue key")
                break
            count += 1
        del read_file[0]
        for column in read_file:
            process_executor(
                async_history_data,
                data=column[issue_key_column],
                workers=workers,
                timeout=timeout,
            )

        file_writer(folder, file_name=file, data=header, mode="w+")
        sleep(flush)
        for history_obj in config["history"]:
            file_writer(
                folder,
                file_name=file,
                data=history_obj.get("value"),
                mark="many",
            )
        print(
            "Export completed, historical record located at {}".format(
                file_path
            )
        )

    def comment_on(
        self,
        key_or_id: str = None,
        comment_id: int = None,
        method: str = "GET",
        **kwargs,
    ) -> Any:
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
            load = LOGIN.get(
                endpoint.comment(
                    key_or_id=key_or_id,
                    ids=comment_id,
                    start_at=start_at,
                    max_results=max_results,
                    event=event,
                    query=query,
                )
            )
            data = load.json()

            class ReturnCommentData:
                """Get a list of the data in one chunk."""

                def __init__(
                    self,
                    results,
                ) -> None:
                    """Get all data from a comment field.

                    This calls the comment endpoint and returns a list
                    of the data. Depending on what method you're calling.
                    It is either you call the method ``comment()`` or you call
                    a property within the method.

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

                    :param results: A dict object that loads the result of
                                    comments.

                    """
                    self.data = results
                    self._author = None
                    self._body = None
                    self._update_author = None
                    self._other_fields = None

                def comment(
                    self,
                    type_field: str,
                ) -> Any:
                    """Return a comment field data.

                    :param type_field: A string used to determine which data
                                       to pull

                    options available

                     i) author - the user which triggered the comment
                     ii) body - a comment body
                     iii) updateAuthor - gets the updated author details
                    """
                    for f in self.data["comments"]:
                        if type_field in f:
                            if type_field == "author":
                                self._author = f.get("author")
                                self._other_fields = {
                                    "created": f.get("created"),
                                    "id": f.get("id"),
                                    "jsdPublic": f.get("jsdPublic"),
                                    "self": f.get("self"),
                                    "updated": f.get("updated"),
                                }
                                result_data.append(
                                    {
                                        "author": self._author,
                                        "fieldset": self._other_fields,
                                    }
                                )

                            if type_field == "body":
                                self._body = f.get("body")
                                self._other_fields = {
                                    "created": f.get("created"),
                                    "id": f.get("id"),
                                    "jsdPublic": f.get("jsdPublic"),
                                    "self": f.get("self"),
                                    "updated": f.get("updated"),
                                }
                                result_data.append(
                                    {
                                        "body": self._body,
                                        "fieldset": self._other_fields,
                                    }
                                )

                            if type_field == "updateAuthor":
                                self._update_author = f.get("updateAuthor")
                                self._other_fields = {
                                    "created": f.get("created"),
                                    "id": f.get("id"),
                                    "jsdPublic": f.get("jsdPublic"),
                                    "self": f.get("self"),
                                    "updated": f.get("updated"),
                                }
                                result_data.append(
                                    {
                                        "updateAuthor": self._update_author,
                                        "fieldset": self._other_fields,
                                    }
                                )

                    class Text:
                        """Return the text of data."""

                        pull = deque()

                        def __init__(
                            self,
                        ):
                            """Return the data value when a property is used."""
                            self.result = result_data
                            self._body_ = None
                            self._author_ = None
                            self._text_ = None
                            self._mention_ = None
                            for d in self.result:
                                if "author" in d:
                                    if self._author_ is None:
                                        self.author = [
                                            {
                                                "author": j["author"][
                                                    "displayName"
                                                ],
                                                "accountId": j["author"][
                                                    "accountId"
                                                ],
                                                "active": j["author"]["active"],
                                                "accountType": j["author"][
                                                    "accountType"
                                                ],
                                            }
                                            for j in self.result
                                        ]
                                if "body" in d:
                                    if self._body_ is None:
                                        self.body = [
                                            j.get("body") for j in self.result
                                        ]
                                        (
                                            first_comm,
                                            *_,
                                            last_comm,
                                        ) = self.body
                                        self.last_comment = last_comm
                                        self.first_comment = first_comm

                        @property
                        def author(
                            self,
                        ):
                            """Property of author field.

                            Returns some data set of the author, extracted
                            from the comment.
                            """
                            return self._author_

                        @author.setter
                        def author(
                            self,
                            user,
                        ):
                            """Sets the author field of an object with
                            the dataset."""
                            self._author_ = user

                        @property
                        def body(
                            self,
                        ):
                            """Property of body field.

                            Returns some data set of the body, extracted from
                            the comment.
                            """
                            return self._body_

                        @body.setter
                        def body(
                            self,
                            content,
                        ):
                            """Sets the body field of an object with
                            the dataset."""
                            self._body_ = content
                            for enter in self._body_:
                                if "content" in enter:
                                    for context in enter["content"]:
                                        if "content" in context:
                                            for value in context["content"]:
                                                if self._text_ is None:
                                                    if "text" in value:
                                                        if (
                                                            value["type"]
                                                            == "mention"
                                                        ):
                                                            self.pull.append(
                                                                {
                                                                    "mention": value[
                                                                        "attrs"
                                                                    ],
                                                                    "type": value[
                                                                        "type"
                                                                    ],
                                                                    "text_type": value[
                                                                        "text"
                                                                    ],
                                                                }
                                                            )
                                                        self.pull.append(
                                                            {
                                                                "text": value[
                                                                    "text"
                                                                ],
                                                                "type": value[
                                                                    "type"
                                                                ],
                                                            }
                                                        )

                                                if self._mention_ is None:
                                                    if "type" in value:
                                                        if (
                                                            value["type"]
                                                            == "mention"
                                                        ):
                                                            self.pull.append(
                                                                {
                                                                    "mention": value[
                                                                        "attrs"
                                                                    ],
                                                                    "type": value[
                                                                        "type"
                                                                    ],
                                                                }
                                                            )
                            # will only show value on API v3.
                            self.text = [
                                OrderedDict(
                                    {
                                        "text": a.get("text"),
                                        "type": a.get("type"),
                                    }
                                )
                                for a in self.pull
                                if "text" in a
                            ]
                            # will only show value on API v3.
                            self.mention = [
                                OrderedDict(
                                    {
                                        "mention": a.get("mention"),
                                        "type": a.get("type"),
                                    }
                                )
                                for a in self.pull
                                if "mention" in a
                            ]

                        @property
                        def text(
                            self,
                        ):
                            """Property of text field.

                            Returns some data set of the body text, extracted
                            from the comment.
                            """
                            return self._text_

                        @text.setter
                        def text(
                            self,
                            content,
                        ):
                            """Sets the text field of a body comment with
                            the dataset."""
                            self._text_ = content

                        @property
                        def mention(
                            self,
                        ):
                            """Property of mention field.

                            Returns some data set of the body @mention of
                            a user, extracted from the comment.
                            """
                            return self._mention_

                        @mention.setter
                        def mention(
                            self,
                            content,
                        ):
                            """Sets the text field of a body comment
                            with @mention user with the dataset."""
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
                    text = replacement_placeholder(
                        placer,
                        block,
                        mention,
                        0,
                    )
            # change REST endpoint from 3 to latest, so we
            # can easily post a comment.
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
                                    "type": "text",
                                }
                            ],
                        }
                    ],
                }
            }
            field_text = (
                {"body": text[0]}
                if visible is None and LOGIN.api is False
                else body_content
                if visible is None and LOGIN.api is True
                else {
                    "visibility": {
                        "type": "role",
                        "value": visible,
                    },
                    "body": text[0],
                }
            )
            result = LOGIN.post(
                endpoint.comment(
                    key_or_id=key_or_id,
                    event=event,
                ),
                payload=field_text,
            )
            if result.status_code < 300:
                print("Comment added to {}".format(key_or_id))
            else:
                print(
                    "Comment not added to {}, error: {}".format(
                        key_or_id,
                        result.status_code,
                    )
                )
            block.clear()

    @staticmethod
    def export_issues(
        *,
        folder: Optional[str] = "EXPORT",
        jql: str = None,
        page: Optional[tuple] = None,
        **kwargs: Any,
    ) -> None:
        """
        Exports all Jira issue either in CSV or JSON format based on JQL
        search. If the number of issues returned is greater than 1K issues,
        all the issues are finally combined into a single file as output.

        :param folder: The name of a folder, where files will be stored.

        :param jql: A valid JQL (required) if ``merge_files``
                    args is not provided

        :param page: An iterative counter for page index denoting the
                     pagination for JQL search

        :param kwargs: Additional arguments that can be supplied.

                  **Available options**

                  * temp_file: Datatype (str) A temporary file name
                  when combining the exported file.

                  * final_file: Datatype (str) Name of the final
                  combined CSV or JSON file name.You do not need to add
                  the extension as this is added automatically based on
                  the ``extension`` argument.

                  * target: Datatype (str or dict) Ability to change or get
                  certain values from another instance. If and only if it
                  is the same user who exist on both. As the same
                  authentication needs to be used to extract or create the
                  data else use a dict to construct a login acceptable
                  form that can be used as authentication. This needs to
                  be set for the ``fields`` argument to work properly.

                  When used as a string, just supply the instance base URL
                  as string only.

                  Example::

                     # previous expression
                     base = "https://yourinstance.atlassian.net"


                  Example of dict construct which can be stored as
                  a ``.json`` file.

                  Example::

                     {
                      "user": "prince@example.com",
                      "password": "secretpassword",
                      "url": "https://server.example.com"
                     }


                  * fields: Datatype (list) Ability to alter the row value
                  of a field. Useful when you want to change the value
                  used for imports into Jira. Such as sprint name to id
                  or username to accountId (Server or DC to cloud migration).
                  This argument requires the ``target`` argument to be set
                  first before it can become useful.

                  * encoding: Datatype (str) Ability to alter the encoding
                  of the exported data to ``file_writer`` function.

                  * errors: Datatype (str) Ability to alter the error type used
                  in encoding argument if the encoded character fails to decode.

                  * extension: Datatype (str) Ability to export the issues in
                  either CSV or JSON format. e.g. options are "csv" or "json"

                  Example::

                     # previous statements
                     PROJECT.export_issues(jql=jql, extension="csv")

                  * field_type: Datatype (str) Ability to define if all fields
                  or default fields are exported. e.g. options are "all" or
                  "current". The default is set to "all" for every field.If you
                  want to export only default fields, set it to "current".
                  This will export the default field your current users has
                  defined on the UI.

                  Example::

                     # previous statements
                     my_current_field = "current"
                     PROJECT.export_issues(jql=jql, field_type=my_current_field)

                  * exclude_fields: Datatype (list) Ability to exclude certain
                  fields from the exported file. This field must be an exact
                  string of the custom field name. This argument cannot be used
                  when ``include_fields`` args is not empty

                  Example::

                     # previous statements
                     fields = ["Labels", "Comment", "SupportTeam"]
                     PROJECT.export_issues(jql=jql, exclude_fields=fields)

                  * include_fields: Datatype (list) Ability to include certain
                  fields from the exported file. This field must be an exact
                  string of the custom field name. This argument cannot be
                  used when ``exclude_fields`` is not empty.

                  Example::

                     # previous statements
                     fields = ["Summary", "Comment", "SupportTeam"]
                     PROJECT.export_issues(jql=jql, include_fields=fields)

                  * workers: Datatype (int) Ability to use process workers for
                  faster iterations. This helps during http request to
                  endpoints. By default, 4 threads are put into motion

                  Example::

                     # previous statement
                     workers = 20
                     PROJECT.export_issues(jql=jql, extension="json",
                     workers=workers)

                  * is_sd_internal: Datatype (bool) Ability to add additional
                  properties to a JSON comment export for JSM projects.
                  This argument expects that a comment field column must include
                  an addition string attribute as "true" or "false" specifically
                  tailored for JSM projects.

                  Example::

                     # Given the below is a CSV row of a comment field
                     "25/Apr/22 11:15 AM;
                     557058:f58131cb-b67d-43c7-b30d-6b58d40bd077;
                     Hello this work;true"

                  The last value there "true" will determine the visibility of
                   a comment on a JSM project import.

                  * merge_files: Datatype (list) Ability to combine various CSV
                   files not necessarily Jira related into a single CSV file.
                   You can supply the filename in a list e.g.

                  Example::

                     # previous statements
                     my_files = ["file1.csv", "file2.csv", file3.csv"]
                     PROJECT.export_issues(merge_files=my_files)

                  When merge_files argument is used, it overrides other
                  arguments such as jql, page, encoding and errors.
                  Please ensure that these files are in the same directory as
                   indicated by the ``folder`` argument

                  * csv_to_json: Datatype (str) Ability to provide a CSV Jira
                  export to be converted to JSON format. This argument expects
                  the name of the CSV file name. It expects a "Project key"
                  column to be included in the CSV file.

                  * timeout: Datatype (float or int) Ability to increase the
                  timeout period required for the ``workers`` argument. If you
                  do increase the ``workers`` argument, you have to set a
                  plausible timeout that allows all thread to join
                  and finish executing to prevent errors e.g. KeyError

                  * json_properties: Datatype (list) Ability to add additional
                  properties to the JSON export option such as users or links
                  objects. Examples of valid properties: users, links and
                  history

                  Example::

                     # previous statements
                     props = ["users", "links"]
                     jql = "project in (ABC, IT)"
                     PROJECT.export_issues(jql=jql, extension="json",
                     json_properties=props)

                  * check_auth: Datatype (bool) Ability to turn off or on the
                  authentication check that the export function uses. Only
                  useful when ``merge_files`` argument is used alone.

                  Example::

                     # previous statements
                     my_files = ["file1.csv", "file2.csv", "file3.csv"]
                     PROJECT.export_issues(merge_files=my_files,
                          check_auth=False)

                  * date_format: Datatype (str) Ability to use certain date
                  pattern to parse datetime Jira fields. Useful for datetime
                  custom field

                  Example::

                     # previous statements
                     date_pattern = "%d/%m/%Y %I:%M %p"
                     # The above would translate into dd/MM/YYYY 09:14 AM
                     jql = "project in (ABC, IT)"
                     PROJECT.export_issues(jql=jql, extension="json",
                     date_format=date_pattern)

                  * json_custom_type: Datatype (list) Ability to exclude
                  certain customType from the JSON export. The name has to
                  be an exact string or unique starting string of the custom
                  type. By default, this argument omits two custom type
                  of which one of such custom type is given in the below
                  example

                  Example::

                     # previous statements
                     _type = ["com.atlassian.plugins.atlassian-connect-plugin"]
                     # The above is referring to the custom field type
                     jql = "project in (ABC, IT)"
                     PROJECT.export_issues(jql=jql, extension="json",
                     json_custom_type=_type)

                  * is_cache: Datatype (bool) Ability to save frequently used
                  http call if the same request is done within a given amount
                  of time for faster iterations.

                  * use_cache: Datatype (bool) Ability to use cached http call
                  object at will. This allows the use of previously saved
                  objects. If none exist, a new http call is made and the data
                  is saved as an JSON object used as cache.

                  * is_cache_filename: Datatype (str) Ability to name the file
                  used to store the cached data.

                  * expires: Datatype (int) Ability to add an expiry timeframe
                  to the ``is_cache`` argument expressed in days,
                  which allows caching to be recalled or valid over a period
                  of time in days.

                  Example::

                     # previous statements
                     expiry_time = 30 # number of days
                     jql = "project in (ABC, IT)"
                     PROJECT.export_issues(jql=jql, extension="json",
                     expires=expiry_time, is_cache=True)

                  * allow_media: Datatype (bool) Ability to add a user
                  credential to each attachment uri of the "Attachment" column
                  of a CSV export. This helps to easily append credentials to
                  all rows of the CSV export with your current credentials.

                  * sub_tasks: Datatype (list) Ability to identify all the
                  sub-tasks issues present in a JSON export. Useful when you
                  want to provide issue links between a parent and child issues

                  * project_type - Datatype(dict) Ability to provide a project
                  template for JSON creation based on the project type

                  Example::

                     # previous expression
                     template = {
                     "software":
                     "com.pyxis.greenhopper.jira:gh-simplified-scrum-classic"}
                     PROJECT.export_issues(jql=jql, extension="json",
                     project_type=template)

                  * workflows - Datatype(dict) Ability to provide a map of
                  project key to workflow scheme name that exist on your
                  destination instance.

                  Example::

                     # previous expression
                     # Where ITSEC is the project key
                     workflow = {"ITSEC":"Software Simplified Workflow Scheme"}
                     PROJECT.export_issues(jql=jql, extension="json",
                     workflows=workflow)

                  * flush - Datatype ( float or int) Ability to set a delay
                  period required for running threads to shut down. Required
                  for history extraction.

                  * delimit - Datatype(str) Ability to change the CSV file
                  separator. The default is a comma.

                  Example::

                     # previous import
                     PROJECT.export_issues(jql=jql, extension="csv",
                     delimit=";")

                  * show_export_link - Datatype(bool) Ability to print out
                  the export file link after it completes. Defaults to True


        .. versionchanged:: 0.7.4

        encoding: Helps determine how encoding are handled.

        errors: Helps determine decoding errors are handled.

        .. versionchanged:: 0.7.6

        extension: Determines the file export format in CSV or JSON format.

        field_type: Specifies if export should contain all fields or
        default fields.

        exclude_fields: Exclude certain fields from the exported data in CSV.

        workers: Indicates how many threads to use at a go when
        making http request.

        is_sd_internal: Adds additional properties to a comment field in
        JSON format. This argument expects that a comment field must include
        an addition string attribute as "true" or "false" specifically
        tailored for JSM projects.

        merge_files: Merge series of CSV files into one which are located in
        the same director fed as a list of file names.

        csv_to_json: When supplied a ``dir`` path to Jira CSV file, auto
        converts to Jira JSON form.

        timeout: Used in conjunction with the ``workers`` argument for
        threads wait time.

        json_properties: Used in JSON export to include other attributes to
        the exported file.

        check_auth: Used as a flag to turn on or off Jira auth validation error.

        include_fields: Used to include only certain Jira fields in a
        CSV export.

        date_format: Used to parse datetime custom fields.

        json_custom_type: Used to exclude certain custom field type from
        being added to the export list in JSON format.

        is_cache: Used to cache dict or list result objects that have used
        some http request in the past for faster lookup.

        use_cache: Allow the use of cached objects such as custom fields
        and users objects.

        is_cache_filename: The name of the file used to store cached data.
        It should be in a ``.json`` format.

        expires: Used in conjunction to ``is_cache`` argument to allow the
        caching to be valid over a given period of time.

        allow_media: Allows auth to be added to each media file in a CSV export.

        sub_tasks: Used to identify sub-task names in JSON export.

        project_type: Project template types.

        workflows: Project workflow scheme names.

        flush: Delay timing when threads are still running for history
        extraction.

        .. versionchanged:: 0.7.9

        delimit: Allows the ability to change the CSV file separator

        show_export_link: Allows the ability to print out the exported file link

        :return: None
        :raises: IndexError, AttributeError, KeyError, TypeError, ValueError,
                 JiraOneErrors

        """
        from jiraone.exceptions import (
            JiraOneErrors,
        )
        from jiraone.utils import (
            DotNotation,
            CUSTOM_FIELD_REGEX,
            process_executor,
            DateFormat as Df,
            INWARD_ISSUE_LINK,
            OUTWARD_ISSUE_LINK,
            validate_on_error,
            validate_argument_name,
            check_is_type,
        )
        from copy import (
            deepcopy,
        )
        from jiraone import (
            field,
        )
        from datetime import (
            datetime,
            timedelta,
        )
        import shutil
        import random
        from time import (
            sleep,
        )

        valid_kwargs = {
            "folder": "folder",
            "jql": "jql",
            "page": "page",
            "temp_file": "temp_file",
            "final_file": "final_file",
            "target": "target",
            "encoding": "encoding",
            "errors": "errors",
            "extension": "extension",
            "field_type": "field_type",
            "exclude_fields": "exclude_fields",
            "include_fields": "include_fields",
            "workers": "workers",
            "is_sd_internal": "is_sd_internal",
            "merge_files": "merge_files",
            "csv_to_json": "csv_to_json",
            "timeout": "timeout",
            "json_properties": "json_properties",
            "json_custom_type": "json_custom_type",
            "is_cache": "is_cache",
            "use_cache": "use_cache",
            "is_cache_filename": "is_cache_filename",
            "expires": "expires",
            "allow_media": "allow_media",
            "sub_tasks": "sub_tasks",
            "project_type": "project_type",
            "workflows": "workflows",
            "flush": "flush",
            "fields": "fields",
            "delimit": "delimit",
            "show_export_link": "show_export_link",
            "date_format": "date_format",
            "check_auth": "check_auth",
        }
        # validate the keyword arguments passed to the functions
        for name_keys in kwargs:
            validate_argument_name(name_keys, valid_kwargs)

        check_auth: bool = (
            kwargs["check_auth"] if "check_auth" in kwargs else True
        )
        validate_on_error(
            check_auth,
            (
                bool,
                "check_auth",
                "a boolean to denote true or false",
            ),
            "a boolean to denote true or "
            "false to check the initial authentication",
        )

        if check_auth is True:
            reason = LOGIN.get(endpoint.myself())
            if reason.status_code > 300:
                add_log(
                    "Authentication failed.Please check your credential "
                    "data to determine "
                    "what went wrong with reason: {} & code {}".format(
                        reason.reason,
                        reason.status_code,
                    ),
                    "error",
                )
                raise JiraOneErrors(
                    "login",
                    "Authentication failed. "
                    "Please check your credentials."
                    " Reason: {}".format(reason.reason),
                )
        # check if the target instance is accessible
        source: str = LOGIN.base_url
        target: Union[
            str,
            dict,
        ] = (
            kwargs["target"] if "target" in kwargs else ""
        )
        active: bool = False
        _field_names_: list = (
            kwargs["fields"]
            if "fields" in kwargs
            else [
                "Sprint",
                "Watchers",
                "Reporter",
                "Assignee",
            ]
        )
        temp_file: str = (
            kwargs["temp_file"] if "temp_file" in kwargs else "temp_file.csv"
        )
        final_file: str = (
            kwargs["final_file"] if "final_file" in kwargs else "final_file.csv"
        )
        encoding: str = kwargs["encoding"] if "encoding" in kwargs else "utf-8"
        errors: str = kwargs["errors"] if "errors" in kwargs else "replace"
        extension: str = kwargs["extension"] if "extension" in kwargs else "csv"
        field_type: str = (
            kwargs["field_type"] if "field_type" in kwargs else "all"
        )
        exclude_fields: list = (
            kwargs["exclude_fields"] if "exclude_fields" in kwargs else []
        )

        workers: int = kwargs["workers"] if "workers" in kwargs else 4
        is_sd_internal: bool = (
            kwargs["is_sd_internal"] if "is_sd_internal" in kwargs else False
        )
        # This should override live download of the Jira CSV file merge
        merge_files: list = (
            kwargs["merge_files"] if "merge_files" in kwargs else []
        )
        # This should override live or supplied merge file and simply process
        # the JSON output portion
        csv_to_json: str = (
            kwargs["csv_to_json"] if "csv_to_json" in kwargs else ""
        )

        timeout: Union[
            float,
            int,
        ] = (
            kwargs["timeout"] if "timeout" in kwargs else 2.5
        )

        json_properties: list = (
            kwargs["json_properties"] if "json_properties" in kwargs else []
        )

        # Should not be used when ``exclude_fields`` is not empty
        include_fields: list = (
            kwargs["include_fields"] if "include_fields" in kwargs else []
        )

        date_format: str = (
            kwargs["date_format"]
            if "date_format" in kwargs
            else Df.dd_MMM_yy_hh_MM_AM_PM
        )

        json_custom_type: list = (
            kwargs["json_custom_type"]
            if "json_custom_type" in kwargs
            else [
                "ari:cloud:ecosystem::extension",
                "com.atlassian.plugins.atlassian-connect-plugin",
            ]
        )

        is_cache: bool = kwargs["is_cache"] if "is_cache" in kwargs else True

        use_cache: bool = (
            kwargs["use_cache"] if "use_cache" in kwargs else False
        )

        is_cache_filename: str = (
            kwargs["is_cache_filename"]
            if "is_cache_filename" in kwargs
            else "j1_config.json"
        )

        expires: int = kwargs["expires"] if "expires" in kwargs else 30

        allow_media: bool = (
            kwargs["allow_media"] if "allow_media" in kwargs else False
        )

        sub_tasks: list = (
            kwargs["sub_tasks"] if "sub_tasks" in kwargs else ["Sub-task"]
        )

        project_type: dict = (
            kwargs["project_type"]
            if "project_type" in kwargs
            else {
                "software": "com.pyxis.greenhopper.jira:gh-simplified-scrum-classic",
                "service_desk": "com.atlassian.servicedesk:simplified-it-service-management",
                "business": "com.atlassian.jira-core-project-templates:jira-core-simplified-procurement",
            }
        )

        workflows: dict = kwargs["workflows"] if "workflows" in kwargs else {}

        flush: Union[
            float,
            int,
        ] = (
            kwargs["flush"] if "flush" in kwargs else 5
        )

        # default is always a comma except another character is
        # specified for the CSV export
        delimit: str = kwargs["delimit"] if "delimit" in kwargs else ""

        show_export_link: bool = (
            kwargs["show_export_link"] if "show_export_link" in kwargs else True
        )
        # stores most configuration data using a dictionary
        config = {}

        if merge_files:
            jql = ""
        if csv_to_json:
            jql = ""
            extension = "json"
            if check_auth is False:
                sys.stderr.write("Warning: A valid session to query Jira data"
                                 " is required when using the `csv_to_json` "
                                 "argument.")

        if merge_files and csv_to_json:
            raise JiraOneErrors("errors",
                                "You cannot use both "
                                "`merge_files` and `csv_to_json` at the same"
                                " time as both are mutually exclusive.")

        # Checking that the arguments are passing correct data structure.
        def field_value_check(
            param_field: list = None,
            attr: bool = False,
            attr_plus: bool = False,
        ) -> None:
            """
            Helps to perform validation check for ``fields``,
            ``exclude_fields`` and ``include_fields`` keyword argument.

            :param param_field: keyword argument names

            :param attr: determines the context for `param_field` argument
                         value

            :param attr_plus: Adds context for a 3rd parameter

            :return: None
            """
            validate_on_error(
                param_field,
                (
                    list,
                    "fields"
                    if attr is False and attr_plus is False
                    else "exclude_fields"
                    if attr is True and attr_plus is False
                    else "include_fields",
                    "a list of items",
                ),
                "a list of field names in Jira",
            )

            # validate each field name in the list provided
            if param_field:
                if isinstance(
                    param_field,
                    list,
                ):
                    is_valid = []

                    def map_field(
                        fname: str,
                    ) -> None:
                        """Processes an object of a field value
                        :param fname: A Jira field name
                        :return: None
                        """

                        mapper = field.get_field(fname)
                        if mapper is not None:
                            _data = mapper.get("name")
                            config["map_list"].add(_data)

                    for item_field in param_field:
                        process_executor(
                            map_field,
                            data=item_field,
                            workers=1,
                        )

                    for check_field in param_field:
                        if check_field not in config["map_list"]:
                            is_valid.append(check_field)

                    if len(is_valid) > 0:
                        add_log(
                            'The following name(s) "{}" in the '
                            "field value list "
                            "doesn't seem to exist or cannot be found.".format(
                                ",".join(is_valid)
                            ),
                            "error",
                        )
                        raise JiraOneErrors(
                            "value",
                            "Unable to find initial field, probably such field"
                            ' "{}" doesn\'t exist for {} argument'.format(
                                ",".join(is_valid),
                                (
                                    "fields"
                                    if attr is False and attr_plus is False
                                    else "exclude_fields"
                                    if attr is True and attr_plus is False
                                    else "include_fields"
                                ),
                            ),
                        )

            config["map_list"].clear()

        config["map_list"] = set()
        field_value_check(_field_names_)  # We'll always check this
        field_value_check(
            exclude_fields,
            True,
        )
        field_value_check(
            include_fields,
            False,
            True,
        )
        validate_on_error(
            target,
            (
                (
                    str,
                    dict,
                ),
                "target",
                "a dictionary or a string",
            ),
            "a dictionary of auth items " "or a string of the url",
        )
        validate_on_error(
            temp_file,
            (
                str,
                "temp_file",
                "a string",
            ),
            "a string of the file name",
        )
        validate_on_error(
            final_file,
            (
                str,
                "final_file",
                "a string",
            ),
            "a string of the file name",
        )

        validate_on_error(
            delimit,
            (
                str,
                "delimit",
                "a string",
            ),
            "a string for use as a CSV file separator",
        )

        validate_on_error(
            show_export_link,
            (
                bool,
                "show_export_link",
                "a boolean",
            ),
            "a boolean to allow the export link printed on terminal",
        )

        if delimit:
            if len(delimit) > 1:
                raise JiraOneErrors(
                    "errors",
                    "The delimit argument accepts only a "
                    "single string character.",
                )
        elif delimit == "":
            delimit = ","
            print(
                "Defaulting to comma as CSV separator."
            ) if extension.lower() == "csv" else None

        def check_field_membership(
            param_field: str = None,
            attr: bool = False,
            value_option: list = None,
        ) -> None:
            """
            Checks if an argument is passing the right
            data

            :param param_field: A keyword value argument
            :param attr: A context decision for param_field value
            :param value_option: A membership value to check
            :return: None
            """
            validate_on_error(
                param_field,
                (
                    str,
                    "field_type" if attr is False else "extension",
                    "a string",
                ),
                "a string of the query field configuration",
            )
            if isinstance(
                param_field,
                str,
            ):
                if param_field.lower() not in value_option:
                    add_log(
                        "The `{}` argument seems to be using the wrong "
                        'option value "{}"'
                        ' expecting either "{}" or "{}" as option.'.format(
                            "field_type" if attr is False else "extension",
                            param_field,
                            value_option[0],
                            value_option[1],
                        ),
                        "error",
                    )
                    raise JiraOneErrors(
                        "wrong",
                        'Unrecognized option value in "{}" request'
                        ' value, only "{}" or "{}" options allowed.'.format(
                            "field_type" if attr is False else "extension",
                            value_option[0],
                            value_option[1],
                        ),
                    )

        check_field_membership(
            field_type,
            value_option=[
                "all",
                "current",
            ],
        )
        validate_on_error(
            jql,
            (
                str,
                "jql",
                "a string",
            ),
            "a string of a valid Jira query",
        )
        validate_on_error(
            encoding,
            (
                str,
                "encoding",
                "a string",
            ),
            "a string of a character " "encoding e.g utf-8",
        )
        validate_on_error(
            errors,
            (
                str,
                "errors",
                "a string",
            ),
            "a string of a character encoding " "exception " "e.g. replace",
        )
        validate_on_error(
            workers,
            (
                int,
                "workers",
                "a number",
            ),
            "a number to indicate the worker process",
        )
        validate_on_error(
            is_sd_internal,
            (
                bool,
                "is_sd_internal",
                "a boolean",
            ),
            "a boolean to indicate true or false",
        )
        validate_on_error(
            merge_files,
            (
                list,
                "merge_files",
                "a list",
            ),
            "a list of file names which can be merged",
        )
        validate_on_error(
            csv_to_json,
            (
                str,
                "csv_to_json",
                "a string",
            ),
            "a string of a Jira generated CSV file",
        )

        validate_on_error(
            timeout,
            (
                (
                    float,
                    int,
                ),
                "timeout",
                "a number as integer or " "with a single decimal point",
            ),
            "a number to denote the timeout period",
        )

        validate_on_error(
            json_properties,
            (
                list,
                "json_properties",
                "a list of valid JSON properties"
                " e.g. users, links or history",
            ),
            "a list of valid JSON property for export",
        )

        allowed_props = [
            "users",
            "links",
            "history",
        ]
        for x_json_value in json_properties:
            if x_json_value.lower() not in allowed_props:
                raise JiraOneErrors(
                    "wrong",
                    f'Value "{x_json_value}" does not match '
                    f"the allowed options in the ``json_properties`` argument",
                )

        validate_on_error(
            date_format,
            (
                str,
                "date_format",
                "a str of a date format"
                " e.g. %m/%d/%y %I:%M %p"
                " which translates to "
                " MM/dd/yy h:mm AM",
            ),
            "a str of python's date format directive"
            " or you can import some common ones from"
            " the DateFormat class in jiraone.utils",
        )

        validate_on_error(
            json_custom_type,
            (
                list,
                "json_custom_type",
                "a list of Jira custom field" " type e.g. com.atlassian.xxx",
            ),
            "a list of custom field type available in Jira",
        )

        validate_on_error(
            is_cache,
            (
                bool,
                "is_cache",
                "a boolean of the caching" " mechanism",
            ),
            "a true or false value to the cache mechanism",
        )

        validate_on_error(
            use_cache,
            (
                bool,
                "use_cache",
                "a boolean of the caching" " mechanism",
            ),
            "a true or false value to use the cache mechanism",
        )

        validate_on_error(
            is_cache_filename,
            (
                str,
                "is_cache_filename",
                "a string of the file" " used for caching",
            ),
            "a string used to name the cache file",
        )

        validate_on_error(
            expires,
            (
                int,
                "expires",
                "an integer of the expiry" " period required for caching",
            ),
            "an integer in days for the period of " "caching time",
        )

        validate_on_error(
            allow_media,
            (
                bool,
                "allow_media",
                "an boolean to indicate "
                " whether the user's auth should"
                " be added to an attachment uri",
            ),
            "a boolean to indicate true or false to "
            "allow a user's auth to media uri",
        )

        validate_on_error(
            sub_tasks,
            (
                list,
                "sub_tasks",
                "a list of Sub-task issue " " type name to identify them",
            ),
            "a list of names denoting the issue types "
            " available within an export",
        )

        validate_on_error(
            project_type,
            (
                dict,
                "project_type",
                "a dictionary of Jira's project " " type template name",
            ),
            "a dict of project type template denoting "
            " the name of the project type",
        )

        validate_on_error(
            workflows,
            (
                dict,
                "workflows",
                "a dictionary of Jira's project " " workflow scheme names",
            ),
            "a dict of a workflow scheme name used in " " Jira",
        )

        validate_on_error(
            flush,
            (
                (
                    float,
                    int,
                ),
                "flush",
                "a number to indicate delay "
                " timeout period required for running"
                " threads to shutdown",
            ),
            "a number to indicate what wait time is "
            " required for running threads to shutdown",
        )

        check_field_membership(
            extension,
            attr=True,
            value_option=[
                "csv",
                "json",
            ],
        )
        if page is None:
            pass
        elif page is not None:
            validate_on_error(
                page,
                (
                    tuple,
                    "page",
                    "a tuple",
                ),
                "a tuple to determine valid page index",
            )
            if isinstance(
                page,
                tuple,
            ):
                fix_point = 0
                for index_item in page:
                    answer = "first" if fix_point == 0 else "second"
                    if not isinstance(
                        index_item,
                        int,
                    ):
                        add_log(
                            "The {} `page` argument value seems to be "
                            "using the wrong "
                            "data "
                            "structure {}"
                            "expecting an integer.".format(
                                answer,
                                page,
                            ),
                            "error",
                        )
                        raise JiraOneErrors(
                            "wrong",
                            "The {} `page` argument "
                            "value"
                            " should be an integer "
                            "to loop page records. "
                            "Detected {} instead.".format(
                                answer,
                                type(index_item),
                            ),
                        )
                    if fix_point > 1:
                        add_log(
                            "The `page` argument value seems to be "
                            "more than the expected "
                            "length. Detected {} values."
                            "".format(len(page)),
                            "error",
                        )
                        raise JiraOneErrors(
                            "wrong",
                            "The `page` argument "
                            "should not have more"
                            " than 2 values. You "
                            "seem "
                            "to have added {} "
                            "so far."
                            "".format(len(page)),
                        )

                    fix_point += 1

        target_option = (
            {
                "user": target.get("user"),
                "password": target.get("password"),
                "url": target.get("url"),
            }
            if isinstance(
                target,
                dict,
            )
            else target
        )
        source_option = {
            "user": LOGIN.user,
            "password": LOGIN.password,
            "url": LOGIN.base_url,
        }
        LOGIN.base_url = (
            target_option.get("url")
            if isinstance(
                target,
                dict,
            )
            else target
        )
        if target != "":
            if isinstance(
                target,
                dict,
            ):
                LOGIN(**target_option)
            locate = LOGIN.get(endpoint.myself())
            if locate.status_code > 300:
                add_log(
                    "Authentication failed to target instance."
                    "Please check your "
                    "credential data to determine what went wrong "
                    "with reason {}"
                    ".".format(locate.json()),
                    "error",
                )
                raise JiraOneErrors(
                    "login",
                    "Authentication failed to "
                    "target instance. "
                    "Please check your credentials."
                    "Reason:{}.".format(locate.reason),
                )
            else:
                active = True
        source_option["url"] = source
        LOGIN(**source_option)
        (
            rows,
            total,
            validate_query,
        ) = (
            0,
            0,
            LOGIN.get(endpoint.search_issues_jql(jql)
                if LOGIN.api is False else
                endpoint.search_cloud_issues(jql)),
        )
        (
            init,
            limiter,
        ) = (
            0,
            0,
        )

        if csv_to_json != "":
            merge_files.append(csv_to_json)

        if not merge_files:
            if validate_query.status_code < 300:
                if LOGIN.api is False:
                    total = validate_query.json()["total"]
                elif LOGIN.api is True:
                    total = LOGIN.post(
                endpoint.search_issue_count(), payload={
                    "jql": jql
                }
            ).json()["count"]
            else:
                add_log(
                    "Invalid JQL query received. Reason {} with status code: "
                    "{} and addition info: {}".format(
                        validate_query.reason,
                        validate_query.status_code,
                        validate_query.json(),
                    ),
                    "debug",
                )
                raise JiraOneErrors(
                    "value",
                    "Your JQL query seems to be invalid"
                    " as no issues were returned.",
                )
            calc = int(total / 1000)
            # We assume each page is 1K that's downloaded.
            (
                limiter,
                init,
            ) = (
                total,
                rows,
            )
            if page is not None:
                assert page[0] > -1, (
                    "The `page` argument first "
                    "range "
                    "value {}, is lesser than 0 "
                    "which is practically wrong.".format(page[0])
                )
                assert page[0] <= page[1], (
                    "The `page` argument first "
                    "range "
                    "value, should be lesser than "
                    "the second range value of {}.".format(page[1])
                )
                assert page[1] <= calc, (
                    "The `page` argument second "
                    "range "
                    "value {}, seems to have "
                    "exceed the issue record range "
                    "searched.".format(page[1])
                )

                limiter = (page[1] + 1) * 1000
                init = page[0] * 1000

        if exclude_fields and include_fields:
            raise JiraOneErrors(
                "wrong",
                "The ``exclude_fields`` and ``include_fields`` "
                "arguments "
                "cannot be used at the same time.",
            )

        if extension.lower() == "json":
            if exclude_fields:
                raise JiraOneErrors(
                    "wrong",
                    "You cannot use the JSON export function if Jira"
                    " fields are being excluded. Please remove the "
                    " `exclude_fields` argument.",
                )
            elif include_fields:
                raise JiraOneErrors(
                    "wrong",
                    "You cannot use the JSON export function if Jira"
                    " fields are being included. Please remove the "
                    " `include_fields` argument.",
                )
            elif field_type.lower() != "all":
                raise JiraOneErrors(
                    "wrong",
                    "You cannot use the JSON export function, if Jira"
                    " fields are not exported properly. "
                    'Please use the "all" option '
                    "in the `field_type` argument or remove it completely.",
                )

        (
            print(
                "Downloading issue export in {} format.".format(
                    extension.upper()
                )
            )
            if show_export_link
            else ""
        )
        file_deposit = []

        def download_csv() -> None:
            """Generate a CSV file from JQL"""
            nonlocal init
            while True:
                if init >= limiter:
                    break
                file_name = temp_file.split(".")[0] + f"_{init}.csv"
                issues = (
                    LOGIN.get(
                        endpoint.issue_export(
                            jql,
                            init,
                        )
                    )
                    if field_type.lower() == "all"
                    else LOGIN.get(
                        endpoint.issue_export(
                            jql,
                            init,
                            fields="current",
                        )
                    )
                )
                print(
                    issues,
                    issues.reason,
                    "::downloading issues at page: " f"{int(init / 1000)}",
                    "of {}".format(int((limiter - 1) / 1000)),
                ) if show_export_link is True else ""
                file_writer(
                    folder,
                    file_name,
                    content=issues.content.decode(
                        encoding,
                        errors=errors,
                    ),
                    mark="file",
                    mode="w+",
                )
                # create a direct link to the new file
                # ensure that there's a unique list as the names are different.
                if file_name not in file_deposit:
                    file_deposit.append(file_name)
                config.update({"exports": file_deposit})
                init += 1000

        download_csv() if not merge_files else config.update(
            {"exports": merge_files}
        )

        (
            config["prev_list"],
            config["next_list"],
            config["set_headers_main"],
            config["make_file"],
            config["set_file"],
        ) = (
            [],
            [],
            [],
            [],
            [],
        )

        config["is_valid"] = False
        (
            sprint_custom_id,
            config["sprint_cf"],
        ) = (
            field.search_field("Sprint"),
            None,
        )
        config["json_props_options"] = [x.lower() for x in json_properties]
        config["user_data_group"] = {}

        def parse_media(
            uri: str,
        ) -> str:
            """
            Parse a URL string to include the
            credential of the URI

            :param uri: An attachment URI
            :return: str
            """
            if uri.startswith("http") or uri.startswith("https"):
                rem_http = uri.split("://")
                user_id = (
                    LOGIN.user.split("@") if LOGIN.api is True else LOGIN.user
                )
                auth_uri = (
                    f"{rem_http[0]}://{user_id[0]}%40{user_id[1]}:"
                    f"{LOGIN.password}@{rem_http[-1]}"
                    if LOGIN.api is True
                    else f"{rem_http[0]}://{user_id}:"
                    f"{LOGIN.password}@{rem_http[-1]}"
                )
                return auth_uri

        def get_pkey_index(
            pkey: list,
            key: str,
            key_search: list,
            attr: bool = False,
        ) -> int:
            """
            Return the index of the column key

            :param pkey: A list of dict values
            :param key : A key name to search
            :param key_search: An object search name
            :param attr: Change context of operations
            :return: int
            """

            for item in pkey:
                if attr is True:
                    if item.get("column_name") == key:
                        config[key_search[0]][key_search[1]].append(
                            item.get("column_index")
                        )
                else:
                    if item.get("column_name") == key:
                        config[key_search[0]][key_search[1]] = item.get(
                            "column_index"
                        )
                        config["is_valid"] = True
                        return config[key_search[0]][key_search[1]]
            return config[key_search[0]][key_search[1]]

        # Get an index of all columns within the first file
        # Then use it across other files in the list
        def data_frame(
            files_: str = None,
            activate: bool = True,
            poll: list = None,
            **kwargs,
        ) -> None:
            """Check each column width of each CSV file,
            get the name of the column and index number
            which can be called with `config["headers"]`.

            :param files_: A name to files

            :param activate: A validator

            :param poll: A poll data link, usually a list of items

            :param kwargs: Additional arguments which can be supplied

            :return: None
            """
            columns = (
                file_reader(
                    folder,
                    files_,
                    **kwargs,
                )
                if activate is True
                else poll
            )
            (
                column_count,
                config["headers"],
            ) = (
                0,
                [],
            )
            for column_ in columns:
                each_col_count = 0
                for each_col in column_:
                    # define the name and index of each column
                    value = {
                        "column_name": each_col,
                        "column_index": each_col_count,
                    }
                    config["headers"].append(value)
                    each_col_count += 1
                column_count += 1
                if column_count == 1:
                    break

        file_path_directory = config["exports"]
        # build headers
        (
            column_headers,
            headers,
            max_col_length,
        ) = (
            [],
            {},
            0,
        )

        def write_files(
            files_: str,
            push: list = None,
        ) -> None:
            """Creates the header file.

            :param files_: The name to the file

            :param push: Holds a list of iterable data

            :return: None
            """

            # create a temp csv file with the header of the export

            def create_file(
                **kwargs,
            ) -> None:
                """
                Create multiple files or data points.

                :param kwargs: Additional supplied arguments
                :return: None
                """

                nonlocal max_col_length, headers, column_headers
                data_frame(**kwargs) if push is not None else data_frame(files_)
                (
                    column_headers,
                    headers,
                    max_col_length,
                ) = (
                    [],
                    DotNotation(value=config["headers"]),
                    0,
                )
                for header in headers.value:
                    column_headers.append(header.column_name)
                    max_col_length += 1

            def make_file(
                modes: str,
                data: list,
            ) -> None:
                """Writes a list into a File<->like object.

                :param modes: A writing mode indicator

                :param data: A data of items, usually a List[list]

                :return: None
                """
                file_writer(
                    folder,
                    temp_file,
                    data=data,
                    mark="many",
                    mode=modes,
                )

            def make_headers_mark() -> None:
                """Make and compare headers then recreate a new header.
                Mostly mutates the config<>object

                :return: None
                """
                # This should contain the data of the next column
                config["next_list"] = column_headers
                create_file(
                    activate=False,
                    poll=copy_temp_read,
                )
                # Because of the above, the column_headers should differ
                # It should contain the previous data and header
                config["prev_list"] = column_headers

                def column_check(
                    first_list: list,
                    second_list: list,
                    _count_: int = 0,
                ) -> None:
                    """Determine and defines the column headers.

                    :param first_list: A list of the previous headers

                    :param second_list: A list of the next headers

                    :param _count_: An iteration counter

                    :return: None
                    """

                    def column_populate(
                        name_of_field: str = None,
                        ticker: int = None,
                    ) -> None:
                        """Receives a column count list with index.
                        which are inserted and arranged properly
                        into a new headers list.

                        :param name_of_field: The name of a column

                        :param ticker: An iteration counter of each
                        element in the headers

                        :return: None
                        """
                        config["set_headers_main"].insert(
                            ticker,
                            name_of_field,
                        )

                    def determine_value(
                        value: str,
                    ) -> int:
                        """Determines how the headers of two files
                        are merged. By taking which ever file has
                        more element in the headers.
                        If the column name is on multiple columns, just
                        suggest that name as a new column in the new
                        header.

                        :param value: A string value of a column name

                        :return: None
                        """
                        next_occurrence = config["next_list"].count(value)
                        prior_occurrence = config["prev_list"].count(value)
                        _plus_value = None
                        if next_occurrence > prior_occurrence:
                            _plus_value = prior_occurrence
                        elif prior_occurrence > next_occurrence:
                            _plus_value = next_occurrence
                        else:
                            _plus_value = prior_occurrence
                        _main_value = (
                            int(abs(next_occurrence - prior_occurrence))
                            + _plus_value
                        )
                        return _main_value

                    def call_column(
                        items: list,
                    ) -> None:
                        """Populate a new column to the list
                        by determining how many exist from the
                        previous and next headers.

                        :param items: A list of elements, mostly
                        header's item

                        :return: None
                        """
                        nonlocal _count_

                        check_value = config["set_headers_main"]
                        for col_list in items:
                            value_id = determine_value(col_list)
                            check = config["set_headers_main"].count(col_list)

                            if col_list not in check_value:
                                column_populate(
                                    col_list,
                                    _count_,
                                )
                            elif col_list in check_value and check < value_id:
                                column_populate(
                                    col_list,
                                    _count_,
                                )
                            _count_ += 1
                        _count_ = 0

                    # do a loop through the first columns
                    call_column(first_list)
                    # call the 2nd column after the first
                    call_column(second_list)
                    # Why call `call_column` twice instead of recursion?
                    # - That would mean creating more variables with 2-3
                    # - lines of additional codes. It's simpler this way.

                column_check(
                    config["prev_list"],
                    config["next_list"],
                )

                def populate_column_data(
                    column_data: list,
                    attr: bool = False,
                ) -> list:
                    """Tries and populate each rows
                    By first getting the headers and the rows beneath it
                    then adding the value of the column by rows.
                    The logic below is a complete accurate
                    1:1 addition of column=>row mechanism of a flattened
                    file structure into a dictionary structure.

                    :param column_data: The header column data to be
                    processed

                    :param attr: A conditional attribute used to determine
                    logic

                    :return: List, usually a list of new elements with
                    corresponding data.
                    """

                    header_choice = (
                        config["prev_list"]
                        if attr is False
                        else config["next_list"]
                    )

                    def load_count(
                        my_list: list,
                        conf: list,
                    ) -> list:
                        """Loads a list into a dictionary of
                        values arranged by their column name.

                        :param my_list: A list of elements

                        :param conf: A new list to return

                        :return: List

                        """
                        nums = 0
                        for main in my_list:
                            props = {
                                "column_index": nums,
                                "column_name": main,
                                "column_data": [],
                            }
                            conf.append(props)
                            nums += 1
                        return conf

                    (
                        pre_config,
                        after_config,
                    ) = (
                        [],
                        [],
                    )
                    my_value = load_count(
                        config["set_headers_main"],
                        pre_config,
                    )
                    other_value = load_count(
                        header_choice,
                        after_config,
                    )
                    # run a loop through the data and assign each value
                    # to their appropriate header

                    locking = deepcopy(header_choice)
                    read_lock = len(locking)
                    (
                        box_item,
                        box_count,
                    ) = (
                        0,
                        deepcopy(column_data),
                    )
                    iter_count = len(box_count)
                    for items in column_data:
                        if box_item >= iter_count:
                            break
                        my_item = 0
                        for (
                            that_row,
                            inner_item,
                        ) in zip(
                            other_value,
                            items,
                        ):
                            if my_item >= read_lock:
                                break
                            # select everything from first row to last row
                            if that_row["column_index"] == my_item:
                                that_row["column_data"].append(inner_item)
                            my_item += 1
                        box_item += 1

                    # Now we have a mapping of all data,the way they should be
                    # But we need to transfer that data to `my_value` variable
                    keep_track = set()  # used to keep track of multiple column

                    def bind_us() -> list:
                        """This helps to align the rows to columns

                        :return: List
                        """

                        # where the values are
                        for new_row in other_value:
                            # where we need the values to be
                            check_name = locking.count(new_row["column_name"])
                            for this_row in my_value:
                                if check_name == 1:
                                    if (
                                        this_row["column_name"]
                                        == new_row["column_name"]
                                    ):
                                        this_row["column_data"] = new_row[
                                            "column_data"
                                        ]
                                        break
                                elif check_name > 1:
                                    if (
                                        this_row["column_name"]
                                        == new_row["column_name"]
                                    ):
                                        if (
                                            this_row["column_index"]
                                            not in keep_track
                                        ):
                                            keep_track.add(
                                                this_row["column_index"]
                                            )
                                            this_row["column_data"] = new_row[
                                                "column_data"
                                            ]
                                            break
                                        else:
                                            continue

                        return my_value

                    bind_us()
                    lock = deepcopy(my_value)
                    (
                        get_range,
                        index,
                    ) = (
                        0,
                        0,
                    )
                    for i in lock:
                        # Use the first index field as a basis to determine
                        # The length of the dataset.
                        if i["column_index"] == index:
                            get_range = len(i["column_data"])
                    block = get_range
                    # Adding a null value to each empty cell
                    # This way, if we read it, we know we won't
                    # Get an index error due to variable length
                    for this_item in my_value:
                        value_ = len(this_item["column_data"])
                        if value_ == 0:
                            runner = 0
                            for i in range(block):
                                if runner >= block:
                                    break
                                data = None
                                this_item["column_data"].append(data)
                                runner += 1

                    return my_value

                def data_provision(
                    make_item: list,
                    attr: bool = False,
                ) -> None:
                    """Add the column data into a list.
                    Here we split the header and the data into
                    columns for [headers] -> vertical view
                    rows for [data] -> horizontal view

                    HEADER + HEADER +   HEADER  +      HEADER +
                     ------+--------+-----------+-------------+
                       A   +   B    +      C    +       D     +
                     ------+--------+-----------+-------------+
                       E   +   F    +      G    +       H     +
                     ------+--------+-----------+-------------+
                       I   +   J    +      K    +       L     +
                     ------+--------+-----------+-------------+

                    Each element in a list of data is assumed a 1
                    value in a row then each row is skipped for the
                    next item in the iteration.
                    While the next item is assumed as next column
                    The same step is repeated in the loop until the
                    steps, are exhausted.

                    :param make_item: A list of element containing the
                    CSV data items

                    :param attr: A conditional logic flow

                    :return: None
                    """
                    # checks the headers and maps the data
                    # to the headers
                    cook_item = populate_column_data(
                        make_item,
                        attr,
                    )
                    look_up = DotNotation(value=cook_item)
                    stop_loop = 0
                    _limit_copy = deepcopy(config["set_headers_main"])
                    _limit = len(_limit_copy)
                    (
                        inner_stop,
                        finish_loop,
                    ) = {
                        "num": 0
                    }, len([row for row in make_item])
                    # The below adds the values as they are gotten
                    # from a dictionary object
                    while True:
                        if stop_loop >= finish_loop:
                            break
                        for _item in range(_limit):
                            if inner_stop["num"] >= _limit:
                                inner_stop.update({"num": 0})
                                break
                            for find_item in look_up.value:
                                if inner_stop["num"] >= _limit:
                                    break
                                for _names in [
                                    config["set_headers_main"][
                                        inner_stop["num"]
                                    ]
                                ]:
                                    if find_item.column_name == _names:
                                        data_brick = find_item.column_data[
                                            stop_loop
                                        ]
                                        config["set_file"].append(data_brick)
                                        inner_stop["num"] += 1
                                        break

                        mutate = deepcopy(config["set_file"])
                        config["make_file"].append(mutate)
                        config["set_file"].clear()
                        stop_loop += 1

                    look_up.clear()  # clear all used list items from memory

                # populate the first list with prev data
                del copy_temp_read[0]  # remove the headers
                data_provision(
                    copy_temp_read,
                    attr=False,
                )
                # populate the second list with current data
                del push[0]  # remove the headers
                data_provision(
                    push,
                    attr=True,
                )
                # Why call `data_provision` twice instead of recursion?
                # - That would mean creating more variables and 2-3 lines of
                # - additional codes. It's simpler this way.

            create_file(files_=files_)
            if push is not None:
                # This denotes the current temp_file
                copy_temp_read = file_reader(
                    folder,
                    temp_file,
                )
                make_headers_mark()
                # This should construct the next CSV file headers
                make_file(
                    "w+",
                    [config["set_headers_main"]],
                )
                # `push` contains the next data_list to be written
                make_file(
                    "a+",
                    config["make_file"],
                )
            # clear all the previous values stored in memory
            column_headers.clear()
            config["set_headers_main"].clear()
            config["make_file"].clear()

        payload = []
        length = max_col_length  # keep track of the column width

        def merging_files() -> None:
            """Merge each files and populate it into one file.

            :return: None
            """
            (
                iteration,
                progress,
            ) = (
                0,
                0,
            )
            for files in file_path_directory:
                current_value = len(file_path_directory)
                (
                    read_original,
                    start_,
                ) = (
                    file_reader(
                        folder,
                        files,
                    ),
                    0,
                )
                copy_read = deepcopy(read_original)
                table_length = len([row for row in copy_read])
                for column in read_original:
                    # break out of loop once we reach the end of the file
                    if start_ == table_length:
                        break
                    payload.append(column)
                    start_ += 1
                if iteration == 0:
                    # write the headers only
                    write_files(files_=files)
                    # add the content into the temp file and populate the rows
                    file_writer(
                        folder,
                        temp_file,
                        data=payload,
                        mark="many",
                        mode="a+",
                    )
                else:
                    # process the next list of files here
                    write_files(
                        files_=files,
                        push=payload,
                    )
                payload.clear()
                iteration += 1
                progress += 1
                current_progress = 100 * progress / current_value
                print(
                    "Processing. "
                    "Current progress: {}%".format(int(current_progress))
                )

        merging_files()  # loop through each file and attempt combination

        if active is True:
            # TODO: Remove this block of code in future or refactor it
            """The solution here is
            # TODO: get the export file and rewrite those field name values
            # TODO: get the users from target environment, get all sprint names
            # TODO: in the current export, translate to sprint id,
            # TODO: username to accountId
            """
            # Change the field name to field id
            # If the field is supported such as sprint or user_picker fields
            field_name = _field_names_
            if isinstance(
                target,
                dict,
            ):
                LOGIN(**target_option)
            else:
                LOGIN.base_url = target
            (
                read_file,
                start,
            ) = (
                file_reader(
                    folder,
                    temp_file,
                    **kwargs,
                ),
                0,
            )
            copy_total = deepcopy(read_file)
            total_ = len([row for row in copy_total])
            # get all the field value in the csv file
            (
                field_list,
                config["fields"],
                config["saves"],
            ) = (
                [],
                [],
                [],
            )
            (
                field_data,
                cycle,
                field_column,
            ) = (
                set(),
                0,
                [],
            )
            data_frame(
                activate=False,
                poll=read_file,
            )
            (
                column_headers,
                max_col_length,
                headers,
            ) = (
                [],
                0,
                DotNotation(value=config["headers"]),
            )
            for header in headers.value:
                column_headers.append(header.column_name)
                max_col_length += 1

            def populate(
                name: str,
            ) -> None:
                """Creates a field name column index
                :param name: A field name
                :return: None
                """
                for _id_ in headers.value:
                    if _id_.column_name == name:
                        field_column.append(_id_.column_index)

            def reset_fields() -> None:
                """Reset field values.

                :return: None
                """

                nonlocal read_file, start, copy_total, total_, field_list, field_data, cycle, field_column

                (
                    read_file,
                    start,
                ) = (
                    file_reader(
                        folder,
                        temp_file,
                        **kwargs,
                    ),
                    0,
                )
                copy_total = deepcopy(read_file)
                total_ = len([row for row in copy_total])
                # get all the field value in the csv file
                (
                    field_list,
                    config["fields"],
                    config["saves"],
                ) = (
                    [],
                    [],
                    [],
                )
                (
                    field_data,
                    cycle,
                    field_column,
                ) = (
                    set(),
                    0,
                    [],
                )

            def check_id(
                _id: int,
                _iter: list,
            ) -> bool:
                """Return true if item exist in list.
                :param _id: An id in a list
                :param _iter: An iterable data

                :return: bool
                """
                if _id in _iter:
                    return True
                return False

            def check_payload(
                data: Union[
                    dict,
                    list,
                ]
            ) -> Union[dict, list,]:
                """Return the value of a field.
                :param data: A data field

                :return: dict or list
                """
                if isinstance(
                    data,
                    list,
                ):
                    # used for sprint fields
                    _data = data[0]
                    _result = {
                        "field_name": _data["name"],
                        "field_id": _data["id"],
                    }
                    return _result
                if isinstance(
                    data,
                    dict,
                ):
                    # used to extract watchers' list
                    my_watch = []
                    if names == "Watchers":
                        watchers = data["watchers"]
                        if watchers != 0:
                            for _name_ in watchers:
                                _result_ = {
                                    "field_name": _name_["displayName"],
                                    "field_id": _name_["accountId"]
                                    if LOGIN.api is True
                                    else data["name"],
                                }
                                my_watch.append(_result_)
                            return my_watch
                    else:
                        # used for any other user field
                        _result_ = {
                            "field_name": data["displayName"],
                            "field_id": data["accountId"]
                            if LOGIN.api is True
                            else data["name"],
                        }
                        return _result_

            def get_watchers(
                name: str,
                key: Union[
                    str,
                    int,
                ],
            ) -> list:
                """
                Return a list of watchers
                :param name: A watcher field
                :param key: An issue key
                :return: dict
                """
                get_issue = field.get_field_value(
                    name,
                    key,
                )
                get_watch = LOGIN.get(get_issue["self"]).json()
                return get_watch

            def field_change() -> None:
                """Recursively check field columns and rewrite values.
                :return: None
                """
                nonlocal field_list, start, cycle
                for columns_ in read_file:

                    def check_field() -> None:
                        """Check field values
                        :return: None
                        """
                        print(
                            "Converting {} name to {} id on outfile "
                            "from {}".format(
                                names,
                                names,
                                LOGIN.base_url,
                            )
                        )
                        for _field_item in field_list:
                            _fields_ = LOGIN.get(
                                endpoint.search_issues_jql(
                                    field_search.format(field_name=_field_item)
                                ) if LOGIN.api is False else
                                endpoint.search_cloud_issues(
                                    field_search.format(field_name=_field_item)
                                )
                            )
                            if _fields_.status_code < 300:
                                issues_ = _fields_.json()["issues"]
                                for keys in issues_:
                                    if "key" in keys:
                                        key = keys["key"]
                                        get_id = (
                                            field.get_field_value(
                                                names,
                                                key,
                                            )
                                            if names != "Watchers"
                                            else get_watchers(
                                                names,
                                                key,
                                            )
                                        )
                                        value_ = check_payload(get_id)
                                        config["fields"].append(value_)
                                        break
                            else:
                                print(
                                    "It seems like the {} name: {} "
                                    "doesn't exist here".format(
                                        names,
                                        _field_item,
                                    )
                                )

                    def check_columns(
                        _max_length: int,
                    ) -> None:
                        """
                        Determines the columns of the CSV file

                        :param _max_length: Max length of issue column
                        :return: None
                        """
                        for rows_ in columns_:
                            if _max_length == length:
                                break
                            if start > 0:
                                if (
                                    check_id(
                                        _max_length,
                                        field_column,
                                    )
                                    and rows_ != ""
                                    and cycle == 0
                                ):
                                    values = columns_[_max_length]
                                    field_data.add(values)
                                if (
                                    check_id(
                                        _max_length,
                                        field_column,
                                    )
                                    and rows_ != ""
                                    and cycle == 1
                                ):
                                    get_value = (
                                        [
                                            name.get("field_id")
                                            for name in config["fields"]
                                            if name.get("field_name")
                                            == columns_[_max_length]
                                        ]
                                        if names != "Watchers"
                                        else [
                                            name.get("field_id")
                                            for data_field in config["fields"]
                                            for name in data_field
                                            if name.get("field_name")
                                            == columns_[_max_length]
                                        ]
                                    )
                                    if len(get_value) != 0:
                                        columns_[_max_length] = get_value[0]
                            _max_length += 1
                        if cycle == 1:
                            config["saves"].append(columns_)

                    max_length = 0
                    check_columns(max_length)
                    field_list = list(tuple(field_data))
                    start += 1
                    if start == total_:
                        if cycle == 0:
                            check_field()
                            cycle += 1
                            start = 0
                            field_change()
                        break
                file_writer(
                    folder,
                    temp_file,
                    data=config["saves"],
                    mark="many",
                    mode="w+",
                )

            for names in field_name:
                try:
                    field_search = '{} = "{}"'.format(
                        names.lower() if names != "Watchers" else "watcher",
                        "{field_name}",
                    )
                    populate(names)
                    field_change()
                    reset_fields()
                except AttributeError as error:
                    sys.stderr.write(f"{error}")

        def caching(
            name_field: str,
            obj_type: Union[
                dict,
                list,
            ],
        ) -> None:
            """
            Creates a caching check by depositing the time,
            and instance that was used during the
            last check along with the object data.
            Works specifically for JSON export

            :param name_field: The name used to save the cache
            :param obj_type: An object that is saved

            :return: None
            """
            if os.path.isdir(folder):
                file_path = path_builder(
                    folder,
                    is_cache_filename,
                )
                data_dump = {name_field: {}}
                if os.path.isfile(file_path):
                    read_json = json.load(
                        open(
                            file_path,
                            encoding=encoding,
                        )
                    )
                    if read_json:
                        data_dump.update(read_json)
                    data_dump.get(name_field).update(
                        {
                            "name": LOGIN.base_url,
                            "value": obj_type,
                            "time": datetime.strftime(
                                datetime.astimezone(
                                    datetime.now() + timedelta(days=expires)
                                ),
                                Df.YYYY_MM_dd_HH_MM_SS_MS,
                            ),
                        }
                    )
                    json.dump(
                        data_dump,
                        open(
                            file_path,
                            mode="w+",
                            encoding=encoding,
                        ),
                        indent=4,
                        sort_keys=True,
                    )
                else:
                    descriptor = os.open(
                        file_path,
                        flags=os.O_CREAT,
                    )
                    os.close(descriptor)
                    _data_ = {}
                    json.dump(
                        _data_,
                        open(
                            file_path,
                            mode="w+",
                            encoding=encoding,
                        ),
                    )

        def is_file_exist(
            cache_file: str = None,
        ) -> bool:
            """
            Checks and updates the object from cache based
            on the name it was saved. If found updates
            the object and returns true. If not found, returns
            false and does nothing.

            :param cache_file: A string of the name used to cache
            the object.

            :return: bool
            """

            if os.path.isdir(folder):
                file_path = path_builder(
                    folder,
                    is_cache_filename,
                )
                if os.path.isfile(file_path):
                    load_file = json.load(
                        open(
                            file_path,
                            encoding=encoding,
                        )
                    )
                    if cache_file in load_file:
                        get_cache_name = load_file[cache_file]
                        current_time = datetime.today()
                        parse_time = datetime.strptime(
                            get_cache_name["time"],
                            Df.YYYY_MM_dd_HH_MM_SS_MS,
                        )
                        if (
                            get_cache_name["name"] == LOGIN.base_url
                            and current_time < parse_time
                        ):
                            if cache_file == "custom_fields":
                                config["headers"] = get_cache_name["value"]
                                return True
                            elif cache_file == "users":
                                for _items_ in get_cache_name["value"]:
                                    config["json_userlist"].append(_items_)
                                return True
            return False

        # Verify each field exist in Jira
        # Then rewrite the name to be suitable in JSON format
        def float_fields(
            field_names: dict,
            regex_pattern: str,
        ) -> None:
            """
            Submit some Jira field data for a search
            and get the field's properties.

            :param field_names: A name to a Jira field
            :param regex_pattern: A regex pattern for custom
            fields

            :return: None
            """
            field_copy = deepcopy(field_names["column_name"])
            config["headers"][field_names["column_index"]][
                "field_column_name"
            ] = field_copy
            if field_names["column_name"].startswith("Custom field"):
                search_name = re.compile(
                    regex_pattern,
                    re.I,
                )
                find_name = search_name.search(field_names["column_name"])
                name_found = None
                if find_name is not None:
                    name_found = find_name.group(2)

                if name_found is not None:
                    jira_field_name = name_found.lstrip("(").rstrip(")")
                    map_name = field.get_field(jira_field_name)

                    if map_name is None:
                        pass
                    else:
                        config["headers"][field_names["column_index"]][
                            "column_name"
                        ] = map_name.get("id")
                        config["headers"][field_names["column_index"]][
                            "original_name"
                        ] = map_name.get("name")
                        config["headers"][field_names["column_index"]][
                            "customType"
                        ] = map_name.get("customType")

            else:
                map_name = field.get_field(field_names["column_name"])
                if map_name is None:
                    map_name = {}

                if "system" in map_name:
                    config["headers"][field_names["column_index"]][
                        "column_name"
                    ] = map_name.get("key")
                    config["headers"][field_names["column_index"]][
                        "original_name"
                    ] = map_name.get("name")
                    config["headers"][field_names["column_index"]][
                        "customType"
                    ] = map_name.get("custom")

        def fetch_field_ids(
            header_names: list,
        ) -> None:
            """
            Mutate the field names of Jira to JSON compatible names

            :param header_names: A list of Jira field names
            :return: None
            """

            for our_field_name in header_names:
                process_executor(
                    float_fields,
                    data=our_field_name,
                    workers=workers,
                    timeout=timeout,
                    regex_pattern=CUSTOM_FIELD_REGEX,
                )

            if is_cache is True:
                caching(
                    "custom_fields",
                    config["headers"],
                )

        def csv_field_change(
            operation: str = None,
        ) -> None:
            """
            Exclude certain fields or include certain fields from Jira
            CSV export. In addition, change the delimiter used on the CSV
            file before export is completed.

            :param operation: A decision trigger for CSV file manipulation
                              changes

            :return: None
            """
            data_frame(files_=temp_file)
            field_read = file_reader(
                folder,
                temp_file,
                skip=True,
            )
            file_headers = []
            print(
                "Validating Jira field names"
                if operation == "exclude" or operation == "include"
                else "Changing CSV file delimiter"
            )
            if operation == "exclude" or operation == "include":
                fetch_field_ids(config["headers"])
            (
                _field_list,
                first_run,
            ) = (
                [],
                False,
            )

            for field_column_ in field_read:
                _field_data = []
                for (
                    field_header,
                    field_row,
                ) in zip(
                    config["headers"],
                    field_column_,
                ):
                    if operation == "exclude":
                        if (
                            field_header.get("original_name")
                            not in exclude_fields
                        ):
                            _field_data.append(field_row)
                            if first_run is False:
                                file_headers.append(
                                    field_header.get("field_column_name")
                                )
                    elif operation == "include":
                        if field_header.get("original_name") in include_fields:
                            _field_data.append(field_row)
                            if first_run is False:
                                file_headers.append(
                                    field_header.get("field_column_name")
                                )
                    else:
                        _field_data.append(field_row)
                        if first_run is False:
                            file_headers.append(
                                field_header.get("column_name")
                            )

                first_run = True
                _field_list.append(_field_data)

            print(
                "Reconstructing file headers"
                if operation == "exclude" or operation == "include"
                else "Recreating file headers"
            )
            (
                file_writer(
                    folder,
                    temp_file,
                    data=[file_headers],
                    mark="many",
                    mode="w+",
                    delimiter=delimit
                )
            )
            print(
                "Excluding declared field columns into the CSV file"
                if operation == "exclude"
                else "Including declared field columns into the CSV file"
                if operation == "include"
                else 'Rewriting file separator to use "{}" as delimiter'.format(
                    delimit
                )
            )
            (
                file_writer(
                    folder,
                    temp_file,
                    data=_field_list,
                    mark="many",
                    delimiter=delimit
                )
            )

        def export_groups(
            user_account: str,
        ) -> list:
            """
            Exports a list of group a user is in.
            :param user_account: The username or account id of a user
            :return:
            """
            _group_holder_ = []
            if not user_account.startswith("qm:"):
                _user_group_ = LOGIN.get(endpoint.get_user_group(user_account))
                if _user_group_.status_code < 300:
                    _group_data_ = _user_group_.json()
                    for user_group in _group_data_:
                        _group_holder_.append(user_group.get("name"))

            return _group_holder_

        def search_sprints(
            sprint_value: str,
        ) -> None:
            """
            Search for sprint id from Jira issues

            :param sprint_value: A Sprint value

            :return: None
            """
            _search_ = LOGIN.get(
                endpoint.search_issues_jql(
                    f'{config["sprint_cf"]} = "{sprint_value}"'
                ) if LOGIN.api is False else
                endpoint.search_cloud_issues(
                    f'{config["sprint_cf"]} = "{sprint_value}"'
                )
            )
            if _search_.status_code < 300:
                _search_results_ = _search_.json()["issues"]
                for keys in _search_results_:
                    if "key" in keys:
                        key_ = keys["key"]
                        _search_issue = LOGIN.get(endpoint.issues(key_))
                        if _search_issue.status_code < 300:
                            _issue_results_ = _search_issue.json()["fields"]
                            sprint_field = _issue_results_[
                                sprint_custom_id["id"]
                            ]
                            if isinstance(sprint_field, list):
                                for sprint_item_ in sprint_field:
                                    if (
                                        sprint_item_.get("name")
                                        in config["sprint_object_container"]
                                    ):
                                        sprint_data = {
                                            "name": sprint_item_.get("name"),
                                            "state": sprint_item_.get("state"),
                                            "startDate": sprint_item_.get(
                                                "startDate"
                                            ),
                                            "endDate": sprint_item_.get(
                                                "endDate"
                                            ),
                                            "completeDate": sprint_item_.get(
                                                "completeDate"
                                            ),
                                            "rapidViewId": sprint_item_.get(
                                                "boardId"
                                            ),
                                        }
                                        if (
                                            sprint_item_.get("name")
                                            not in config[
                                                "sprint_object_container"
                                            ][sprint_item_.get("name")]
                                        ):
                                            config["sprint_object_container"][
                                                sprint_item_.get("name")
                                            ].append(sprint_data)
                                        break

        def extend_format(
            ext: str = None,
        ) -> None:
            """
            Differentiate between the format file to render

            :param ext: A format type to render
            :return: None
            """

            def extend_file_type() -> None:
                """
                Determines the file name when ``final_file`` argument is
                used.

                :return: None
                """
                nonlocal final_file
                if ext.lower() == "csv":
                    if not final_file.endswith(".csv"):
                        final_file = final_file + ".csv"
                    shutil.copy(
                        path_builder(
                            folder,
                            temp_file,
                        ),
                        path_builder(
                            folder,
                            final_file,
                        ),
                    )
                elif ext.lower() == "json":
                    if not final_file.endswith(".json"):
                        final_file = final_file + ".json"
                    json.dump(
                        config["json_build"],
                        open(
                            path_builder(
                                folder,
                                final_file,
                            ),
                            mode="w+",
                            encoding=encoding,
                        ),
                        indent=4,
                        sort_keys=True,
                    )
                os.remove(
                    path_builder(
                        folder,
                        temp_file,
                    )
                )

            def user_extraction() -> None:
                """
                Extracts and retains Jira users
                and groups lookup until program finish executing

                :return: list
                """

                def export_users(
                    _export_data_: dict,
                ) -> None:
                    """
                    Perform an export of users
                    :param _export_data_: An iterable item of data
                    :return: None
                    """

                    _data_ = {
                        "display_name": _export_data_.get("displayName"),
                        "account_id": _export_data_.get("accountId")
                        if LOGIN.api is True
                        else _export_data_.get("name"),
                        "active": _export_data_.get("active"),
                        "account_type": _export_data_.get("accountType"),
                        "groups": [],
                        "email": _export_data_.get("emailAddress"),
                    }
                    config["json_userlist"].append(_data_)

                print("Searching for user data.")
                (
                    _start,
                    _max_result_,
                ) = (
                    0,
                    1000,
                )

                while True:
                    user_export = LOGIN.get(
                        endpoint.search_users(
                            _start,
                            _max_result_,
                        )
                    )
                    if user_export.status_code < 300:
                        _user_data_ = user_export.json()
                        if not _user_data_:
                            break
                        for _user_item_ in _user_data_:
                            process_executor(
                                export_users,
                                data=_user_item_,
                                workers=workers,
                                timeout=timeout,
                            )
                    else:
                        break
                    _start += _max_result_

                if is_cache is True:
                    caching(
                        "users",
                        config["json_userlist"],
                    )

            def link_issue_extraction(
                linked_object: dict,
                regex_pattern_in: str,
                regex_pattern_out: str,
            ) -> None:
                """
                Extracts the linked issues according to
                issue key data in the export.

                :param linked_object: A dict of the column header
                :param regex_pattern_in: A regular expression pattern
                                        for issue links inwards
                :param regex_pattern_out: A regular expression pattern
                                          for issue links outwards

                :return: None
                """
                if linked_object["column_name"].startswith("Inward issue link"):
                    search_name = re.compile(
                        regex_pattern_in,
                        re.I,
                    )
                    find_name = search_name.search(linked_object["column_name"])
                    name_found = None
                    if find_name is not None:
                        name_found = find_name.group(2)

                    if name_found is not None:
                        jira_field_name = name_found.lstrip("(").rstrip(")")
                        map_name = jira_field_name

                        config["headers"][linked_object["column_index"]][
                            "linked_name"
                        ] = map_name
                elif linked_object["column_name"].startswith(
                    "Outward issue link"
                ):
                    search_name = re.compile(
                        regex_pattern_out,
                        re.I,
                    )
                    find_name = search_name.search(linked_object["column_name"])
                    name_found = None
                    if find_name is not None:
                        name_found = find_name.group(2)

                    if name_found is not None:
                        jira_field_name = name_found.lstrip("(").rstrip(")")
                        map_name = jira_field_name

                        config["headers"][linked_object["column_index"]][
                            "linked_name"
                        ] = map_name

            def json_field_builder() -> None:
                """Builds a JSON representation of fields in Jira

                :return: None
                """
                # A blueprint of a JSON template
                json_project_template = {"projects": []}
                json_linked_issues_template = {"links": []}
                json_user_template = {"users": []}
                json_history_template = {"history": []}
                # declare the base template of the Jira JSON structure
                (
                    config["json_build"],
                    config["save_point"],
                    config["sprint_data"],
                    config["issuekey_data"],
                ) = (
                    {},
                    {},
                    {},
                    {},
                )
                (
                    config["projecttype_data"],
                    config["projecturl_data"],
                    config["projectdescription_data"],
                    config["projectlead_data"],
                    config["projectname_data"],
                ) = (
                    {},
                    {},
                    {},
                    {},
                    {},
                )
                config["sprint_data"]["col_name_index"] = []
                # Start the first project save point
                config["save_point"]["col_name_index"] = 0
                config["issuekey_data"]["col_name_index"] = 0
                config["projecttype_data"]["col_name_index"] = 0
                config["projectdescription_data"]["col_name_index"] = 0
                config["projecturl_data"]["col_name_index"] = 0
                config["projectlead_data"]["col_name_index"] = 0
                config["projectname_data"]["col_name_index"] = 0
                (
                    config["sprint_object_container"],
                    config["json_userlist"],
                ) = (
                    {},
                    [],
                )
                # begin data extraction from issue exported
                data_frame(files_=temp_file)

                try:
                    # locate the project key and use it across
                    # the JSON structure
                    get_pkey_index(
                        config["headers"],
                        "Project key",
                        [
                            "save_point",
                            "col_name_index",
                        ],
                    )
                    assert config["is_valid"] is True, (
                        "Unable to find required field "
                        "in header column e.g. Project key"
                    )
                except AssertionError as err:
                    os.remove(
                        path_builder(
                            folder,
                            temp_file,
                        )
                    )
                    add_log(
                        f"{err} on line {err.__traceback__.tb_lineno}"
                        f"{sys.__excepthook__(Exception, err, err.__traceback__)}",
                        "error",
                    )
                    exit(err)

                print(
                    "Converting Jira custom field names to "
                    "Jira JSON compatible names."
                )

                try:
                    if use_cache is True:
                        if is_file_exist("custom_fields"):
                            print("Using cached data of custom fields")
                        else:
                            fetch_field_ids(config["headers"])
                    else:
                        fetch_field_ids(config["headers"])
                except (
                    KeyError,
                    AttributeError,
                    ValueError,
                    IndexError,
                    TypeError,
                ) as err:
                    os.remove(
                        path_builder(
                            folder,
                            temp_file,
                        )
                    )
                    add_log(
                        f"{err} on line {err.__traceback__.tb_lineno} "
                        f"{sys.__excepthook__(Exception, err, err.__traceback__)}",
                        "error",
                    )
                    exit(f"An error has occurred: {err}")

                # Fetching sprints if exist
                get_pkey_index(
                    config["headers"],
                    "Sprint",
                    [
                        "sprint_data",
                        "col_name_index",
                    ],
                    attr=True,
                )
                # Search other fields below if they exist
                get_pkey_index(
                    config["headers"],
                    "Issue key",
                    [
                        "issuekey_data",
                        "col_name_index",
                    ],
                )
                get_pkey_index(
                    config["headers"],
                    "Project type",
                    [
                        "projecttype_data",
                        "col_name_index",
                    ],
                )
                get_pkey_index(
                    config["headers"],
                    "Project description",
                    [
                        "projectdescription_data",
                        "col_name_index",
                    ],
                )
                get_pkey_index(
                    config["headers"],
                    "Project url",
                    [
                        "projecturl_data",
                        "col_name_index",
                    ],
                )
                get_pkey_index(
                    config["headers"],
                    "Project lead id" if LOGIN.api is True else "Project lead",
                    [
                        "projectlead_data",
                        "col_name_index",
                    ],
                )
                get_pkey_index(
                    config["headers"],
                    "Project name",
                    [
                        "projectname_data",
                        "col_name_index",
                    ],
                )
                read_csv_file = file_reader(
                    folder,
                    temp_file,
                    skip=True,
                )
                # generate a user list
                print(
                    "Verifying users membership"
                ) if use_cache is False else print(
                    "Looking up users from cache"
                )
                if use_cache is True:
                    if is_file_exist("users"):
                        print("Using cache to verify users")
                    else:
                        user_extraction()
                else:
                    user_extraction()

                if "links" in config["json_props_options"]:
                    print("Verifying linked issues from issuelink types")
                    for links in config["headers"]:
                        link_issue_extraction(
                            links,
                            INWARD_ISSUE_LINK,
                            OUTWARD_ISSUE_LINK,
                        )

                print("Verifying Sprint values.")
                get_sprint_obj = deepcopy(read_csv_file)

                for sprint_item in get_sprint_obj:
                    for sub_sprint in config["sprint_data"]["col_name_index"]:
                        if sprint_item[sub_sprint]:
                            config["sprint_object_container"].update(
                                {f"{sprint_item[sub_sprint]}": []}
                            )

                if sprint_custom_id is not None and "customType" in sprint_custom_id:
                    if sprint_custom_id["customType"].endswith("gh-sprint"):
                        extract = sprint_custom_id["id"].split("_")
                        config["sprint_cf"] = "cf[{}]".format(extract[1])

                def name_to_user_id(
                    user_value: str,
                ) -> dict:
                    """
                    Returns an account_id or userid of a User object

                    :param user_value: Convert a display name to acceptable
                                        username or accountId

                    :return: dict
                    """

                    (
                        _user_value_list,
                        _profile_data_,
                    ) = (
                        [],
                        None,
                    )
                    for _user_names_ in config["json_userlist"]:
                        if user_value == _user_names_["display_name"]:
                            _profile_data_ = {
                                "account_id": _user_names_["account_id"],
                                "display_name": _user_names_["display_name"],
                                "active": _user_names_["active"],
                                "groups": _user_names_["groups"],
                                "email": _user_names_.get("email"),
                            }
                            _user_value_list.append(_profile_data_)

                    if not _user_value_list:
                        return {"account_id": None}
                    elif len(_user_value_list) == 1:
                        return _profile_data_
                    elif len(_user_value_list) > 1:
                        # Since we're finding these users by display name
                        # if multiple users with the same name exist, we want to
                        # take a calculated guess but this is not accurate
                        # as it's a probability
                        guess = random.choices(
                            _user_value_list,
                            [
                                float(_user_value_list.index(each_user) + 0.5)
                                for each_user in _user_value_list
                            ],
                        )
                        return guess[0]

                print("Extracting Sprint Ids from values.")
                print("Searching for Sprint data")
                for (
                    sprint_key,
                    sprint_val,
                ) in config["sprint_object_container"].items():
                    process_executor(
                        search_sprints,
                        data=sprint_key,
                        workers=2,
                        timeout=timeout,
                    )

                project_settings = {}
                project_config = {}

                def field_builder(
                    bundle: list = None,
                    col_name: list = None,
                ) -> None:
                    """Takes a bundle which is a list and extracts values

                    :param bundle: A data list to process
                    :param col_name: A list of the column names

                    :return: None
                    """


                    def start_process() -> None:
                        """
                        Initiates the JSON conversion process
                        :return: None
                        """
                        nonlocal my_index
                        json_customfield_template = {"customFieldValues": []}
                        json_customfield_sub_template = {"value": []}
                        json_attachment_template = {"attachments": []}
                        json_comment_template = {"comments": []}
                        json_worklog_template = {"worklogs": []}
                        json_labels_template = {"labels": []}
                        json_watchers_template = {"watchers": []}
                        json_component_template = {"components": []}
                        json_fixversion_template = {"fixedVersions": []}
                        json_affectversion_template = {"affectedVersions": []}
                        (
                            data,
                            issue_data,
                            issue_temp,
                        ) = (
                            {},
                            {},
                            {"issues": []},
                        )
                        (
                            sprint_issue_data,
                            cf_multi_field,
                        ) = (
                            [],
                            {},
                        )

                        def parse_sla_fields(
                            time_value: str,
                        ) -> Union[str, None,]:
                            """
                            Convert the datetime string into compatible
                            d/MMM/yy

                            :param time_value: A string of datetime data
                            :return: str
                            """
                            time_val = None
                            if time_value is None or time_value == "":
                                pass
                            else:
                                time_val = datetime.strptime(
                                    time_value,
                                    Df.YYYY_MM_dd_HH_MM_SS_MS,
                                )
                                return time_val.strftime(Df.dd_MMM_yy)
                            return time_val

                        def parse_duration(
                            time_value: int = 0,
                        ) -> str:
                            """
                            Parse time value into ISO_8601 durations
                            source: https://en.wikipedia.org/wiki/ISO_8601#Durations
                            Using seconds for every time value.

                            :param time_value: A time estimate value
                            :return: str
                            """
                            time_val = "PT0S"
                            if time_value is None or time_value == "":
                                pass
                            else:
                                time_val = f"PT{time_value}S"
                            return time_val

                        def parse_dates(
                            date_value: str,
                            date_pattern: str = date_format,
                            index_level: int = 0,
                            end_format: str = None,
                        ) -> Union[str, None,]:
                            """
                            Parse date format into Jira JSON acceptable format

                            :param date_value: A date string value
                            :param date_pattern: A format for datetime
                            :param index_level: Level of index
                            :param end_format: An end format for the date field

                            :return: datetime string value
                            """

                            new_date = None
                            if date_value == "" or date_value is None:
                                pass
                            else:
                                try:
                                    new_date = datetime.strptime(
                                        date_value,
                                        date_pattern,
                                    )
                                    return new_date.strftime(
                                        Df.YYYY_MM_dd_HH_MM_SS_MS_TZ
                                        if end_format is None
                                        else end_format
                                    )
                                except ValueError:
                                    default_format = [
                                        Df.dd_MMM_yy_hh_MM_AM_PM,
                                        Df.dd_MM_yy_hh_MM_AM_PM,
                                        Df.dd_MMM_YYYY_hh_MM_SS_AM_PM,
                                        Df.dd_space_MMM_space_YYYY_space_HH_MM,
                                        Df.YYYY_MM_dd_T_HH_MM_SS_MS,
                                        Df.dd_space_MMM_space_YYYY_space_hh_MM,
                                        Df.MM_dd_yy_space_hh_MM_AM_PM,
                                        Df.dd_MM_YYYY_space_hh_MM_AM_PM,
                                        Df.MM_dd_yy_hh_MM_AM_PM,
                                        Df.MMM_dd_YYYY_hh_MM_SS_AM_PM,
                                        Df.YYYY_MM_dd_hh_MM_SS_AM_PM,
                                        Df.dd_MM_YYYY_hh_MM_SS_AM_PM,
                                        Df.MM_dd_YYYY_hh_MM_AM_PM,
                                        "Invalid format",
                                    ]
                                    guess_format = default_format.copy()
                                    limit = len(guess_format)
                                    count = index_level
                                    current_value = date_value
                                    for _pattern_ in guess_format[index_level:]:
                                        count += 1
                                        if count >= limit:
                                            raise JiraOneErrors(
                                                "wrong",
                                                "Unable to determine "
                                                "date_format for"
                                                f" value {current_value}",
                                            )
                                        parse_dates(
                                            current_value,
                                            _pattern_,
                                            count,
                                        )

                            return new_date

                        for (
                            obj_value,
                            obj_name,
                        ) in zip(
                            bundle,
                            col_name,
                        ):
                            # Establish an updated reference of the project list
                            # and their object configurations above

                            def check_customtype(
                                custom: list,
                                type_obj: dict,
                            ) -> bool:
                                """
                                Return true or false for valid custom type

                                :param custom: a list of custom types
                                :param type_obj: An object type
                                :return: bool
                                """
                                for custom_type in custom:
                                    if type_obj.get("customType").startswith(
                                        custom_type
                                    ):
                                        return True
                                return False

                            def produce_custom_type(
                                type_object: dict,
                                type_value: Any,
                            ) -> dict:
                                """
                                Determine object type for custom field based
                                on custom field type
                                :param type_object: A dict representation of
                                                    the custom field
                                :param type_value: A value of the custom field
                                                    type
                                :return: dict
                                """
                                _data_ = None

                                def multi_drop_data(
                                    type_obj: dict,
                                ) -> dict:
                                    """
                                    Mutate data to avoid object duplication
                                    :param type_obj: An object data, typically
                                                     a custom field

                                    :return: dict
                                    """
                                    _cf_data_ = {
                                        "fieldName": type_obj.get(
                                            "original_name"
                                        ),
                                        "fieldType": type_obj.get("customType"),
                                        "value": cf_multi_field.get(
                                            type_obj.get("original_name")
                                        ).get("value"),
                                    }
                                    return _cf_data_

                                def multi_drop_check(
                                    _value_data_: Any,
                                    type_obj: dict,
                                ) -> None:
                                    """Mutates data into multiple list value
                                    :param _value_data_: A data value
                                    :param type_obj: An object data
                                    :return: None
                                    """
                                    for _items_ in json_customfield_template[
                                        "customFieldValues"
                                    ]:
                                        if _items_.get(
                                            "fieldName"
                                        ) == type_obj.get("original_name"):
                                            if (
                                                _value_data_ is None
                                                or _value_data_ == ""
                                            ):
                                                pass
                                            else:
                                                _items_.get("value").append(
                                                    _value_data_
                                                    if not type_obj.get(
                                                        "customType"
                                                    ).endswith(
                                                        "multiuserpicker"
                                                    )
                                                    else name_to_user_id(
                                                        _value_data_
                                                    ).get("account_id")
                                                )

                                if (
                                    type_object.get("customType").endswith(
                                        "multicheckboxes"
                                    )
                                    or type_object.get("customType").endswith(
                                        "multiuserpicker"
                                    )
                                    or type_object.get("customType").endswith(
                                        "labels"
                                    )
                                ):
                                    if type_object.get("original_name") not in [
                                        d.get("fieldName")
                                        for d in json_customfield_template[
                                            "customFieldValues"
                                        ]
                                    ]:
                                        if not hasattr(
                                            cf_multi_field,
                                            type_object.get("original_name"),
                                        ):
                                            if (
                                                type_value is None
                                                or type_value == ""
                                            ):
                                                cf_multi_field.update(
                                                    {
                                                        type_object.get(
                                                            "original_name"
                                                        ): {
                                                            "fieldName": type_object.get(
                                                                "original_name"
                                                            ),
                                                            "fieldType": type_object.get(
                                                                "customType"
                                                            ),
                                                            "value": [],
                                                        }
                                                    }
                                                )
                                            else:
                                                cf_multi_field.update(
                                                    {
                                                        type_object.get(
                                                            "original_name"
                                                        ): {
                                                            "fieldName": type_object.get(
                                                                "original_name"
                                                            ),
                                                            "fieldType": type_object.get(
                                                                "customType"
                                                            ),
                                                            "value": [
                                                                type_value
                                                            ]
                                                            if not type_object.get(
                                                                "customType"
                                                            ).endswith(
                                                                "multiuserpicker"
                                                            )
                                                            else [
                                                                name_to_user_id(
                                                                    type_value
                                                                ).get(
                                                                    "account_id"
                                                                )
                                                            ],
                                                        }
                                                    }
                                                )
                                            _data_ = multi_drop_data(
                                                type_object
                                            )

                                    else:
                                        if (
                                            type_value is None
                                            or type_value == ""
                                        ):
                                            multi_drop_check(
                                                type_value,
                                                type_object,
                                            )
                                        else:
                                            multi_drop_check(
                                                type_value,
                                                type_object,
                                            )

                                elif type_object.get("customType").endswith(
                                    "datetime"
                                ):
                                    _data_ = {
                                        "fieldName": type_object.get(
                                            "original_name"
                                        ),
                                        "fieldType": type_object.get(
                                            "customType"
                                        ),
                                        "value": parse_dates(
                                            type_value,
                                            Df.dd_MMM_yy_hh_MM_AM_PM,
                                            end_format=Df.dd_MMM_yy_hh_MM_AM_PM,
                                        ),
                                    }
                                elif type_object.get("customType").endswith(
                                    "userpicker"
                                ):
                                    _data_ = {
                                        "fieldName": type_object.get(
                                            "original_name"
                                        ),
                                        "fieldType": type_object.get(
                                            "customType"
                                        ),
                                        "value": name_to_user_id(
                                            type_value
                                        ).get("account_id"),
                                    }
                                elif type_object.get("customType").endswith(
                                    "firstresponsedate"
                                ):
                                    _data_ = {
                                        "fieldName": type_object.get(
                                            "original_name"
                                        ),
                                        "fieldType": type_object.get(
                                            "customType"
                                        ),
                                        "value": parse_sla_fields(type_value),
                                    }
                                elif type_object.get("customType").endswith(
                                    "cascadingselect"
                                ):
                                    cascade = type_value.split("->")
                                    cascade_obj = {}
                                    if len(cascade) > 1:
                                        cascade_obj.update(
                                            {
                                                "": cascade[0].strip(" "),
                                                "1": cascade[1].strip(" "),
                                            }
                                        )
                                        sub_cf_copy = deepcopy(cascade_obj)
                                        _data_ = {
                                            "fieldName": type_object.get(
                                                "original_name"
                                            ),
                                            "fieldType": type_object.get(
                                                "customType"
                                            ),
                                            "value": sub_cf_copy,
                                        }
                                    else:
                                        _data_ = {
                                            "fieldName": type_object.get(
                                                "original_name"
                                            ),
                                            "fieldType": type_object.get(
                                                "customType"
                                            ),
                                            "value": type_value,
                                        }
                                else:
                                    if check_customtype(
                                        json_custom_type,
                                        type_object,
                                    ):
                                        pass
                                    else:
                                        _data_ = {
                                            "fieldName": type_object.get(
                                                "original_name"
                                            ),
                                            "fieldType": type_object.get(
                                                "customType"
                                            ),
                                            "value": type_value,
                                        }

                                return _data_

                            def sprint_extract(
                                type_value: Any,
                            ) -> None:
                                """
                                Extracts a sprint object
                                :param type_value: A value of an object

                                :return: None
                                """

                                if (
                                    type_value
                                    in config["sprint_object_container"]
                                ):
                                    if config["sprint_object_container"][
                                        type_value
                                    ]:
                                        prep_obj = config[
                                            "sprint_object_container"
                                        ][type_value][-1]
                                        sprint_issue_data.append(prep_obj)

                            # Keep track of each project key and their objects
                            if (
                                bundle[config["save_point"]["col_name_index"]]
                                not in project_settings
                            ):
                                my_index += 1

                                my_bundle = {
                                    bundle[
                                        config["save_point"]["col_name_index"]
                                    ]: bundle[
                                        config["save_point"]["col_name_index"]
                                    ]
                                }
                                my_bundle_index = {
                                    bundle[
                                        config["save_point"]["col_name_index"]
                                    ]: my_index
                                }
                                project_name = (
                                    bundle[
                                        config["projectname_data"][
                                            "col_name_index"
                                        ]
                                    ]
                                    if config["projectname_data"][
                                        "col_name_index"
                                    ]
                                    > 0
                                    else None
                                )
                                project_settings.update(my_bundle)
                                project_config.update(my_bundle_index)
                                (
                                    cf_versions,
                                    cf_components,
                                ) = {
                                    "versions": []
                                }, {"components": []}
                                _project_keys_ = bundle[
                                    config["save_point"]["col_name_index"]
                                ]
                                get_versions = LOGIN.get(
                                    endpoint.get_project_versions(
                                        id_or_key=_project_keys_
                                    )
                                )
                                get_components = LOGIN.get(
                                    endpoint.get_project_component(
                                        id_or_key=_project_keys_
                                    )
                                )
                                if get_versions.status_code < 300:
                                    for version in get_versions.json():
                                        _data = {
                                            "name": version.get(
                                                "name",
                                                "",
                                            ),
                                            "released": version.get(
                                                "released",
                                                "",
                                            ),
                                            "releaseDate": version.get(
                                                "releaseDate",
                                                "",
                                            ),
                                        }
                                        cf_versions["versions"].append(_data)
                                if get_components.status_code < 300:
                                    for component in get_components.json():
                                        lead = None
                                        if "lead" in component:
                                            lead = component.get("lead").get(
                                                "accountId"
                                            )
                                        _data = (
                                            {
                                                "name": component.get(
                                                    "name",
                                                    "",
                                                ),
                                                "description": component.get(
                                                    "description",
                                                    "",
                                                ),
                                            }
                                            if lead is None
                                            else {
                                                "name": component.get(
                                                    "name",
                                                    "",
                                                ),
                                                "description": component.get(
                                                    "description",
                                                    "",
                                                ),
                                                "lead": lead,
                                            }
                                        )
                                        cf_components["components"].append(
                                            _data
                                        )

                                issue_temp.update(
                                    {
                                        "key": bundle[
                                            config["save_point"][
                                                "col_name_index"
                                            ]
                                        ]
                                    }
                                )
                                issue_temp.update({"name": project_name})
                                issue_temp.update(cf_versions)
                                issue_temp.update(cf_components)
                                issue_temp.update(
                                    {
                                        "type": bundle[
                                            config["projecttype_data"][
                                                "col_name_index"
                                            ]
                                        ]
                                        if config["projecttype_data"][
                                            "col_name_index"
                                        ]
                                        > 0
                                        else None
                                    }
                                )
                                issue_temp.update(
                                    {
                                        "template": project_type.get("software")
                                        if issue_temp["type"] == "software"
                                        else project_type.get("service_desk")
                                        if issue_temp["type"] == "service_desk"
                                        else project_type.get("business")
                                    }
                                )
                                issue_temp.update(
                                    {
                                        "url": bundle[
                                            config["projecturl_data"][
                                                "col_name_index"
                                            ]
                                        ]
                                        if config["projecturl_data"][
                                            "col_name_index"
                                        ]
                                        > 0
                                        else None
                                    }
                                )
                                issue_temp.update(
                                    {
                                        "description": bundle[
                                            config["projectdescription_data"][
                                                "col_name_index"
                                            ]
                                        ]
                                        if config["projectdescription_data"][
                                            "col_name_index"
                                        ]
                                        > 0
                                        else None
                                    }
                                )
                                issue_temp.update(
                                    {
                                        "lead": bundle[
                                            config["projectlead_data"][
                                                "col_name_index"
                                            ]
                                        ]
                                        if config["projectlead_data"][
                                            "col_name_index"
                                        ]
                                        > 0
                                        else None
                                    }
                                )
                                if workflows:
                                    issue_temp.update(
                                        {
                                            "workflowSchemeName": workflows[
                                                _project_keys_
                                            ]
                                            if _project_keys_ in workflows
                                            else "Sample project workflow"
                                        }
                                    )
                                issue_temp.update(
                                    {"externalName": project_name}
                                )
                                json_project_template["projects"].append(
                                    issue_temp
                                )

                            # Dynamically get a sub-item into custom field
                            # values
                            # Below are the conditions for arranging field
                            # values

                            if not check_is_type(obj_name.get("column_name", "")
                                                 ).startswith("custom"):
                                if (
                                    check_is_type(obj_name.get("column_name", ""))
                                    .lower()
                                    .startswith("comment")
                                ):
                                    issue_comment = obj_value.split(";")
                                    if len(issue_comment) > 1:
                                        _data = {
                                            "created": parse_dates(
                                                issue_comment[0]
                                            ),
                                            "author": issue_comment[1],
                                            "body": issue_comment[2],
                                        }
                                        if is_sd_internal is True:
                                            _data.update(
                                                {
                                                    "properties": [
                                                        {
                                                            "key": "sd.public.comment",
                                                            "value": {
                                                                "internal": issue_comment[
                                                                    3
                                                                ]
                                                            },
                                                        }
                                                    ]
                                                }
                                            )
                                        json_comment_template[
                                            "comments"
                                        ].append(_data)

                                elif (
                                    check_is_type(obj_name.get("column_name", ""))
                                    .lower()
                                    .startswith("attachment")
                                ):
                                    attacher = obj_value.split(";")
                                    if len(attacher) > 1:
                                        _data = {
                                            "created": parse_dates(attacher[0]),
                                            "attacher": attacher[1],
                                            "name": attacher[2],
                                            "uri": attacher[3],
                                        }
                                        json_attachment_template[
                                            "attachments"
                                        ].append(_data)
                                elif check_is_type(obj_name.get("column_name", "")).startswith(
                                    "worklog"
                                ):
                                    worklog = obj_value.split(";")
                                    if len(worklog) > 1:
                                        _data = {
                                            "startDate": parse_dates(
                                                worklog[1]
                                            ),
                                            "author": worklog[2],
                                            "timeSpent": parse_duration(
                                                worklog[3]
                                            ),
                                        }
                                        json_worklog_template[
                                            "worklogs"
                                        ].append(_data)

                                elif check_is_type(obj_name.get("column_name", "")).startswith(
                                    "labels"
                                ):
                                    if obj_value == "" or obj_value is None:
                                        pass
                                    else:
                                        json_labels_template["labels"].append(
                                            obj_value
                                        )

                                elif check_is_type(obj_name.get("column_name", "")).startswith(
                                    "Inward issue link"
                                ):
                                    if obj_value == "" or obj_value is None:
                                        pass
                                    else:
                                        json_linked_issues_template[
                                            "links"
                                        ].append(
                                            {
                                                "name": obj_name.get(
                                                    "linked_name"
                                                ),
                                                "sourceId": obj_value,
                                                "destinationId": bundle[
                                                    config["issuekey_data"][
                                                        "col_name_index"
                                                    ]
                                                ],
                                            }
                                        )
                                elif check_is_type(obj_name.get("column_name", "")).startswith(
                                    "Outward issue link"
                                ):
                                    if obj_value == "" or obj_value is None:
                                        pass
                                    else:
                                        json_linked_issues_template[
                                            "links"
                                        ].append(
                                            {
                                                "name": obj_name.get(
                                                    "linked_name"
                                                ),
                                                "destinationId": obj_value,
                                                "sourceId": bundle[
                                                    config["issuekey_data"][
                                                        "col_name_index"
                                                    ]
                                                ],
                                            }
                                        )
                                elif check_is_type(obj_name.get("column_name", "")).startswith(
                                    "Watchers Id"
                                    if LOGIN.api is True
                                    else "Watchers"
                                ):
                                    if obj_value == "" or obj_value is None:
                                        pass
                                    else:
                                        json_watchers_template[
                                            "watchers"
                                        ].append(obj_value)
                                elif check_is_type(obj_name.get("column_name", "")).startswith(
                                    "components"
                                ):
                                    if obj_value == "" or obj_value is None:
                                        pass
                                    else:
                                        json_component_template[
                                            "components"
                                        ].append(obj_value)
                                elif check_is_type(obj_name.get("column_name", "")).startswith(
                                    "fixVersions"
                                ):
                                    if obj_value == "" or obj_value is None:
                                        pass
                                    else:
                                        json_fixversion_template[
                                            "fixedVersions"
                                        ].append(obj_value)
                                elif check_is_type(obj_name.get("column_name", "")).startswith(
                                    "affectedVersions"
                                ):
                                    if obj_value == "" or obj_value is None:
                                        pass
                                    else:
                                        json_affectversion_template[
                                            "affectedVersions"
                                        ].append(obj_value)
                                elif check_is_type(obj_name.get("column_name", "")).startswith(
                                    "Issue id"
                                ):
                                    issue_id = obj_value
                                    issue_data.update({"externalId": issue_id})
                                elif check_is_type(obj_name.get("column_name", "")).startswith(
                                    "Sprint"
                                ):
                                    if obj_value == "" or obj_value is None:
                                        pass
                                    else:
                                        sprint_extract(obj_value)

                                else:
                                    if obj_value is None or obj_value == "":
                                        pass
                                    else:
                                        data.update(
                                            {
                                                check_is_type(obj_name.get(
                                                    "column_name"
                                                )): obj_value
                                            }
                                        )
                                        issue_data.update(data)
                            else:
                                _data = produce_custom_type(
                                    obj_name,
                                    obj_value,
                                )
                                if _data is not None:
                                    if "value" in _data:
                                        if (
                                            _data["value"] is None
                                            or _data["value"] == ""
                                        ):
                                            pass
                                        else:
                                            json_customfield_template[
                                                "customFieldValues"
                                            ].append(_data)
                                json_customfield_sub_template["value"].clear()

                        # Only include sprint data if not empty
                        if sprint_issue_data:
                            json_customfield_template[
                                "customFieldValues"
                            ].append(
                                {
                                    "fieldName": "Sprint",
                                    "fieldType": field.field_type.get("sprint"),
                                    "value": sprint_issue_data,
                                }
                            )

                        # remove custom field id generated and issue links
                        value_to_delete = []
                        for (
                            _issue_key,
                            _issue_value,
                        ) in issue_data.items():
                            if check_is_type(_issue_key).startswith("Custom field"):
                                value_to_delete.append(_issue_key)
                            if check_is_type(_issue_key).startswith("Inward issue link"):
                                value_to_delete.append(_issue_key)
                            if check_is_type(_issue_key).startswith("Outward issue link"):
                                value_to_delete.append(_issue_key)

                        for _vals_ in value_to_delete:
                            del issue_data[_vals_]

                        # Add each field value to the issue data object
                        issue_data.update(json_customfield_template)
                        issue_data.update(json_comment_template)
                        issue_data.update(json_attachment_template)
                        issue_data.update(json_watchers_template)
                        issue_data.update(json_labels_template)
                        issue_data.update(json_worklog_template)
                        issue_data.update(json_component_template)
                        issue_data.update(json_fixversion_template)
                        issue_data.update(json_affectversion_template)

                        # perform field copy and rewrites for
                        # system known fields
                        issue_data["timeSpent"] = parse_duration(
                            issue_data.get("timespent")
                        )
                        issue_data["originalEstimate"] = parse_duration(
                            issue_data.get("timeoriginalestimate")
                        )
                        issue_data["estimate"] = parse_duration(
                            issue_data.get("timeestimate")
                        )
                        if "issuetype" in issue_data:
                            issue_data["issueType"] = issue_data["issuetype"]
                        issue_data["resolutionDate"] = parse_dates(
                            issue_data.get("resolutiondate")
                        )
                        if LOGIN.api is True:
                            issue_data["assignee"] = issue_data.get(
                                "Assignee Id"
                            )
                            issue_data["reporter"] = issue_data.get(
                                "Reporter Id"
                            )
                            issue_data["creator"] = issue_data.get("Creator Id")
                        if "created" in issue_data:
                            issue_data["created"] = parse_dates(
                                issue_data.get("created")
                            )
                        if "Created" in issue_data:
                            issue_data["created"] = parse_dates(
                                issue_data.get("Created")
                            )
                        issue_data["updated"] = parse_dates(
                            issue_data.get("updated")
                        )
                        issue_data["duedate"] = parse_dates(
                            issue_data.get("duedate")
                        )

                        # project configuration data
                        issue_data["projectDescription"] = issue_data.get(
                            "Project description"
                        )
                        issue_data["projectKey"] = issue_data.get("Project key")
                        issue_data["projectLead"] = issue_data.get(
                            "Project lead id"
                            if LOGIN.api is True
                            else "Project lead"
                        )
                        issue_data["projectName"] = issue_data.get(
                            "Project name"
                        )
                        issue_data["projectType"] = issue_data.get(
                            "Project type"
                        )
                        issue_data["projectUrl"] = issue_data.get("Project url")
                        issue_data["id"] = issue_data.get("externalId")
                        issue_data["parent"] = issue_data.get("Parent")
                        issue_data["key"] = issue_data.get("Issue key")
                        issue_data["epicLinkSummary"] = issue_data.get(
                            "Epic Link Summary"
                        )
                        issue_data["statusCategory"] = issue_data.get(
                            "Status Category"
                        )
                        issue_data["parentSummary"] = issue_data.get(
                            "Parent summary"
                        )
                        # perform deletion of unused fields
                        items_to_delete = [
                            "Project lead id",
                            "Project lead",
                            "Project description",
                            "Project key",
                            "Project name",
                            "Project type",
                            "Status Category",
                            "Project url",
                            "Issue id",
                            "watches",
                            "workratio",
                            "versions",
                            "Created",
                            "Creator",
                            "timeestimate",
                            "issuetype",
                            "resolutiondate",
                            "timeoriginalestimate",
                            "timespent",
                            "Parent",
                            "Parent id",
                            "Epic Link Summary",
                            "Parent summary",
                            "Issue key",
                        ]
                        for del_item in items_to_delete:
                            if del_item in issue_data:
                                del issue_data[del_item]

                        if issue_data["timeSpent"] == "":
                            del issue_data["timeSpent"]
                        if issue_data["originalEstimate"] == "":
                            del issue_data["originalEstimate"]
                        if (
                            issue_data["duedate"] == ""
                            or issue_data["duedate"] is None
                        ):
                            del issue_data["duedate"]
                        if (
                            issue_data["estimate"] == ""
                            or issue_data["estimate"] is None
                        ):
                            del issue_data["estimate"]
                        if (
                            issue_data["resolutionDate"] == ""
                            or issue_data["resolutionDate"] is None
                        ):
                            del issue_data["resolutionDate"]
                        if LOGIN.api is True:
                            user_attr = [
                                "Assignee Id",
                                "Reporter Id",
                                "Creator Id",
                            ]
                            for attr in user_attr:
                                if attr in issue_data:
                                    del issue_data[attr]
                        if issue_data["worklogs"]:
                            del issue_data["timeSpent"]
                        if not issue_data["worklogs"]:
                            del issue_data["worklogs"]

                        # appending all issues data to each issue list per
                        # project key
                        project_index = project_config[
                            bundle[config["save_point"]["col_name_index"]]
                        ]
                        json_project_template["projects"][project_index][
                            "issues"
                        ].append(issue_data)

                    start_process()

                my_index = -1
                # Begin the JSON conversion process
                print("JSON conversion started.")
                try:
                    for name_of_fields in read_csv_file:
                        field_builder(
                            name_of_fields,
                            config["headers"],
                        )
                except (
                    IndexError,
                    KeyError,
                    TypeError,
                    AttributeError,
                    ValueError,
                    JiraOneErrors,
                ) as err:
                    os.remove(
                        path_builder(
                            folder,
                            temp_file,
                        )
                    )
                    add_log(
                        f"{err} on line {err.__traceback__.tb_lineno}"
                        f" with {err.__traceback__} "
                        f"{sys.__excepthook__(Exception, err, err.__traceback__)}",
                        "error",
                    )
                    exit(f"An error has occurred: {err}")

                config["json_build"].update(json_project_template)

                def parse_history_data(
                    history_key: str,
                ) -> None:
                    """
                    Parse some history payload and process
                    some object with list of items about the
                    history

                    :param history_key: A Jira issue key
                    :return: None
                    """
                    query = f"key = {history_key}"
                    history_folder = f"{folder}/history"
                    history_file = f"history_{history_key}.csv"
                    PROJECT.change_log(
                        folder=history_folder,
                        allow_cp=False,
                        file=history_file,
                        jql=query,
                        show_output=False,
                    )
                    read_history = file_reader(
                        history_folder,
                        history_file,
                        skip=True,
                    )
                    history_data = []
                    for _history_ in read_history:
                        name_mapper = {
                            "issueKey": _history_[0],
                            "summary": _history_[1],
                            "author": _history_[2],
                            "created": _history_[3],
                            "fieldType": _history_[4],
                            "field": _history_[5],
                            "fieldId": _history_[6],
                            "from_": _history_[7],
                            "fromString": _history_[8],
                            "to_": _history_[9],
                            "toString": _history_[10],
                        }
                        mapped = DotNotation(name_mapper)
                        _history_data_ = {
                            "author": name_to_user_id(mapped.author).get(
                                "account_id"
                            ),
                            "created": mapped.created,
                            "items": [
                                {
                                    "fieldType": mapped.fieldType,
                                    "field": mapped.field,
                                    "from": mapped.from_ or None,
                                    "fromString": mapped.fromString or None,
                                    "to": mapped.to_ or None,
                                    "toString": mapped.toString or None,
                                }
                            ],
                        }
                        history_data.append(_history_data_)

                    json_history_template["history"].append(
                        {
                            "key": history_key,
                            "value": history_data,
                        }
                    )

                    os.remove(
                        path_builder(
                            history_folder,
                            history_file,
                        )
                    )

                # adjust sub-task link
                def run_multi_check(
                    parent_key: str,
                ) -> str:
                    """
                    Run a search on the json build object until
                    you can find a parent issue, if not return
                    empty string

                    :param parent_key: An issue number
                    :return: str
                    """
                    for some_issue in config["json_build"]["projects"]:
                        another_issue = some_issue["issues"]
                        for now_issue in another_issue:
                            now_id = now_issue.get("id")
                            now_issue_key = now_issue.get("key")
                            if parent_key == now_id:
                                return now_issue_key
                    return ""

                for sub_task_check in config["json_build"]["projects"]:
                    issues = sub_task_check["issues"]
                    for issue in issues:
                        if issue.get("issueType") in sub_tasks:
                            get_parent = issue.get("parent")
                            get_sub_task_key = issue.get("key")
                            linked_parent = run_multi_check(get_parent)
                            json_linked_issues_template["links"].append(
                                {
                                    "name": "jira_subtask_link",
                                    "destinationId": get_sub_task_key,
                                    "sourceId": linked_parent,
                                }
                            )

                if json_properties:
                    if "links" in config["json_props_options"]:
                        print("Adding linked issues to the export")

                        config["json_build"].update(json_linked_issues_template)

                    if "users" in config["json_props_options"]:
                        print("Updating users and group to the export")

                        def get_groups(
                            user_data: dict,
                        ) -> None:
                            """Process the group extraction"""
                            usernames = {
                                "name": user_data.get("account_id"),
                                "fullname": user_data.get("display_name"),
                                "active": user_data.get("active"),
                                "groups": export_groups(
                                    user_data.get("account_id")
                                ),
                                "email": user_data.get("email"),
                            }
                            json_user_template["users"].append(usernames)

                        for names_of_users in config["json_userlist"]:
                            process_executor(
                                get_groups,
                                data=names_of_users,
                                workers=workers,
                                timeout=timeout,
                            )

                        config["user_data_group"].update(
                            {"users": json_user_template["users"]}
                        )
                        config["json_build"].update(config["user_data_group"])

                    if "history" in config["json_props_options"]:
                        print("Extracting change history from issues")

                        for search_history in config["json_build"]["projects"]:
                            issue_history = search_history["issues"]
                            for history in issue_history:
                                key = history.get("key")
                                process_executor(
                                    parse_history_data,
                                    data=key,
                                    workers=workers,
                                    timeout=timeout,
                                )

                        print("Appending historic data into JSON structure")
                        # If there are any running threads, let's wait for
                        # their shutdown
                        sleep(flush)

                        for search_history in config["json_build"]["projects"]:
                            issue_history = search_history["issues"]
                            for history in issue_history:
                                key = history.get("key")
                                for sub_history in json_history_template[
                                    "history"
                                ]:
                                    sub_key = sub_history.get("key")
                                    sub_value = sub_history.get("value")
                                    if key == sub_key:
                                        history["history"] = sub_value

                print("Clearing temporary configuration data")
                project_settings.clear()
                project_config.clear()
                config["save_point"].clear()

            if ext.lower() == "json":
                json_field_builder()
            extend_file_type()
            for file in config["exports"]:
                path = path_builder(
                    folder,
                    file,
                )
                os.remove(path)

        if allow_media is True:
            data_frame(files_=temp_file)
            attach_read = file_reader(
                folder,
                temp_file,
                skip=True,
            )

            _change_flag_ = False
            for _attach_column_ in attach_read:
                for (
                    allow_row,
                    attach_header,
                ) in zip(
                    _attach_column_,
                    config["headers"],
                ):
                    if attach_header.get("column_name") == "Attachment":
                        if allow_row is None or allow_row == "":
                            pass
                        else:
                            _change_flag_ = True
                            _get_items_ = allow_row.split(";")
                            get_attachment = _get_items_.pop(-1)
                            get_parse_value = parse_media(get_attachment)
                            _get_items_.append(get_parse_value)
                            amend_attachment = ";".join(_get_items_)
                            _attach_column_[
                                attach_header.get("column_index")
                            ] = amend_attachment

            _file_headers_ = [x.get("column_name") for x in config["headers"]]
            print("Reconstructing file headers")
            file_writer(
                folder,
                temp_file,
                data=[_file_headers_],
                mark="many",
                mode="w+",
            )
            print(
                "Applying updated data into the CSV file"
            ) if _change_flag_ is True else print(
                "No change for attachment done to CSV file"
            )
            file_writer(
                folder,
                temp_file,
                data=attach_read,
                mark="many",
            )

        if exclude_fields:
            csv_field_change("exclude")
        elif include_fields:
            csv_field_change("include")

        if delimit:
            if delimit == ",":
                sys.stderr.write(
                    "The default CSV separator is a comma for the"
                    " delimit argument, no action taken."
                )
            else:
                csv_field_change()

        try:
            extend_format(extension)
        except (
            IndexError,
            KeyError,
            TypeError,
            AttributeError,
            ValueError,
            JiraOneErrors,
        ) as err:
            os.remove(
                path_builder(
                    folder,
                    temp_file,
                )
            )
            add_log(
                f"{err} on line {err.__traceback__.tb_lineno}"
                f" with {err.__traceback__} "
                f"{sys.__excepthook__(Exception, err, err.__traceback__)}",
                "error",
            )
            exit(f"An error has occurred: {err}")

        print(
            "Export Completed.File located at {}".format(
                path_builder(
                    folder,
                    final_file,
                )
            )
            if show_export_link is True
            else ""
        )

    @staticmethod
    def issue_count(
        jql: str,
    ) -> dict:
        """Returns the total count of issues within a
        JQL search phrase.

        :param jql: A valid JQL query (required)

        :type jql: str

         Example of the dict return value

        .. code-block:: json
           {
            "count": 2345,
            "max_page": 2
           }

        :return: a dictionary, containing issue count & max_page
        """
        from jiraone.utils import (
            DotNotation,
        )
        from jiraone.exceptions import (
            JiraOneErrors,
        )

        if jql is None:
            raise JiraOneErrors("value")
        elif jql is not None:
            if not isinstance(
                jql,
                str,
            ):
                raise JiraOneErrors(
                    "wrong",
                    "Invalid data structure " "received. " "Expected a string.",
                )
        (
            total,
            validate_query,
        ) = (
            0,
            LOGIN.get(endpoint.search_issues_jql(jql)
                      if LOGIN.api is False else
                      endpoint.search_cloud_issues(jql)
                      ),
        )
        if validate_query.status_code < 300:
            if LOGIN.api is False:
                total = validate_query.json()["total"]
            elif LOGIN.api is True:
                total = LOGIN.post(
                endpoint.search_issue_count(), payload={
                    "jql": jql
                }
            ).json()["count"]
        else:
            add_log(
                "Invalid JQL query received. Reason {} with status code: "
                "{} and addition info: {}".format(
                    validate_query.reason,
                    validate_query.status_code,
                    validate_query.json(),
                ),
                "debug",
            )
            raise JiraOneErrors(
                "value",
                "Your JQL query seems to be invalid"
                " as no issues were returned.",
            )

        calc = int(total / 1000)
        value = {
            "count": total,
            "max_page": calc if total > 1000 else 0,
        }
        return DotNotation(value)


    @staticmethod
    def view_issues(*,
                    project_key_or_id: Union[str, int] = None,
                    key_or_id: Union[str, int] = None) -> None:
        """View all issues and its properties"""


class Users:
    """
    This class helps to Generate the No of Users on Jira Cloud

    You can customize it to determine which user you're looking for.

    * It's method such as ``get_all_users`` displays active or inactive users,
       so you'll be getting all users

    """

    user_list = deque()

    def get_all_users(
        self,
        pull: str = "both",
        user_type: str = "atlassian",
        file: str = None,
        folder: str = Any,
        **kwargs,
    ) -> None:
        """Generates a list of users.

         :param pull: (options) for the argument

             * both: pulls out inactive and active users

             * active: pulls out only active users

             * inactive: pulls out inactive users

        :param user_type: (options) for the argument

             * atlassian: a normal Jira Cloud user

             * customer: this will be your JSM customers

             * app: this will be the bot users for any Cloud App

             * unknown: As the name suggest unknown user type

        :param file: String of the filename

        :param folder: String of the folder name

        :param kwargs: Additional keyword argument for the method.

         :return: Any
        """
        count_start_at = 0
        validate = LOGIN.get(endpoint.myself())

        while validate.status_code == 200:
            extract = LOGIN.get(
                endpoint.search_users(
                    count_start_at,
                    1000,
                )
            )
            results = json.loads(extract.content)
            self.user_activity(
                pull,
                user_type,
                results,
            )
            count_start_at += 1000
            print(
                "Current Record - At Row",
                count_start_at,
            )
            add_log(
                f"Current Record - At Row {count_start_at}",
                "info",
            )

            if not results:
                break
        else:
            sys.stderr.write(
                "Unable to connect to {} - Login Failed...".format(
                    LOGIN.base_url
                )
            )
            add_log(
                f"Login Failure on {LOGIN.base_url}, "
                f"due to {validate.reason}",
                "error",
            )
            sys.exit(1)

        if file is not None:
            self.report(
                category=folder,
                filename=file,
                **kwargs,
            )

    def report(
        self,
        category: str = Any,
        filename: str = "users_report.csv",
        **kwargs,
    ) -> None:
        """Creates a user report file in CSV format.
        :return: None
        """
        read = [d for d in self.user_list]
        file_writer(
            folder=category,
            file_name=filename,
            data=read,
            mark="many",
            **kwargs,
        )
        add_log(
            f"Generating report file on {filename}",
            "info",
        )

    def user_activity(
        self,
        status: str = Any,
        account_type: str = Any,
        results: List = Any,
    ) -> None:
        """Determines users activity.

        :return: None
        """

        # get both active and inactive users
        def stack(
            c: Any,
            f: List,
            s: Any,
        ) -> None:
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
            list_user = [
                each_user["accountId"],
                each_user["accountType"],
                each_user["displayName"],
                each_user["active"],
            ]
            stack(
                self,
                list_user,
                each_user,
            )

    def get_all_users_group(
        self,
        group_folder: str = "Groups",
        group_file_name: str = "group_file.csv",
        user_extraction_file: str = "group_extraction.csv",
        **kwargs,
    ) -> None:
        """Get all users and the groups associated to them on the Instance.
        :return: None
        """
        headers = [
            "Name",
            "AccountId",
            "Groups",
            "User status",
        ]
        file_writer(
            folder=group_folder,
            file_name=group_file_name,
            data=headers,
            **kwargs,
        )
        file_name = user_extraction_file
        self.get_all_users(
            file=file_name,
            folder=group_folder,
            **kwargs,
        )
        reader = file_reader(
            file_name=file_name,
            folder=group_folder,
            **kwargs,
        )
        for user in reader:
            account_id = user[0]
            display_name = user[2]
            active_status = user[3]
            load = LOGIN.get(endpoint.get_user_group(account_id))
            results = json.loads(load.content)
            get_all = [d["name"] for d in results]
            raw = [
                display_name,
                account_id,
                get_all,
                active_status,
            ]
            file_writer(
                folder=group_folder,
                file_name=group_file_name,
                data=raw,
            )

        print(
            "File extraction completed. Your file is located at {}".format(
                path_builder(
                    path=group_folder,
                    file_name=group_file_name,
                )
            )
        )
        add_log(
            "Get Users group Completed",
            "info",
        )

    def search_user(
        self,
        find_user: Union[
            str,
            list,
        ] = None,
        folder: str = "Users",
        **kwargs,
    ) -> Union[list, int,]:
        """Get a list of all cloud users and search for them by using the
        displayName.

        :param find_user: A list of user's displayName or a string of the
                          displayName

        :param folder: A name to the folder

        :param kwargs: Additional arguments

                   **options**

                   * skip (bool) - allows you to skip the header
                   of ``file_reader``

                   * delimiter (str) - allows a delimiter to the
                    ``file_reader`` function

                   * pull (str) - determines which user is available
                    e.g. "active", "inactive"

                   * user_type (str) - searches for user type
                    e.g "atlassian", "customer"

                   * file (str) - Name of the file

        """
        pull = kwargs["pull"] if "pull" in kwargs else "both"
        user_type = (
            kwargs["user_type"] if "user_type" in kwargs else "atlassian"
        )
        file = kwargs["file"] if "file" in kwargs else "user_file.csv"
        build = path_builder(
            folder,
            file,
        )

        if not os.path.isfile(build):
            open(
                build,
                mode="a",
            ).close()

        def get_users():
            if os.stat(build).st_size != 0:
                print(
                    f'The file "{file}" exist...',
                    end="",
                )
                os.remove(build)
                print(
                    "Updating extracted user...\n",
                    end="",
                )
                self.get_all_users(
                    pull=pull,
                    user_type=user_type,
                    file=file,
                    folder=folder,
                )
            else:
                print("Extracting users...")
                self.get_all_users(
                    pull=pull,
                    user_type=user_type,
                    file=file,
                    folder=folder,
                )

        if not self.user_list:
            get_users()
        CheckUser = namedtuple(
            "CheckUser",
            [
                "accountId",
                "account_type",
                "display_name",
                "active",
            ],
        )
        list_user = file_reader(
            file_name=file,
            folder=folder,
            **kwargs,
        )
        checker = []
        for _ in list_user:
            f = CheckUser._make(_)
            if isinstance(
                find_user,
                str,
            ):
                if find_user in f._asdict().values():
                    get_user = f.accountId
                    display_name = f.display_name
                    status = f.active
                    checker.append(
                        OrderedDict(
                            {
                                "accountId": get_user,
                                "displayName": display_name,
                                "active": status,
                            }
                        )
                    )
            if isinstance(
                find_user,
                list,
            ):
                for i in find_user:
                    if i in f._asdict().values():
                        get_user = f.accountId
                        display_name = f.display_name
                        status = f.active
                        checker.append(
                            OrderedDict(
                                {
                                    "accountId": get_user,
                                    "displayName": display_name,
                                    "active": status,
                                }
                            )
                        )

        return checker if checker else 0

    def mention_user(
        self,
        name,
    ) -> List[str]:
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


def path_builder(
    path: str = "Report",
    file_name: str = Any,
    **kwargs: Any,
) -> str:
    """Builds a dir path and file path in a directory.

    :param path: A path to declare absolute to where the script is executed.

    :param file_name: The name of the file being created

    :return: A string of the directory path or file path
    """
    base_dir = os.path.join(
        WORK_PATH,
        path,
    )
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
        add_log(
            f"Building Path {path}",
            "info",
        )
    base_file = os.path.join(
        base_dir,
        file_name,
    )
    return base_file


def file_writer(
    folder: str = WORK_PATH,
    file_name: str = None,
    data: Iterable = Any,
    mark: str = "single",
    **kwargs,
) -> None:
    """Reads and writes to a file, single or multiple rows or write
    as byte files.

    :param folder: A path to the name of the folder

    :param file_name: The name of the file being created.

    :param data: An iterable data, usually in form of a list.

    :param mark: Helps evaluate how data is created,
                  available options [“single”, “many”, “file”],
                  by default mark is set to “single”

    :param kwargs: Additional parameters

               **options**

               * mode: File mode, available options [“a”, “w”, “a+”, “w+”, “wb”],
                       by default the mode is set to “a+”.

               * content: Outputs the file in bytes if mode is in bytes else in
                           strings

               * delimiter: defaults to comma - datatype (strings)

               * encoding: defaults to utf-8 - datatype (strings)

               * errors: defaults to replace - datatype (strings)

    .. versionchanged:: 0.7.3

    errors - added keyword argument which helps determine how
    encoding and decoding errors are handled

    .. versionchanged:: 0.6.3

    encoding - added keyword argument encoding to handle encoding
    issues on Windows like device.

    :return: Any
    """
    from platform import (
        system,
    )

    mode: str = kwargs.get("mode", "a+")
    content: Union[
        str,
        bytes,
    ] = (
        kwargs.get("content") if "content" in kwargs else None
    )

    delimiter = kwargs["delimiter"] if "delimiter" in kwargs else ","
    file = path_builder(
        path=folder,
        file_name=file_name,
    )
    encoding = kwargs["encoding"] if "encoding" in kwargs else "utf-8"
    errors = kwargs["errors"] if "errors" in kwargs else "replace"
    # Bug:fix:JIR-8 on https://github.com/princenyeche/jiraone/issues/89
    windows = (
        open(
            file,
            mode,
            encoding=encoding,
            newline="",
            errors=errors,
        )
        if system() == "Windows" and mark != "file"
        else open(
            file,
            mode,
        )
        if isinstance(
            content,
            bytes,
        )
        else open(
            file,
            mode,
            encoding=encoding,
            errors=errors,
        )
    )
    if mode:
        with windows as f:
            write = csv.writer(
                f,
                delimiter=delimiter,
            )
            if mark == "single":
                write.writerow(data)
            if mark == "many":
                write.writerows(data)
            if mark == "file":
                f.write(content)
            add_log(
                f"Writing to file {file_name}",
                "info",
            )


def file_reader(
    folder: str = WORK_PATH,
    file_name: str = None,
    mode: str = "r",
    skip: bool = False,
    **kwargs,
) -> Union[List[List[str]], str,]:
    """Reads a CSV file and returns a list comprehension of the data or
    reads a byte into strings.

    :param folder: A path to the name of the folder

    :param file_name: The name of the file being created

    :param mode: File mode, available options [“r”, “rb”]

    :param skip: True allows you to skip the header if the file has any.
                 Otherwise, defaults to False

    :param kwargs: Additional parameters

              **options**

              * content: True allows you to read a byte file. By default,
                         it is set to False
              * encoding: Standard encoding strings. e.g “utf-8”.

              * delimiter: defaults to comma.

              * errors: defaults to replace


    .. versionchanged:: 0.7.3

    errors - added keyword argument which helps determine how
    encoding and decoding errors are handled


    :return: A list comprehension data or binary data
    """
    from platform import (
        system,
    )

    content: bool = kwargs.get("content", False)

    file = path_builder(
        path=folder,
        file_name=file_name,
    )
    encoding = kwargs["encoding"] if "encoding" in kwargs else "utf-8"
    errors = kwargs["errors"] if "errors" in kwargs else "replace"
    delimiter = kwargs["delimiter"] if "delimiter" in kwargs else ","
    windows = (
        open(
            file,
            mode,
            encoding=encoding,
            newline="",
            errors=errors,
        )
        if system() == "Windows" and content is False
        else open(
            file,
            mode,
        )
    )
    if mode:
        with windows as f:
            read = csv.reader(
                f,
                delimiter=delimiter,
            )
            if skip is True:
                next(
                    read,
                    None,
                )
            if content is True:
                feed = (
                    f.read()
                    if "encoding" not in kwargs
                    else f.read().encode(encoding)
                )
            load = [d for d in read]
            add_log(
                f"Read file {file_name}",
                "info",
            )
            return load if content is False else feed


def replacement_placeholder(
    string: str = None,
    data: List = None,
    iterable: List = None,
    row: int = 2,
) -> Any:
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
                result = [
                    lines.replace(
                        string,
                        iterable[count],
                        1,
                    )
                    for lines in data
                ]
        if count > 0:
            if string in result[row]:
                result = [
                    lines.replace(
                        string,
                        iterable[count],
                        1,
                    )
                    for lines in result
                ]
        count += 1
        if count > length:
            break
    return result


def delete_attachments(
    file: Optional[str] = None,
    search: Union[
        str,
        Dict,
        List,
        int,
    ] = None,
    delete: bool = True,
    extension: Union[
        str,
        List,
    ] = None,
    **kwargs: Union[
        str,
        bool,
    ],
) -> None:
    """
    A function that helps to delete attachments on Jira issues.
    You can export a JQL search of issues
    containing the ``Attachment`` column either in CSV or xlsx
    from your advanced filter search,
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

    :param file: A file export of issues from Jira which includes
                 the ``attachment columns``

    :param search: A search parameter for issues e.g. issue key or JQL query

    :param extension: A file extension to focus on while deleting.

    :param delete: A decision to delete or not delete the attachments.
                   Defaults to ``True``

    :param kwargs: Additional arguments

                 **Available options**

                 * by_user: Search by user accountId and delete attachments.
                            You can also combine the extension parameter.
                            This will only work when using the ``search``
                            parameter.

                 * by_size: Search by allocated file size and delete the
                             attachment. You can combine the extension and
                             ``by_user`` parameter with this argument.

                 * by_date: Search by date_range from when the attachment was
                            created until the initiator's current time.
                            Then delete the attachment.
                            You can combine this argument with all
                            other arguments provided with the search parameter.

                 * allow_cp: Allows the ability to trigger and save a
                  checkpoint.

                 * saved_file: Provides a generic name for the checkpoint
                 save file.

                 * delimiter: Allows you to change the delimiter used to
                 read the file used by ``file`` parameter.

    :return: None
    """
    by_user: Optional[List] = kwargs.get("by_user", None)
    by_size: Optional[str] = kwargs.get("by_size", None)
    by_date: Optional[str] = kwargs.get("by_date", None)
    from jiraone.exceptions import (
        JiraOneErrors,
    )
    from datetime import (
        datetime,
        timedelta,
    )
    from jiraone.utils import DateFormat

    if LOGIN.get(endpoint.myself()).status_code > 300:
        add_log(
            "Authentication failed. Please check your "
            "credential data to determine what went wrong.",
            "error",
        )
        raise JiraOneErrors(
            "login",
            "Authentication failed. Please check your credentials.",
        )
    search_path = None
    folder: str = "DATA"
    allow_cp: bool = "allow_cp" not in kwargs
    saved_file: str = (
        "data_block.json"
        if "saved_file" not in kwargs
        else kwargs["saved_file"]
    )
    back_up: bool = False
    attach_load = []
    data_file = path_builder(
        folder,
        file_name=saved_file,
    )

    def time_share(
        _time: str,
        _items=None,
    ) -> bool:
        """
        Calculate the time difference it takes with the date and now to
        determine if deletion is possible.

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
        time_hold_one = {
            "minute": minutes,
            "hour": hours,
            "day": days,
            "week": weeks,
            "month": months,
            "year": years,
        }
        time_factors = {}
        time_hold_two = {
            "minutes": minutes,
            "hours": hours,
            "days": days,
            "weeks": weeks,
            "months": months,
            "years": years,
        }

        times = []
        if isinstance(
            _time,
            str,
        ):
            number = re.compile(r"(?:\d+)")
            string_one = re.compile(r"(?:[a-zA-Z]{4,7})")
            if number.search(_time) is not None:
                times.append(number.search(_time).group())
            if string_one.search(_time) is not None:
                times.append(string_one.search(_time).group())
        else:
            add_log(
                "Invalid time parameter received. Expected a "
                'string but got "{}"'.format(type(_time)),
                "debug",
            )
            raise JiraOneErrors(
                "wrong",
                "Invalid time parameter received. Expected a "
                'string but got "{}"'.format(type(_time)),
            )

        if times[1]:
            if times[1] in time_hold_one:
                time_factor = time_hold_one
                selection = "time_factor"
            elif times[1] in time_hold_two:
                time_factors = time_hold_two
                selection = "time_factors"
            else:
                add_log(
                    'Invalid option "{}" detected as `time_info` '
                    'for "by_date" argument'.format(by_date),
                    "error",
                )
                raise JiraOneErrors(
                    "value",
                    "We're unable to determine your precise "
                    'date range with "{}"'.format(by_date),
                )

        def time_delta(
            val: int,
            cet: str,
        ) -> tuple:
            """
            Return a tuple to determine what the expected datetime are.

            :param val: An integer of the datetime.

            :param cet: A string denoting the name to time.

            :return: A tuple of probably time factor.
            """

            _time_ = None
            time_check_ = (
                time_factor if selection == "time_factor" else time_factors
            )
            if cet in time_check_:
                _time_ = val * time_check_[cet]
            return (
                _time_,
                list(time_check_.keys())[list(time_check_.keys()).index(cet)],
            )

        if len(times) > 0:
            issue_time = datetime.strptime(
                _items.get("created"),
                DateFormat.YYYY_MM_dd_HH_MM_SS_MS_TZ,
            )

            present = datetime.strftime(
                datetime.astimezone(datetime.now()),
                DateFormat.YYYY_MM_dd_HH_MM_SS_MS_TZ,
            )
            parse_present = datetime.strptime(
                present,
                DateFormat.YYYY_MM_dd_HH_MM_SS_MS_TZ,
            )
            time_check = (
                time_factor if selection == "time_factor" else time_factors
            )
            if times[1] in time_check:
                ask_time = time_delta(
                    int(times[0]),
                    times[1],
                )
                d_range = (
                    [
                        "days",
                        "months",
                        "years",
                        "weeks",
                    ]
                    if selection == "time_factors"
                    else [
                        "day",
                        "month",
                        "year",
                        "week",
                    ]
                )
                d_min = "minute" if selection == "time_factor" else "minutes"
                past_time = (
                    timedelta(days=ask_time[0])
                    if ask_time[1] in d_range
                    else timedelta(minutes=ask_time[0])
                    if ask_time[1] == d_min
                    else timedelta(hours=ask_time[0])
                )
                diff = parse_present - past_time
                if diff < issue_time:
                    return True

        return False

    def regulator(
        size: str,
        block=None,
    ) -> bool:
        """
        Determine the size of an attachment.

        :param size: The size in byte of an attachment.

        :param block: An iterable that contains the attachment data

        :return: Returns a boolean output to determine if an attachment is
                 greater or lesser than size parameter.
        """
        chars = []
        giga_byte = 1000 * 1000 * 1000
        mega_byte = 1000 * 1000
        kilo_byte = 1000
        if isinstance(
            size,
            str,
        ):
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
            add_log(
                "Invalid size parameter received. "
                'Expected a string but got "{}"'.format(type(size)),
                "debug",
            )
            raise JiraOneErrors(
                "wrong",
                "Invalid size parameter received. "
                'Expected a string but got "{}"'.format(type(size)),
            )

        if len(chars) > 0:
            symbol = chars[0]
            my_num = int(chars[1])
            this = chars[2].lower()
            if this in [
                "mb",
                "kb",
                "gb",
            ]:
                byte_size = (
                    my_num * mega_byte
                    if this == "mb"
                    else my_num * giga_byte
                    if this == "gb"
                    else my_num * kilo_byte
                    if this == "kb"
                    else my_num
                )
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

    def get_ext(
        ex,
    ) -> Union[str, List,]:
        """
        Determine the extension and cycle through it.

        :param ex: An extension checker

        :return: A string or a list item
        """
        if isinstance(
            ex,
            str,
        ):
            if "," in ex:
                ex = ex.lower().split(",")
                return ex
            return ex.lower()
        if isinstance(
            ex,
            list,
        ):
            return [x.lower() for x in ex]

    def ex_validator(
        func,
        _item=None,
        tp: bool = True,
    ) -> bool:
        """
        Determines if an extension supplied is equivalent to what it is all
        about prior to deletion.

        :param func: A str or list value of extensions

        :param _item: An iterable of a file extension

        :param tp: Changes context between file or search mode parameter
                   for this function.

        :return: True or False for the query
        """
        if isinstance(
            func,
            str,
        ):
            _ex_name = (
                (
                    f".{_item.get('filename').split('.')[-1].lower()}"
                    if "." in func
                    else _item.get("filename").split(".")[-1].lower()
                )
                if tp is True
                else (
                    f".{_item[-1].split('.')[-1].lower()}"
                    if "." in func
                    else _item[-1].split(".")[-1].lower()
                )
            )
            return _ex_name == func
        if isinstance(
            func,
            list,
        ):
            _ex_name = (
                (
                    f".{_item.get('filename').split('.')[-1].lower()}"
                    if [f for f in func if "." in f]
                    else _item.get("filename").split(".")[-1].lower()
                )
                if tp is True
                else (
                    f".{_item[-1].split('.')[-1].lower()}"
                    if [f for f in func if "." in f]
                    else _item[-1].split(".")[-1].lower()
                )
            )
            return _ex_name in func
        return False

    def get_attachments(
        items: Dict,
    ) -> None:
        """
        Helps to get a list of attachments on an issue.

        :param items: A dictionary of search results.

        :return: None
        """
        nonlocal attach_load, count, depth, next_count # noqa: F824
        infinity_point = data_brick["point"]
        issues = items["issues"][data_brick["point"]:]
        attach_load = (
            data_brick["data_block"] if back_up is True else attach_load
        )
        count = (
            set_up["iter"]
            if back_up is True and depth == 1
            else data_brick["iter"]
        )

        def inf_block(
            atl: bool = False,
        ):
            """
            A function that updates data_brick.

            :param atl: Indicates whether a condition exist that favours
                        search attachment or not.

            :return: None
            """
            data_brick.update(
                {
                    "data_block": attach_load,
                    "key": keys,
                    "status": "in_progress",
                    "point": infinity_point,
                }
            ) if atl is False else data_brick.update(
                {
                    "key": keys,
                    "status": "in_progress",
                    "point": infinity_point,
                }
            )

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
                            "accountid": attach.get("author").get("accountId"),
                        }
                        print(
                            "Accessing attachments {} | Key: {}".format(
                                attach.get("filename"),
                                keys,
                            )
                        )
                        add_log(
                            "Accessing attachments {} | Key: {}".format(
                                attach.get("filename"),
                                keys,
                            ),
                            "info",
                        )
                        attach_load.append(attach_item)
                        inf_block()
                else:
                    inf_block(atl=True)
            else:
                inf_block(atl=True)
            json.dump(
                data_brick,
                open( # noqa
                    data_file,
                    mode="w+",
                    encoding="utf-8",
                ),
                indent=4,
            ) if allow_cp is True else None
            infinity_point += 1

    data_brick = {}
    set_up = {}

    def data_wipe(
        del_,
        counts_,
        usr: bool = False,
        fl: bool = False,
        _items_=None,
    ) -> None:
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
            print(
                'Deleting attachment "{}" | Key: {}'.format(
                    _items_.get("filename") if fl is False else _items_[0],
                    _items_.get("key") if fl is False else _items_[1],
                )
            ) if usr is False else print(
                'Deleting attachment by user {} "{}" | Key: {}'.format(
                    _items_.get("author"),
                    _items_.get("filename"),
                    _items_.get("key"),
                )
            )
            add_log(
                'The Attachments "{}" has been deleted | Key: {}'.format(
                    _items_.get("filename") if fl is False else _items_[0],
                    _items_.get("key") if fl is False else _items_[1],
                ),
                "info",
            )
        else:
            data_brick.update({"saves" if fl is False else "iter": counts_})
            print(
                'Unable to delete attachment "{}" | Key: {}'.format(
                    _items_.get("filename") if fl is False else _items_[0],
                    _items_.get("key") if fl is False else _items_[1],
                )
            ) if usr is False else print(
                'Unable to delete attachment by user {} "{}" | Key: {}'.format(
                    _items_.get("author"),
                    _items_.get("filename"),
                    _items_.get("key"),
                )
            )
            add_log(
                'Attachment deletion of "{}" failed with reason "{}" '
                "| Key: {}".format(
                    _items_.get("filename") if fl is False else _items_[0],
                    del_.reason,
                    _items_.get("key") if fl is False else _items_[1],
                ),
                "info",
            )

    if allow_cp is True:
        if os.path.isfile(data_file) and os.stat(data_file).st_size != 0:
            user_input = input(
                "An existing save point exist from your last search, "
                "do you want to use it? (Y/N) \n"
            )
            set_up = json.load(open(data_file))
            if user_input.lower() in [
                "y",
                "yes",
            ]:
                back_up = True
            else:
                print("Starting search from scratch.")
                add_log(
                    "Starting search from scratch, "
                    "any previous data will be removed",
                    "info",
                )
    descriptor = (
        os.open(
            data_file,
            flags=os.O_CREAT,
        )
        if allow_cp is True
        else None
    )
    os.close(descriptor) if allow_cp is True else None
    (
        count,
        cycle,
        step,
        next_count # used for new search API for Jira cloud,
    ) = (
        0,
        0,
        0,
        None,
    )
    if file is None:
        if search is None:
            add_log(
                "The search parameter can't be None when "
                "you have not provided a file input data.",
                "debug",
            )
            raise JiraOneErrors(
                "value",
                "Search parameter can't be None if a " "file is not provided.",
            )
        search_path = search
    elif file is not None:
        key_index = 0
        attach_index = []
        temp_reader = file_reader(
            file_name=file,
            **kwargs,
        )
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

        reader = file_reader(
            file_name=file,
            skip=True,
            **kwargs,
        )
        new_data_form = deque()
        do_once = 0
        for issue in reader:
            _attach_ = {}
            key = issue[key_index]
            attach_pattern = re.compile(
                r"(?:\w{4,5}:\/\/\w*\.+\w+.\w+\/[s]\w*\/.\w.+\.\w+)"
            )
            if len(attach_index) > 0:
                attach_loop = 0
                for column in attach_index:
                    attach_loop += 1
                    _attach_.update(
                        {"attach_{}".format(attach_loop): issue[column]}
                    )
            # Find every attachment in the attachment column to
            # determine the attachments
            for (
                each_attach,
                attach_,
            ) in _attach_.items():
                if ";" in attach_:
                    break_ = attach_.split(";")
                    files_ = break_[-1]
                    new_data_form.append(
                        [
                            key,
                            files_,
                        ]
                    )
            do_once += 1
            if len(_attach_) == 0 and do_once == 1:
                print(
                    "Attachment not processed, file structure could be "
                    "empty or not properly formatted."
                )
                add_log(
                    f"It seems that the attachments URL "
                    f"could not be determined from the {file}",
                    "debug",
                )
            # Use regex to find other attachments links that are in
            # other fields.
            # The below would likely find one or more links or none if it can't.
            for data in issue:
                if attach_pattern.match(data) is not None:
                    _files = attach_pattern.match(data).group()
                    new_data_form.append(
                        [
                            key,
                            _files,
                        ]
                    )

        new_list = []
        for arrange_attach in new_data_form:
            if arrange_attach[1] is not None:
                new_list.append(
                    [
                        arrange_attach[0],
                        arrange_attach[1],
                    ]
                )
        new_data_form.clear()
        split_file = file.split(".")[-2]
        new_file = f"{split_file}_temp.csv"
        file_writer(
            folder,
            file_name=new_file,
            data=new_list,
            mark="many",
            mode="w+",
        )
        read_file = file_reader(
            folder,
            file_name=new_file,
        )

        step = (
            0
            if back_up is False and os.stat(data_file).st_size == 0
            else set_up["iter"]
        )
        count = step
        for item in read_file[step:]:
            attach_ = item[1].split("/")
            attach_id = attach_[-2]
            if delete is True:
                if extension is not None:
                    if ex_validator(
                        get_ext(extension),
                        attach_,
                        tp=False,
                    ):
                        delete_ = LOGIN.delete(
                            endpoint.issue_attachments(attach_id=attach_id)
                        )
                        data_wipe(
                            delete_,
                            count,
                            fl=True,
                            _items_=[
                                attach_[-1],
                                item[0],
                            ],
                        )
                else:
                    delete_ = LOGIN.delete(
                        endpoint.issue_attachments(attach_id=attach_id)
                    )
                    data_wipe(
                        delete_,
                        count,
                        fl=True,
                        _items_=[
                            attach_[-1],
                            item[0],
                        ],
                    )
            else:
                data_brick.update({"iter": count})
                print(
                    "Safe mode on: Attachment will not be deleted "
                    '"{}" | Key: {}'.format(
                        attach_[-1],
                        item[0],
                    )
                )
                add_log(
                    "Safe mode on: Attachment will not be deleted "
                    '"{}" | Key: {}'.format(
                        attach_[-1],
                        item[0],
                    ),
                    "info",
                )
            count += 1
            json.dump(
                data_brick,
                open( # noqa
                    data_file,
                    mode="w+",
                    encoding="utf-8",
                ),
                indent=4,
            ) if allow_cp is True else None
        os.remove(
            path_builder(
                folder,
                file_name=new_file,
            )
        )
    if search_path is not None:
        query = (
            f"key in ({search_path})"
            if isinstance(
                search_path,
                (
                    str,
                    int,
                ),
            )
            else "key in {}".format(tuple(search_path))
            if isinstance(
                search_path,
                list,
            )
            else search_path["jql"]
            if isinstance(
                search_path,
                dict,
            )
            else sys.stderr.write(
                "Unexpected datatype received. "
                "Example on https://jiraone.readthedocs.io "
            )
        )
        data_brick["status"] = (
            set_up["status"]
            if "status" in set_up and back_up is True
            else "in_progress"
        )
        depth: int = 1
        while True:
            load = (
                LOGIN.get(
                    endpoint.search_issues_jql(
                        query=set_up["query"],
                        start_at=set_up["iter"],
                        max_results=100,
                    ) if LOGIN.api is False else
                    endpoint.search_cloud_issues(
                        query=set_up["query"],
                        next_page=set_up["iters"],
                        fields=None,
                        max_results=100,
                    )
                )
                if back_up is True and depth == 1
                else LOGIN.get(
                    endpoint.search_issues_jql(
                        query=query,
                        start_at=count,
                        max_results=100,
                    ) if LOGIN.api is False else
                    endpoint.search_cloud_issues(
                        query=query,
                        next_page=next_count,
                        fields=None,
                        max_results=100,
                    )
                )
            )
            if data_brick["status"] == "complete":
                open_ = json.load(open(data_file)) if allow_cp is True else {}
                attach_load = (
                    open_["data_block"] if "data_block" in open_ else []
                )
                break
            if load.status_code < 300:
                data_ = load.json()
                cycle = 0
                print(
                    "Extracting attachment details on row {}".format(
                        (set_up["iter"] if LOGIN.api is False else set_up["iters"])
                        if back_up is True and depth == 1
                        else (count if LOGIN.api is False else next_count)
                    )
                )
                print("*" * 100)
                add_log(
                    "Extracting attachment details on row {}".format(
                        (set_up["iter"] if LOGIN.api is False else set_up["iters"])
                        if back_up is True and depth == 1
                        else (count if LOGIN.api is False else next_count)
                    ),
                    "info",
                )
                data_brick.update(
                    {
                        "iter": set_up["iter"]
                        if back_up is True and depth == 1
                        else count,
                        "iters": set_up["iters"]
                        if back_up is True and depth == 1
                        else next_count,
                        "query": set_up["query"]
                        if back_up is True and depth == 1
                        else query,
                        "data_block": set_up["data_block"]
                        if back_up is True and depth == 1
                        else attach_load,
                        "point": set_up["point"] + 1
                        if back_up is True and depth == 1
                        else 0,
                    }
                )
                if LOGIN.api is False:
                    if count > data_["total"]:
                        data_brick.update({"status": "complete"})
                        json.dump(
                            data_brick,
                            open( # noqa
                                data_file,
                                mode="w+",
                                encoding="utf-8",
                            ),
                            indent=4,
                        ) if allow_cp is True else None
                        add_log(
                            "Extraction is completed, "
                            "deletion of attachments on the next step",
                            "info",
                        )
                        break

                get_attachments(data_)
                if LOGIN.api is True:
                    if "nextPageToken" not in data_:
                        data_brick.update({"status": "complete"})
                        json.dump(
                            data_brick,
                            open( # noqa
                                data_file,
                                mode="w+",
                                encoding="utf-8",
                            ),
                            indent=4,
                        ) if allow_cp is True else None
                        add_log(
                            "Extraction is completed, "
                            "deletion of attachments on the next step",
                            "info",
                        )
                        break
                next_count = data_.get("nextPageToken", None)
            count += 100 # if api is False use a different search API

            if back_up is True and depth == 1:
                data_brick["iter"] = count
                data_brick["iters"] = next_count
                back_up = False
            depth += 2
            if load.status_code > 300:
                cycle += 1
                if cycle > 99:
                    add_log(
                        "Trying to search for the issues with "
                        'query "{}" returned a "{}" '
                        'error with reason "{}".'.format(
                            query,
                            load.status_code,
                            load.reason,
                        ),
                        "error",
                    )
                    raise JiraOneErrors(
                        "value",
                        'It seems that the search "{}" cannot be '
                        "retrieved as we've attempted it {} times".format(
                            query,
                            cycle,
                        ),
                    )

        length = len(attach_load)
        if length > 0:
            _open_ = json.load(open(data_file)) if allow_cp is True else {}
            data_brick["data_block"] = attach_load
            data_brick["iter"] = _open_["iter"] if "iter" in _open_ else 0
            data_brick["query"] = (
                _open_["query"] if "query" in _open_ else query
            )
            data_brick["saves"] = _open_["saves"] if "saves" in _open_ else 0
            step = 0 if back_up is False else data_brick["saves"]
            count = step
            for each_item in attach_load[step:]:
                if delete is True:
                    if extension is not None:
                        if ex_validator(
                            get_ext(extension),
                            each_item,
                        ):
                            if by_user is not None:
                                if each_item.get("accountid") in by_user:
                                    if by_size is not None:
                                        if regulator(
                                            by_size,
                                            each_item,
                                        ):
                                            if by_date is not None:
                                                if time_share(
                                                    by_date,
                                                    each_item,
                                                ):
                                                    delete_ = LOGIN.delete(
                                                        endpoint.issue_attachments(
                                                            attach_id=each_item.get(
                                                                "id"
                                                            )
                                                        )
                                                    )
                                                    data_wipe(
                                                        delete_,
                                                        count,
                                                        usr=True,
                                                        _items_=each_item,
                                                    )
                                            else:
                                                delete_ = LOGIN.delete(
                                                    endpoint.issue_attachments(
                                                        attach_id=each_item.get(
                                                            "id"
                                                        )
                                                    )
                                                )
                                                data_wipe(
                                                    delete_,
                                                    count,
                                                    usr=True,
                                                    _items_=each_item,
                                                )
                                    else:
                                        if by_date is not None:
                                            if time_share(
                                                by_date,
                                                each_item,
                                            ):
                                                delete_ = LOGIN.delete(
                                                    endpoint.issue_attachments(
                                                        attach_id=each_item.get(
                                                            "id"
                                                        )
                                                    )
                                                )
                                                data_wipe(
                                                    delete_,
                                                    count,
                                                    usr=True,
                                                    _items_=each_item,
                                                )
                                        else:
                                            delete_ = LOGIN.delete(
                                                endpoint.issue_attachments(
                                                    attach_id=each_item.get(
                                                        "id"
                                                    )
                                                )
                                            )
                                            data_wipe(
                                                delete_,
                                                count,
                                                usr=True,
                                                _items_=each_item,
                                            )
                            else:
                                if by_size is not None:
                                    if regulator(
                                        by_size,
                                        each_item,
                                    ):
                                        if by_date is not None:
                                            if time_share(
                                                by_date,
                                                each_item,
                                            ):
                                                delete_ = LOGIN.delete(
                                                    endpoint.issue_attachments(
                                                        attach_id=each_item.get(
                                                            "id"
                                                        )
                                                    )
                                                )
                                                data_wipe(
                                                    delete_,
                                                    count,
                                                    _items_=each_item,
                                                )
                                        else:
                                            delete_ = LOGIN.delete(
                                                endpoint.issue_attachments(
                                                    attach_id=each_item.get(
                                                        "id"
                                                    )
                                                )
                                            )
                                            data_wipe(
                                                delete_,
                                                count,
                                                _items_=each_item,
                                            )
                                else:
                                    if by_date is not None:
                                        if time_share(
                                            by_date,
                                            each_item,
                                        ):
                                            delete_ = LOGIN.delete(
                                                endpoint.issue_attachments(
                                                    attach_id=each_item.get(
                                                        "id"
                                                    )
                                                )
                                            )
                                            data_wipe(
                                                delete_,
                                                count,
                                                _items_=each_item,
                                            )
                                    else:
                                        delete_ = LOGIN.delete(
                                            endpoint.issue_attachments(
                                                attach_id=each_item.get("id")
                                            )
                                        )
                                        data_wipe(
                                            delete_,
                                            count,
                                            _items_=each_item,
                                        )
                    else:
                        if by_user is not None:
                            if each_item.get("accountid") in by_user:
                                if by_size is not None:
                                    if regulator(
                                        by_size,
                                        each_item,
                                    ):
                                        if by_date is not None:
                                            if time_share(
                                                by_date,
                                                each_item,
                                            ):
                                                delete_ = LOGIN.delete(
                                                    endpoint.issue_attachments(
                                                        attach_id=each_item.get(
                                                            "id"
                                                        )
                                                    )
                                                )
                                                data_wipe(
                                                    delete_,
                                                    count,
                                                    usr=True,
                                                    _items_=each_item,
                                                )
                                        else:
                                            delete_ = LOGIN.delete(
                                                endpoint.issue_attachments(
                                                    attach_id=each_item.get(
                                                        "id"
                                                    )
                                                )
                                            )
                                            data_wipe(
                                                delete_,
                                                count,
                                                usr=True,
                                                _items_=each_item,
                                            )
                                else:
                                    if by_date is not None:
                                        if time_share(
                                            by_date,
                                            each_item,
                                        ):
                                            delete_ = LOGIN.delete(
                                                endpoint.issue_attachments(
                                                    attach_id=each_item.get(
                                                        "id"
                                                    )
                                                )
                                            )
                                            data_wipe(
                                                delete_,
                                                count,
                                                usr=True,
                                                _items_=each_item,
                                            )
                                    else:
                                        delete_ = LOGIN.delete(
                                            endpoint.issue_attachments(
                                                attach_id=each_item.get("id")
                                            )
                                        )
                                        data_wipe(
                                            delete_,
                                            count,
                                            usr=True,
                                            _items_=each_item,
                                        )
                        else:
                            if by_size is not None:
                                if regulator(
                                    by_size,
                                    each_item,
                                ):
                                    if by_date is not None:
                                        if time_share(
                                            by_date,
                                            each_item,
                                        ):
                                            delete_ = LOGIN.delete(
                                                endpoint.issue_attachments(
                                                    attach_id=each_item.get(
                                                        "id"
                                                    )
                                                )
                                            )
                                            data_wipe(
                                                delete_,
                                                count,
                                                _items_=each_item,
                                            )
                                    else:
                                        delete_ = LOGIN.delete(
                                            endpoint.issue_attachments(
                                                attach_id=each_item.get("id")
                                            )
                                        )
                                        data_wipe(
                                            delete_,
                                            count,
                                            _items_=each_item,
                                        )
                            elif by_date is not None:
                                if time_share(
                                    by_date,
                                    each_item,
                                ):
                                    delete_ = LOGIN.delete(
                                        endpoint.issue_attachments(
                                            attach_id=each_item.get("id")
                                        )
                                    )
                                    data_wipe(
                                        delete_,
                                        count,
                                        _items_=each_item,
                                    )
                            else:
                                delete_ = LOGIN.delete(
                                    endpoint.issue_attachments(
                                        attach_id=each_item.get("id")
                                    )
                                )
                                data_wipe(
                                    delete_,
                                    count,
                                    _items_=each_item,
                                )
                else:
                    data_brick.update({"saves": count})
                    print(
                        "Safe mode on: Attachment will not be deleted "
                        '"{}" | Key: {}'.format(
                            each_item.get("filename"),
                            each_item.get("key"),
                        )
                    )

                count += 1
                json.dump(
                    data_brick,
                    open( # noqa
                        data_file,
                        mode="w+",
                        encoding="utf-8",
                    ),
                    indent=4,
                ) if allow_cp is True else None

        else:
            print(
                "The data search seems to be empty. Please "
                "recheck your search criteria."
            )
            add_log(
                "Searching for attachment did not yield any result. "
                "It seems the search criteria"
                " does not have attachments.",
                "debug",
            )

    os.remove(data_file) if allow_cp is True else None


USER = Users()
PROJECT = Projects()
comment = PROJECT.comment_on
issue_export = PROJECT.export_issues
