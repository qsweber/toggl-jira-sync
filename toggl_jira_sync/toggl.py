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

    return [
        _TogglTimeEntry(
            jira_issue_id=_jira_issue_id_for_time_entry(entry),
            user=entry['user'],
            seconds=entry['dur'] / float(1000),
        )
        for entry in entries_total
        if entry['user'] in config.dev_list
    ]


def _jira_issue_id_for_time_entry(entry):
    issue_id_regex = r'[A-Za-z]+-\d+'

    match = search(issue_id_regex, entry['description'])
    if match:
        return match.group(0).lower()
    else:
        return None
