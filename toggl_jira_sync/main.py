import argparse
from collections import defaultdict
from datetime import datetime, timedelta
import logging
import logging.config
import operator

from jira.exceptions import JIRAError

from toggl_jira_sync.jira import (
    connect_to_jira,
    get_jira_worklogs,
    get_ticket_id_history,
    delete_worklog,
    add_worklog,
)
from toggl_jira_sync.load_config import get_config
from toggl_jira_sync.toggl import get_toggl_time_entries


logger = logging.getLogger(__name__)


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


def _get_toggl_time_entries_for_issue(config, jira_issue_id, jira_client):
    return [
        entry
        for _jira_issue_id in get_ticket_id_history(jira_client, jira_issue_id)
        for entry in get_toggl_time_entries(
            config,
            {'description': _jira_issue_id.lower()}
        )
    ]


def _delete_existing_sync_worklogs(
    config,
    jira_worklogs,
    jira_client,
    dry_run,
):
    remaining_worklogs = []

    for worklog in jira_worklogs:
        if worklog.user == config.jira_username:
            if not dry_run:
                delete_worklog(jira_client, worklog)
        else:
            remaining_worklogs.append(worklog)

    return remaining_worklogs


def _sync_toggl_with_jira(config, jira_issue_id, jira_client, dry_run=False):
    try:
        jira_worklogs = get_jira_worklogs(jira_client, jira_issue_id)
    except JIRAError:
        logger.info('jira_issue_id {} does not exist in JIRA'.format(jira_issue_id))

        return False

    toggl_entries = _get_toggl_time_entries_for_issue(
        config,
        jira_issue_id,
        jira_client,
    )

    toggl_total = sum([entry.seconds for entry in toggl_entries])
    jira_total = sum([worklog.seconds for worklog in jira_worklogs])

    if abs(toggl_total - jira_total) < 60:
        logger.info('already_synced, {}'.format(jira_issue_id))

        return True

    remaining_worklogs = _delete_existing_sync_worklogs(
        config,
        jira_worklogs,
        jira_client,
        dry_run,
    )

    jira_total = sum([worklog.seconds for worklog in remaining_worklogs])

    seconds = toggl_total - jira_total

    if seconds < 0:
        logger.warning('{} has more time tracked in JIRA than in Toggl'.format(
            jira_issue_id,
        ))

        return False

    comment = _get_comment(config, toggl_entries)

    if not dry_run:
        try:
            add_worklog(
                jira_client,
                jira_issue_id,
                seconds,
                comment,
            )
        except JIRAError as e:
            if 'non-editable' in e.text:
                logger.info('jira_issue_id {}: {}'.format(
                    jira_issue_id,
                    e.text,
                ))
            else:
                logger.warning(e.text)

            return False

    return True


def main(lookback_days, dry_run):
    config = get_config()

    jira_client = connect_to_jira(config)

    for jira_issue_id in _get_jira_issue_ids_to_sync(
        config,
        lookback_days,
    ):
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
