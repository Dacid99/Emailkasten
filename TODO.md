# ToDo

## Feature ideas

- custom fetching filters with NOT, OR and custom criteria
- combined filter for correspondent with mention
- streamable logs for daemons
- extensive database statistics
- option to prohibit daemon for spambox
- toggleable [tooltips](https://getbootstrap.com/docs/5.3/components/tooltips/)
- reprocess mail action
- mechanism to remove all correspondents without emails
- more daemon logging configs via model
- streaming daemon logs
- download for main logfiles
- fetching in bunches to handle large amounts of emails, fetch as generator
- autotest account before form submission, fetch mailboxes on submission
- [spinner](https://getbootstrap.com/docs/5.3/components/spinners/) and [progressbar](https://getbootstrap.com/docs/5.3/components/progress/) for actions
- notes field for models
- more tags
- autotagging
- saving old correspondent mailername info (via fk maybe)
- async parsing, sync saving
- auto transfer of pdfs to paperless
- fetch once by criterion instead of hardcoded ALL

## To refactor

- safeimap and pop classes
- rework test:
  - disable all signals in tests
  - tests more implementation agnostic
  - use more of the unittest api
  - replace modeltodict in form and serializer tests with payloads
- emailcorrespondent creation for better integration of mailinglist
- shorten redundant exception logging in fetchers, move parts of the messages to the exc classes
- other-scripts blocks can be replaced using super_block

## To test

- views customactions for response with updated modeldata
- storagebackend for colliding file/dir
- test celery daemons

## To implement

- ensure threadsafe db operations in daemons
- fetch only specific errors in fetchers
- favicon.ico for the icon
- time benchmarks in debug log
- batch download and delete in web
- dependency-upgrading tool for your project dependencies? (eg. dependabot, PyUp, Renovate, pip-tools, Snyx)
- coverage in test job
- daemonize celery worker
- helptexts for orientation instead of empty lists
- api creation of daemons
- mailbox specific daemon create view
- only show available fetching options in daemonform


### Work in progress

- tests
- documentation
- type annotations

## To fix

- fetching too many emails leads to browser timeout
- daemon logger setup doesnt persist
- running tests from test dir
- storage is incremented by healthcheck
- daemon api allows unavailable criteria
- task doesnt catch mailaccounterrors
- fetchers can raise valueerror but that is not caught
which can happen if the user changes the protocol of an account with existing fetchers and the criteria become unavailable (what happens if task raises?)
- optics:
  - checkboxes for boolean data instead of True and False
  - better name for daemon
- ci:
  - djlint has no files to lint
