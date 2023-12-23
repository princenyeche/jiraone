import os
import json
import unittest
from jiraone import (
    LOGIN,
    endpoint,
    issue_export,
    path_builder,
    PROJECT,
    file_reader,
)


class JiraOne(unittest.TestCase):
    def setUp(self):
        """Configure test case"""
        user = os.environ.get("JIRAONEUSERNAME") or "email"
        password = os.environ.get("JIRAONEUSERPASS") or "token"
        link = (
            os.environ.get("JIRAONEUSERURL")
            or "https://yourinstance.atlassian.net"
        )
        LOGIN(user=user, password=password, url=link)
        self.payload = {
            "fields": {
                "project": {"key": "IP"},
                "summary": "A new summary",
                "description": "Testing creation of issues",
                "issuetype": {"name": "Task"},
                "labels": ["test"],
            }
        }
        self.attachment = (
            os.environ.get("JIRAONEIMAGEURL") + "/image-size/large?v=v2&px=999"
        )
        self.token = os.environ.get("JIRAONEAPITOKEN") or "token"
        self.issue_key = "IP-5"
        self.issue_keys = "AT2-1"
        self.jql = "project = AT2 order by created desc"

    def test_login_basic_auth(self):
        """Test the LOGIN authentication for basic auth"""
        load = LOGIN.get(endpoint.myself())
        self.assertTrue(load.status_code == 200,
                        "Login not successful")

    def test_context_login_session(self):
        """Test a context login using LOGIN.session"""
        LOGIN.session.headers = LOGIN.headers
        LOGIN.session.auth = LOGIN.auth_request
        session = LOGIN.session.get(endpoint.myself())
        self.assertTrue(session.status_code < 300,
                        "Session context failed")

    def test_endpoints(self):
        """Test endpoint constant extraction"""
        load = LOGIN.get(endpoint.myself())
        self.assertTrue(load.status_code < 300,
                        "Unable to load self endpoint")

    def test_data_extraction(self):
        """Test response data from an endpoint"""
        load = LOGIN.get(endpoint.get_all_priorities())
        if load.status_code == 200:
            e = json.loads(load.content)
            self.assertIsInstance(e, (list, dict),
                                  "Extraction failed")

    def test_issue_export_csv(self):
        """Test CSV issue export"""
        jql = self.jql
        path = path_builder("TEST", "test_sample.csv")
        # testing parameters
        issue_export(
            jql=jql, extension="csv", folder="TEST",
            final_file="CSV_test_sample"
        )
        self.assertTrue(
            os.path.isfile(path),
            "Unable to detect CSV file for issue export"
        )

    def test_issue_export_json(self):
        """Test JSON issue export"""
        jql = self.jql
        path = path_builder("TEST", "test_sample.json")
        issue_export(
            jql=jql, extension="json", folder="TEST",
            final_file="JSON_test_sample"
        )
        self.assertTrue(
            os.path.isfile(path),
            "Unable to detect JSON file for issue export"
        )

    def test_time_in_status(self):
        """Test for time in status for CSV or JSON"""
        from jiraone.module import time_in_status

        key = self.issue_key
        json_file = path_builder("TEST",
                                 "test_time_in_status.json")
        csv_file = path_builder("TEST",
                                "test_time_in_status.csv")
        time_in_status(
            PROJECT,
            key,
            reader=file_reader,
            output_format="json",
            report_folder="TEST",
            output_filename="test_json_time_in_status",
            login=LOGIN,
            pprint="timestamp",
        )
        self.assertTrue(
            os.path.isfile(json_file),
            "Unable to detect JSON file for time in status",
        )
        time_in_status(
            PROJECT,
            key,
            reader=file_reader,
            output_format="csv",
            report_folder="TEST",
            output_filename="test_csv_time_in_status",
            login=LOGIN,
            pprint=True,
        )
        self.assertTrue(
            os.path.isfile(csv_file),
            "Unable to detect CSV file for time in status",
        )

    def test_history_extraction(self):
        """Test for issue history extraction"""
        jql = "key = {}".format(self.issue_key)
        file = "test_history.csv"
        history_file = path_builder("TEST", file)
        PROJECT.change_log(folder="TEST", file=file, jql=jql)
        self.assertTrue(
            os.path.isfile(history_file),
            "Unable to detect CSV file for history extraction",
        )

    def test_delete_attachment(self):
        """Test for attachment deletion"""
        from jiraone import delete_attachments

        issue_key = self.issue_keys
        # upload a public file for the test
        file_name = "test-attachment"
        attach_file = self.attachment  # public accessible file
        fetch = LOGIN.custom_method("GET", attach_file)
        payload = {"file": (file_name, fetch.content)}
        new_headers = {
            "Accept": "application/json",
            "X-Atlassian-Token": "no-check",
        }
        LOGIN.headers = new_headers
        upload = LOGIN.post(
            endpoint.issue_attachments(issue_key, query="attachments"),
            files=payload,
        )
        self.assertTrue(upload.status_code < 300,
                        "Cannot add attachment")
        # delete file
        delete_attachments(search=issue_key)
        # check for file existence
        image_url = LOGIN.get(upload.json()[0].get("content"))
        self.assertFalse(image_url.status_code < 300,
                         "Attachment still exist")

    def test_search_user(self):
        """Test for user search"""
        from jiraone import USER

        user = USER.search_user("Prince Nyeche", "TEST")
        self.assertIsInstance(user, list, "User cannot be found")

    def test_bulk_email_change(self):
        """Test for bulk email change"""
        from jiraone import manage, file_writer
        from jiraone.module import bulk_change_email

        # change email amongst users
        manage.add_token(self.token)
        manage.get_organization()
        org = manage.org_id
        users = manage.get_organization(org_id=org, filter_by="users")
        output = manage.get_all_users(users.json(), detail=True)
        limit, count, user_list = 4, 0, []
        for item in output:
            if count >= limit:
                break
            user_list.append(item)
            count += 1
        headers = ["account_id", "current_email", "name", "target_email"]
        arrange_user_by_two, user_count = [], 0

        def rearrange_users() -> list:
            """Re-arrange the user list by two"""
            nonlocal user_count
            for user in user_list:
                d = [user.get("account_id"), user.get("email")]
                arrange_user_by_two.append(d)
                value = user_list.pop(user_count + 1)
                arrange_user_by_two[user_count].insert(
                    user_count + 2, f"Test {user_count}"
                )
                arrange_user_by_two[user_count].insert(
                    user_count + 3, value.get("email")
                )
                user_count += 1

            return arrange_user_by_two

        values = rearrange_users()
        account_id_two, left_email_two, right_email_two = (
            values[1][0],
            values[1][1],
            values[1][3],
        )
        file_writer(
            file_name="sampleTest.csv", data=headers, mark="single", mode="w+"
        )
        file_writer(
            file_name="sampleTest.csv", data=values, mark="many", mode="a+"
        )
        bulk_change_email("sampleTest.csv", self.token)
        # check for those users
        verify_user = manage.manage_profile(account_id_two)
        self.assertTrue(verify_user.status_code < 300,
                        "Verifying user failed")
        self.assertEqual(
            right_email_two,
            verify_user.json().get("account").get("email"),
            "User bulk email change failed",
        )

    def test_organization_access(self):
        """Test for organization authentication and usage"""
        from jiraone import manage
        from collections import deque

        # login to organization
        manage.add_token(self.token)
        manage.get_organization()
        org = manage.org_id
        # extract users
        users = manage.get_organization(org_id=org, filter_by="users")
        self.assertTrue(users.status_code < 300, "User extraction failed")
        output = manage.get_all_users(users.json(), detail=True)
        self.assertIsInstance(output, deque, "All user check failed")

        limit, count, user_list = 4, 0, []
        for item in output:
            if count >= limit:
                break
            user_list.append(item)
            count += 1
        payload = {"message": "On 6-month suspension"}
        # disable user
        for i in user_list:
            disable = manage.manage_user(
                i.get("account_id"), json=payload, disable=True
            )
            self.assertTrue(disable.status_code < 300,
                            "Disabling user failed")
        # enable user
        for i in user_list:
            enable = manage.manage_user(
                i.get("account_id"), json=payload, disable=False
            )
            self.assertTrue(enable.status_code < 300,
                            "Enabling user failed")

    def test_multiprocessing_history_extraction(self):
        """Test for multiprocessing on history extraction"""
        path = path_builder("TEST", "sampleAsyncFile.csv")
        LOGIN.api = True
        PROJECT.async_change_log(self.jql, folder="TEST",
                                 file="sampleAsyncFile.csv",
                                 flush=10)
        self.assertTrue(
            os.path.isfile(path), "Unable to find change log file.")

    def test_field_extraction(self):
        """Test for field extraction"""
        from jiraone import field

        name = field.get_field("Test Field")
        self.assertIsInstance(name, dict, "Field cannot be found")

    def test_http_request(self):
        """Test http request ("GET", "PUT", "DELETE" and "POST")
        to Jira resource"""
        # get
        get = LOGIN.get(endpoint.myself())
        self.assertTrue(get.status_code < 300,
                        "GET request is not working")
        # post
        LOGIN.api = False
        post = LOGIN.post(
            endpoint.issues(),
            payload=self.payload,
        )
        self.assertTrue(post.status_code < 300,
                        "POST request is not working")
        if post.status_code < 300:
            issue_key = post.json().get("key")
            # put
            put = LOGIN.put(
                endpoint.issues(issue_key),
                payload={"fields": {"priority": {"name": "Highest"}}},
            )
            self.assertTrue(put.status_code < 300,
                            "PUT request is not working")
            # delete
            delete = LOGIN.delete(endpoint.issues(issue_key))
            self.assertTrue(
                delete.status_code < 300, "DELETE request is not working"
            )

    def tearDown(self):
        """Closes the test operations"""


if __name__ == "__main__":
    unittest.main(verbosity=2)
