import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jiraone",
    version="0.7.7",
    author="Prince Nyeche",
    author_email="support@elfapp.website",
    description="A REST API Implementation to Jira Cloud APIs for creating reports and "
                "for performing other Jira queries.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://jiraone.readthedocs.io",
    license="MIT License",
    keywords="jiraone,Atlassian API,Jira API",
    packages=setuptools.find_packages(),
    install_requires=['requests'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    project_urls={"Tracker": "https://github.com/princenyeche/jiraone/issues", 
                  "Source": "https://github.com/princenyeche/jiraone"}
)
