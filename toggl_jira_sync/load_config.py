import os
from collections import namedtuple


_TogglJiraSyncConfig = namedtuple(
    '_TogglJiraSyncConfig',
    [
        'jira_username',
        'jira_password',
        'jira_url',
        'toggl_username',
        'toggl_api_key',
        'toggl_wid',
        'include_users_list',
        'exclude_users_list',
        'jira_comment_prefix',
    ]
)


def _get_list_from_string(string, seperator=','):
    return [
        item.strip()
        for item in string.split(seperator)
    ]


def get_config():
    return _TogglJiraSyncConfig(
        jira_username=os.environ['JTS_JIRA_USERNAME'],
        jira_password=os.environ['JTS_JIRA_PASSWORD'],
        jira_url=os.environ['JTS_JIRA_URL'],
        toggl_username=os.environ['JTS_TOGGL_USERNAME'],
        toggl_api_key=os.environ['JTS_TOGGL_API_KEY'],
        toggl_wid=os.environ['JTS_TOGGL_WID'],
        include_users_list=_get_list_from_string(os.environ['JTS_INCLUDE_USERS']),
        exclude_users_list=_get_list_from_string(os.environ['JTS_EXCLUDE_USERS']),
        jira_comment_prefix=os.environ['JTS_JIRA_COMMENT_PREFIX'],
    )
