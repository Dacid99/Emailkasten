# ToDo

## To implement
- implement basic exchange
- maybe fetcher template superclass
- custom fetching filters with NOT, OR and custom criteria
- autostart daemons on restart
- custom additional healthchecks
- exceptions while fetching parsing and inserting for appropriate api response
- user divided storage to make file_paths unique again
- combined filter for correspondent with mention
- refine storage management error correction
- streamable logs for daemons
- registration toggling
- disable all signals in tests
- threadsafe db operations in daemons
- filtertest for choices
- move all signals into models
- user validation for serializers to avoid leakage
- enforce choices via constraint
- references header
- database statistics
- replace daemons with celery
- mailbox info from list (e.g. b'(\\Archive \\HasChildren) "/" Archiv', b'(\\HasNoChildren) "/" Archiv/2024', b'(\\Drafts \\HasNoChildren) "/" Entw&APw-rfe', b'(\\Sent \\HasNoChildren) "/" "Gesendete Objekte"', b'(\\HasNoChildren) "/" INBOX', b'(\\Trash \\HasNoChildren) "/" Papierkorb', b'(\\Junk \\HasNoChildren) "/" Spam')

### Work in progress
- tests
- documentation
- type annotations

## To test
- mailboxserializer with correspondents

## To fix
- mailbox names parsing doesnt match IMAP format

# Remember
- new migration must include setting of defaults
- logpath is misconfigured for makemigrations
- csrf is disabled for debug
