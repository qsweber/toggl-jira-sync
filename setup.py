from setuptools import setup

setup(
    name='toggl-jira-sync',
    packages=['toggl_jira_sync'],
    description='Sync Toggl with JIRA',
    version='0.0.3',
    author='Quinn Weber',
    author_email='quinn@quinnweber.com',
    maintainer='Quinn Weber',
    maintainer_email='quinn@quinnweber.com',
    url='https://github.com/qsweber/toggl-jira-sync',
    install_requires=(
        'requests',
        'python-dateutil',
        'jira',
    ),
    entry_points={
        'console_scripts': (
            'run-toggl-jira-sync = toggl_jira_sync.main:cli',
        ),
    },
)
