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
        'dev_list',
        'jira_comment_prefix',
    ]
)


def get_config():
    return _TogglJiraSyncConfig(
        jira_username=os.environ['JTS_JIRA_USERNAME'],
        jira_password=os.environ['JTS_JIRA_PASSWORD'],
        jira_url=os.environ['JTS_JIRA_URL'],
        toggl_username=os.environ['JTS_TOGGL_USERNAME'],
        toggl_api_key=os.environ['JTS_TOGGL_API_KEY'],
        toggl_wid=os.environ['JTS_TOGGL_WID'],
        dev_list=os.environ['JTS_DEV_LIST'].split(','),
        jira_comment_prefix=os.environ['JTS_JIRA_COMMENT_PREFIX'],
    )
