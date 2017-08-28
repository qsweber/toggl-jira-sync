import pytest

import toggl_jira_sync.toggl as module


@pytest.mark.parametrize(
    'string,expected',
    [
        ('abc-1: sldkfj', 'abc-1'),
        ('ABC-1: sldkfj', 'abc-1'),
        ('lakjsdf', None),
    ]
)
def test_get_jira_issue_id(string, expected):
    actual = module._get_jira_issue_id(string)

    assert actual == expected
