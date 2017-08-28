from collections import defaultdict
from datetime import datetime, timedelta
import logging
import operator

from toggl_jira_sync.jira import (
    connect_to_jira,
    get_jira_worklogs,
    delete_worklog,
    add_worklog,
)
from toggl_jira_sync.load_config import get_config
from toggl_jira_sync.toggl import get_toggl_time_entries


logger = logging.getLogger(__name__)


def _get_jira_issue_ids_to_sync(config):
    toggl_entries = get_toggl_time_entries(
        config,
        {'since': (
            datetime.now().date() - timedelta(days=5)
        ).strftime('%Y-%m-%d')}
    )

    return set([
        entry.jira_issue_id
        for entry in toggl_entries
        if entry.jira_issue_id
    ])


def _get_comment(config, toggl_entries):
    seconds_by_dev = defaultdict(int)
    for entry in toggl_entries:
        seconds_by_dev[entry.user] += float(entry.seconds)

    seconds_by_dev = sorted(
        seconds_by_dev.items(),
        reverse=True,
        key=operator.itemgetter(1),
    )

    return config.jira_comment_prefix + '\n\n' + ' minutes \n'.join([
        '{}: {}'.format(user, round(float(seconds) / 60, 1))
        for user, seconds in seconds_by_dev
    ]) + ' minutes'


def _sync_toggl_with_jira(config, jira_issue_id, jira_client):
    toggl_entries = get_toggl_time_entries(
        config,
        {'description': jira_issue_id.lower()}
    )

    jira_worklogs = get_jira_worklogs(jira_client, jira_issue_id)

    toggl_total = sum([entry.seconds for entry in toggl_entries])
    jira_total = sum([entry.seconds for entry in jira_worklogs])

    if abs(toggl_total - jira_total) < 60:
        return True

    jira_worklogs_toggl_user = [
        jira_worklog
        for jira_worklog in jira_worklogs
        if jira_worklog.user == config.jira_username
    ]

    for worklog in jira_worklogs_toggl_user:
        logger.info('delete_worklog', extra=dict(
            jira_issue_id=worklog.jira_issue_id,
            worklog_id=worklog.worklog_id,
        ))
        delete_worklog(jira_client, worklog)
        jira_total -= worklog.seconds

    seconds = toggl_total - jira_total

    if seconds < 0:
        raise Exception('does not support negative times')

    comment = _get_comment(config, toggl_entries)

    logger.info('add_worklog', extra=dict(
        jira_issue_id=jira_issue_id,
        seconds=seconds,
    ))
    add_worklog(
        jira_client,
        jira_issue_id,
        seconds,
        comment,
    )

    return True


def main():
    config = get_config()

    jira_client = connect_to_jira(config)

    for jira_issue_id in _get_jira_issue_ids_to_sync(config):
        _sync_toggl_with_jira(config, jira_issue_id, jira_client)
