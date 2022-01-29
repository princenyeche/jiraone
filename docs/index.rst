.. image:: https://app.codacy.com/project/badge/Grade/86f1594e0ac3406aa9609c4cd7c70642
   :target: https://www.codacy.com/gh/princenyeche/jiraone/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=princenyeche/jiraone&amp;utm_campaign=Badge_Grade
   :alt: Codacy Badge

.. image:: https://pepy.tech/badge/jiraone
   :target: https://pepy.tech/project/jiraone
   :alt: Downloads

.. image:: https://badge.fury.io/py/jiraone.svg
   :target: https://badge.fury.io/py/jiraone
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/l/jiraone
   :target: https://img.shields.io/pypi/l/jiraone
   :alt: PyPI - License

.. image:: https://readthedocs.org/projects/jiraone/badge/?version=latest
   :target: https://jiraone.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status


Jira one
=================
A REST API Implementation to Jira Cloud APIs for creating reports and for performing other Jira queries.


Configurations
-------
Install using ``pip``. you have to be on python >= 3.6.x in order to utilize this script.

.. code-block:: bash

    pip install jiraone


Classes, functions and methods
-------
Jiraone comes with various classes, functions and methods. Aliases as well, are used to represent
links to classes and functions. The major ones to take note of are the ones shown on the directory link below.

For further knowledge on how to use the classes, methods or functions.Open 
the jiraone package and read the docstring on the aforementioned
methods or functions above to get further information.

If you're connecting to Jira server or datacenter, you will need to change 
the API endpoint to point to server instances. To do that, simply change
the attribute ``LOGIN.api = False`` this helps to use the endpoint ``/rest/api/latest``
which is compatible for Jira server or datacenter.

.. code-block:: python

    from jiraone import LOGIN

    data = "username", "password", "https://server.jiraserver.com"
    LOGIN.api = False
    LOGIN(*data)


The above login method applies only when you need to access a Jira server or 
datacenter type instances. The above has little or no effect on cloud 
instance and will work normally.


Directory
-------

.. toctree::
   :maxdepth: 2
   
   api
   report


API Reference
-------
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
