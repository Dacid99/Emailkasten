from project.settings import *          # pylint: disable=wildcard-import, unused-wildcard-import ; all settings need to be imported

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",  # Use SQLite in memory
        "NAME": ":memory:",
    }
}
