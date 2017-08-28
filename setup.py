from setuptools import setup

setup(
    name='toggl-jira-sync',
    description='Sync Toggl with JIRA',
    version='0.0.1',
    author='Quinn Weber',
    maintainer='Quinn Weber',
    maintainer_email='quinn@quinnweber.com',
    install_requires=(
        'requests',
        'python-dateutil',
        'jira',
    ),
)
