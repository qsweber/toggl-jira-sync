# Toggl-JIRA Sync

This package is designed to sync time tracking data from Toggl over to
JIRA. For example, if there is a Toggl time entry called
"ABC-1: working on ticket", the time spent will be added to a the ticket in
JIRA called "ABC-1".

This makes it easier to view the total time spent on tickets, which is helpful
for future work estimation.

# Overview

This package has an entry point called `run-toggl-jira-sync` which does the
following:

1. Download the last 5 days worth of Toggl data
1. Parse the ticket numbers from the Toggl data
1. Loop through each ticket and:
    1. Download full history of Toggl data for ticket
    1. Download JIRA worklogs for ticket
    1. Add/update worklogs in JIRA to sync with the total time tracked in Toggl

# Configuration

The following variables must defined:

## `JTS_JIRA_USERNAME`

Username for accessing JIRA. This should be a non-human account.

## `JTS_JIRA_PASSWORD`

Password for accessing JIRA.

## `JTS_JIRA_URL`

URL of JIRA (e.g. `https://jira.foo.org`)

## `JTS_TOGGL_USERNAME`

Username for accessing Toggl. This user should be an admin or have the ability
to read Toggl entries for the entire organization.

## `JTS_TOGGL_API_KEY`

API key of the Toggl user.

## `JTS_TOGGL_WID`

Workspace ID in Toggl. See the Toggl API docs for how to determine this value.

## `JTS_INCLUDE_USERS`

Which Toggl users should be included when posting to JIRA?

## `JTS_EXCLUDE_USERS`

Which Toggl users should be excluded when posting to JIRA? All users must
exist in either `JTS_EXCLUDE_USERS` or `JTS_INCLUDE_USERS`.

## `JTS_JIRA_COMMENT_PREFIX`

This string will be appended to the beginning of the comment in JIRA worklogs
that originate from this package. This makes it easier for users to understand
where the Worklogs are coming from.
