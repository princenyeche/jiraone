import os
import json
import unittest
from jiraone import LOGIN, endpoint


user = os.environ.get("JIRAONEUSERNAME") or "email"
password = os.environ.get("JIRAONEUSERPASS") or "token"
link = os.environ.get("JIRAONEUSERURL") or "https://yourinstance.atlassian.net"
LOGIN(user=user, password=password, url=link)


class JiraOne(unittest.TestCase):

    def test_login(self):
        load = LOGIN.get(endpoint.myself())
        self.assertTrue(load.status_code == 200, "Login Successful")

    def test_endpoints(self):
        load = LOGIN.get(endpoint.myself())
        if load.status_code != 200:
            self.assertFalse(load.status_code != 200, "Unable to Load")

    def test_data_extraction(self):
        load = LOGIN.get(endpoint.get_all_priorities())
        if load.status_code == 200:
            e = json.loads(load.content)
            self.assertIsInstance(e, (list, dict))


if __name__ == '__main__':
    unittest.main(verbosity=2)
