import pytest

import toggl_jira_sync.load_config as module


@pytest.mark.parametrize(
    'string,expected',
    [
        ('abc,def', ['abc', 'def']),
        ('abc , def  ', ['abc', 'def']),
    ]
)
def test_get_list_from_string(string, expected):
    actual = module._get_list_from_string(string)

    assert actual == expected
