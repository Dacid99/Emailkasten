# ToDo

## To implement

- implement basic exchange
- custom fetching filters with NOT, OR and custom criteria
- autostart daemons on restart
- custom additional healthchecks
- user divided storage to make file_paths unique again
- combined filter for correspondent with mention
- refine storage management error correction
- streamable logs for daemons
- disable all signals in tests
- threadsafe db operations in daemons
- filtertest for choices
- move all signals into models
- user validation for serializers to avoid leakage
- validating choices in serializers and models
- references header
- database statistics
- replace daemons with celery
- rework test:
  - consistent naming
  - more autouse
  - more autospec
  - unify model fixtures
  - sort args
  - AssertionErrors for injected side_effects
  - no pytest.raises(Exception)
- email correspondent on delete is cascading! Should be data preserving instead
- download mailboxes and accounts
- tooltips

### Work in progress

- tests
- documentation
- type annotations

## To test

- complete app

## To fix

# Remember

- logpath is misconfigured for makemigrations
