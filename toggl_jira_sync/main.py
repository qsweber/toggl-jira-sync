import argparse
from collections import defaultdict
from datetime import datetime, timedelta
import logging
import logging.config
import operator

from jira.utils import JIRAError

from toggl_jira_sync.jira import (
    connect_to_jira,
    get_jira_worklogs,
    delete_worklog,
    add_worklog,
)
from toggl_jira_sync.load_config import get_config
from toggl_jira_sync.toggl import get_toggl_time_entries


logger = logging.getLogger('toggl_jira_sync')
logging.config.fileConfig('logging.ini')


def _get_jira_issue_ids_to_sync(config, lookback_days):
    if not lookback_days:
        lookback_days = 5

    toggl_entries = get_toggl_time_entries(
        config,
        {'since': (
            datetime.now().date() - timedelta(days=lookback_days)
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


def _sync_toggl_with_jira(config, jira_issue_id, jira_client, dry_run=False):
    toggl_entries = get_toggl_time_entries(
        config,
        {'description': jira_issue_id.lower()}
    )

    try:
        jira_worklogs = get_jira_worklogs(jira_client, jira_issue_id)
    except JIRAError:
        logger.info('jira_issue_id {} does not exist in JIRA'.format(jira_issue_id))
        return False

    toggl_total = sum([entry.seconds for entry in toggl_entries])
    jira_total = sum([entry.seconds for entry in jira_worklogs])

    if abs(toggl_total - jira_total) < 60:
        logger.info('already_synced, {}'.format(jira_issue_id))
        return True

    jira_worklogs_toggl_user = [
        jira_worklog
        for jira_worklog in jira_worklogs
        if jira_worklog.user == config.jira_username
    ]

    for worklog in jira_worklogs_toggl_user:
        logger.info('delete_worklog, {} - {}'.format(
            worklog.jira_issue_id,
            worklog.worklog_id,
        ))
        if not dry_run:
            delete_worklog(jira_client, worklog)

        jira_total -= worklog.seconds

    seconds = toggl_total - jira_total

    if seconds < 0:
        raise Exception('does not support negative times')

    comment = _get_comment(config, toggl_entries)

    logger.info('add_worklog, {} - {} - {}'.format(
        jira_issue_id,
        seconds,
        comment,
    ))
    if not dry_run:
        add_worklog(
            jira_client,
            jira_issue_id,
            seconds,
            comment,
        )

    return True


def main(lookback_days, dry_run):
    config = get_config()

    jira_client = connect_to_jira(config)

    for jira_issue_id in _get_jira_issue_ids_to_sync(config, lookback_days):
        _sync_toggl_with_jira(config, jira_issue_id, jira_client, dry_run)


def cli():
    parser = argparse.ArgumentParser(
        description='syncs Toggl with JIRA'
    )
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--lookback-days')

    cli_args = vars(parser.parse_args())

    dry_run = cli_args['dry_run']
    lookback_days = cli_args['lookback_days']
    if lookback_days:
        lookback_days = int(lookback_days)

    main(lookback_days, dry_run)
