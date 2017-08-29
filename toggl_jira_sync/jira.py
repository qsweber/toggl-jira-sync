from jira.client import GreenHopper
from typing import NamedTuple


_JiraWorklog = NamedTuple(
    '_JiraWorklog',
    [
        ('jira_issue_id', str),
        ('worklog_id', str),
        ('user', str),
        ('seconds', float),
        ('comment', str),
    ]
)


def _get_jira_issue_id(jira_issue):
    return (
        jira_issue.key
        .encode('ascii', 'ignore')
        .decode()
        .lower()
    )


def get_ticket_id_history(jira_client, jira_issue_id):
    jira_issue = jira_client.issue(jira_issue_id, expand='changelog')

    jira_issue_id_current = _get_jira_issue_id(jira_issue)

    jira_issue_id_history = []

    for history in jira_issue.changelog.histories:
        for item in history.items:
            if item.field == 'Key':
                jira_issue_id_history.append(item.fromString.lower())

    jira_issue_id_history.append(jira_issue_id_current)

    return jira_issue_id_history


def get_jira_worklogs(jira_client, jira_issue_id):
    return [
        _JiraWorklog(
            jira_issue_id,
            worklog_id=log.id,
            user=log.author.name,
            seconds=log.timeSpentSeconds,
            comment=getattr(log, 'comment', ''),
        )
        for log in jira_client.worklogs(jira_issue_id)
    ]


def delete_worklog(jira_client, jira_worklog):
    url = jira_client._get_url('issue/{0}/worklog/{1}'.format(
        jira_worklog.jira_issue_id,
        jira_worklog.worklog_id,
    ))

    jira_client._session.delete(url)

    return True


def add_worklog(jira_client, jira_issue_id, seconds, comment):
    jira_client.add_worklog(
        issue=jira_issue_id,
        timeSpentSeconds=max(60, seconds),
        comment=comment,
    )

    return True


def connect_to_jira(config):
    '''
    @param config: _TogglJiraSyncConfig object
    @returns: object with connection to JIRA API
    '''
    return GreenHopper(
        basic_auth=(config.jira_username, config.jira_password),
        options={'server': config.jira_url},
    )
