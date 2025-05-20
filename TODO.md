# ToDo

## Feature ideas

- custom additional healthchecks
- implement basic exchange
- custom fetching filters with NOT, OR and custom criteria
- combined filter for correspondent with mention
- streamable logs for daemons
- extensive database statistics
- download mailboxes and accounts
- option to prohibit daemon for spambox
- tooltips
- show pdf attachments in pdfjs
- combo queries via connectors
- reprocess mail action
- mechanism to remove all correspondents and mailinglists without emails
- more daemon logging configs via model
- streaming daemon logs
- download for main logfiles
- fetching in bunches to handle large amounts of emails, fetch as generator

## To refactor

- safeimap and pop classes
- move all signals into models
- rework test:
  - disable all signals in tests
  - tests more implementation agnostic

## To test

- Storage for more cases of conflicting storage
- views customactions for response with updated modeldata
- use of cleanFilename

## To implement

- autostart daemons on restart
- user divided storage to make file_paths unique again
- replace daemons with celery, ensure threadsafe db operations in daemons
- important headers in html repr
- create daemon view
- favicon.ico for the icon
- default ssl cert and safest settings
- more attachment thumbnails
- fallback for list-id if other list entries are present
- identification of mailinglists via from
- time benchmarks in debug log

### Work in progress

- tests
- documentation
- type annotations

## To test hands-on

- complete app
- mailinglist

## To fix

- mysql may need some more care for use with timezone <https://docs.djangoproject.com/en/5.2/ref/databases/#time-zone-definitions>
- cascase doesnt trigger delete!
- optics:
  - stats table out of bounds for slim viewport
