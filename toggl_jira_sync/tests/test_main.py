import pytest

import toggl_jira_sync.main as module


@pytest.mark.parametrize(
    'toggl_time_entries,jira_worklogs,delete_worklog_calls,add_worklog_calls',
    [
        (
            [
                {'user': 'foo', 'seconds': 101},
            ],
            [],
            None,
            (None, 'abc-1', 101, '--- FROM TOGGL --\n\nfoo: 1.7 minutes'),
        ),
        (
            [
                {'user': 'foo', 'seconds': 101},
            ],
            [
                {'user': 'toggl', 'seconds': 101},
            ],
            None,
            None,
        ),
    ]
)
def test_sync_toggl_with_jira(
    toggl_time_entries,
    jira_worklogs,
    delete_worklog_calls,
    add_worklog_calls,
    mocker,
):
    mocked_delete_worklog = mocker.patch.object(
        module,
        'delete_worklog',
        return_value=True,
    )

    mocked_add_worklog = mocker.patch.object(
        module,
        'add_worklog',
        return_value=True,
    )

    mocker.patch.object(
        module,
        'get_toggl_time_entries',
        return_value=[
            mocker.Mock(
                jira_issue_id='abc-1',
                user=entry['user'],
                seconds=entry['seconds'],
            )
            for entry in toggl_time_entries
        ]
    )

    mocker.patch.object(
        module,
        'get_jira_worklogs',
        return_value=[
            mocker.Mock(
                user=entry['user'],
                seconds=entry['seconds'],
            )
            for entry in jira_worklogs
        ]
    )

    module._sync_toggl_with_jira(
        mocker.Mock(
            jira_comment_prefix='--- FROM TOGGL --',
            jira_username='toggl',
        ),
        'abc-1',
        None,
    )

    if delete_worklog_calls:
        mocked_delete_worklog.assert_called_with(*delete_worklog_calls)
    else:
        mocked_delete_worklog.assert_not_called()

    if add_worklog_calls:
        mocked_add_worklog.assert_called_with(*add_worklog_calls)
    else:
        mocked_add_worklog.assert_not_called()
