import pytest

import toggl_jira_sync.main as module


@pytest.mark.parametrize(
    'toggl_time_entries,jira_worklogs,delete_worklog_called,add_worklog_calls',
    [
        (
            [
                {'user': 'foo', 'seconds': 101},
            ],
            [],
            False,
            (None, 'abc-1', 101, '--- FROM TOGGL --\n\nfoo: 1.7 minutes'),
        ),
        (
            [
                {'user': 'foo', 'seconds': 101},
            ],
            [
                {'user': 'toggl', 'seconds': 101},
            ],
            False,
            None,
        ),
        (
            [
                {'user': 'foo', 'seconds': 101},
                {'user': 'bar', 'seconds': 120},
            ],
            [],
            False,
            (None, 'abc-1', 221, '--- FROM TOGGL --\n\nbar: 2.0 minutes \nfoo: 1.7 minutes'),
        ),
        (
            [
                {'user': 'foo', 'seconds': 500},
            ],
            [
                {'user': 'toggl', 'seconds': 50},
            ],
            True,
            (None, 'abc-1', 500, '--- FROM TOGGL --\n\nfoo: 8.3 minutes'),
        ),
    ]
)
def test_sync_toggl_with_jira(
    toggl_time_entries,
    jira_worklogs,
    delete_worklog_called,
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
                jira_issue_id='abc-1',
                worklog_id=1000,
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
        dry_run=False,
    )

    if delete_worklog_called:
        assert mocked_delete_worklog.called
    else:
        mocked_delete_worklog.assert_not_called()

    if add_worklog_calls:
        mocked_add_worklog.assert_called_with(*add_worklog_calls)
    else:
        mocked_add_worklog.assert_not_called()


@pytest.mark.parametrize(
    'toggl_time_entries,jira_comment_prefix,expected',
    [
        (
            [
                {'user': 'foo', 'seconds': 100},
                {'user': 'bar', 'seconds': 120},
            ],
            '--- FROM TOGGL ---',
            '--- FROM TOGGL ---\n\nbar: 2.0 minutes \nfoo: 1.7 minutes',
        ),
        (
            [
                {'user': 'bar', 'seconds': 120},
                {'user': 'foo', 'seconds': 100},
            ],
            '--- FROM TOGGL ---',
            '--- FROM TOGGL ---\n\nbar: 2.0 minutes \nfoo: 1.7 minutes',
        ),
        (
            [
                {'user': 'bar', 'seconds': 120},
                {'user': 'foo', 'seconds': 100},
            ],
            '--- TEST ---',
            '--- TEST ---\n\nbar: 2.0 minutes \nfoo: 1.7 minutes',
        ),
    ],
)
def test_get_comment(
    toggl_time_entries,
    jira_comment_prefix,
    expected,
    mocker,
):
    actual = module._get_comment(
        mocker.Mock(jira_comment_prefix=jira_comment_prefix),
        [
            mocker.Mock(
                user=entry['user'],
                seconds=entry['seconds'],
            )
            for entry in toggl_time_entries
        ]
    )

    assert actual == expected
