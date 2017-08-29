from distutils.core import setup

setup(
    name='toggl_jira_sync',
    packages=['toggl_jira_sync'],
    description='Sync Toggl with JIRA',
    version='0.0.2',
    author='Quinn Weber',
    maintainer='Quinn Weber',
    maintainer_email='quinn@quinnweber.com',
    url='https://github.com/qsweber/toggl-jira-sync',
    download_url='https://github.com/qsweber/toggl-jira-sync/archive/v0.0.2.zip',
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
