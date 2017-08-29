from datetime import datetime, timedelta
import json
from re import search
import requests
from time import sleep

from typing import NamedTuple


TOGGL_URL = 'https://toggl.com/reports/api/v2/'


_TogglTimeEntry = NamedTuple(
    '_TogglTimeEntry',
    [
        ('jira_issue_id', str),
        ('user', str),
        ('seconds', float),
    ]
)


def get_toggl_time_entries(config, params={}):
    one_year_ago = (
        datetime.now().date() - timedelta(days=365)
    ).strftime('%Y-%m-%d')

    default_params = {
        'user_agent': config.toggl_username,
        'workspace_id': config.toggl_wid,
        'since': one_year_ago,
        'page': 1,
    }
    default_params.update(params)

    entries_total = []
    while True:
        result = requests.get(
            TOGGL_URL + 'details',
            params=default_params,
            auth=(config.toggl_api_key, "api_token"),
        )

        entries = json.loads(result.text).get('data')
        if not entries:
            break

        entries_total = entries_total + entries
        default_params['page'] += 1
        sleep(1)

    unique_users = set([entry['user'] for entry in entries_total])
    new_users = unique_users - set(config.include_users_list) - set(config.exclude_users_list)
    if new_users:
        raise Exception('add the following users to either the JTS_INCLUDE_USERS or JTS_EXCLUDE_USERS: {}'.format(
            ', '.join(new_users)
        ))

    return [
        _TogglTimeEntry(
            jira_issue_id=_get_jira_issue_id(entry['description']),
            user=entry['user'],
            seconds=entry['dur'] / float(1000),
        )
        for entry in entries_total
        if entry['user'] in config.include_users_list
    ]


def _get_jira_issue_id(string):
    issue_id_regex = r'[A-Za-z]+-\d+'

    match = search(issue_id_regex, string)
    if match:
        return match.group(0).lower()
    else:
        return None
