# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os

class MailFetchingCriteria:
    """Namespace class for all implemented mail fetching criteria constants.
    For a list of all existing IMAP criteria see https://datatracker.ietf.org/doc/html/rfc3501.html#section-6.4.4
    Note that IMAP does not support time just dates. So we are always refering to full days.
    POP does not support queries at all, so everything will be fetched."""

    RECENT: str = "RECENT"
    """Filter: str by "RECENT" flag."""

    UNSEEN: str = "UNSEEN"
    """Filter by "UNSEEN" flag."""

    ALL: str = "ALL"
    """Filter by "ALL" flag."""

    NEW: str = "NEW"
    """Filter by "NEW" flag."""

    OLD: str = "OLD"
    """Filter by "OLD" flag."""

    FLAGGED: str = "FLAGGED"
    """Filter by "FLAGGED" flag."""

    DRAFT: str = "DRAFT"
    """Filter by "DRAFT" flag."""

    ANSWERED: str = "ANSWERED"
    """Filter by "ANSWERED" flag."""

    DAILY: str = "DAILY"
    """Filter using "SENTSINCE" for mails sent the previous day or later."""

    WEEKLY: str = "WEEKLY"
    """Filter using "SENTSINCE" for mails sent the previous week (counting back from now) or later."""

    MONTHLY: str = "MONTHLY"
    """Filter using "SENTSINCE" for mails sent the previous 4 weeks (counting back from now) or later."""

    ANNUALLY: str = "ANNUALLY"
    """Filter using "SENTSINCE" for mails sent the previous 52 weeks (counting back from now) or later."""


    def __iter__(self):
        """Method to allow easier referencing of the members by listing."""
        return iter((attr, value) for attr, value in self.__class__.__dict__.items() if not attr.startswith("__"))

    def __getitem__(self, key):
        return getattr(self, key)



class MailFetchingProtocols:
    """Namespace class for all implemented mail protocols constants."""

    IMAP: str = "IMAP"
    """The IMAP4 protocol."""

    IMAP_SSL: str = "IMAP_SSL"
    """The IMAP4 protocol over SSL."""

    POP3: str = "POP3"
    """The POP3 protocol."""

    POP3_SSL: str = "POP3_SSL"
    """The POP3 protocol over SSL."""

    EXCHANGE: str = "EXCHANGE"
    """Microsofts Exchange protocol."""



class TestStatusCodes:
    """Namespace class for all status codes for the tests of mailaccounts and mailboxes."""

    OK: int = 0
    """Everything worked fine"""

    ABORTED: int = 1
    """The operation was aborted, try again."""

    BAD_RESPONSE: int = 2
    """The server did not return status OK."""

    ERROR: int = 3
    """There was an IMAP error, the account is unhealthy."""

    UNEXPECTED_ERROR: int = 4
    """An unexpected error occured, try again and check the logs."""

    INFOS: list[str] = [ "Everything worked as expected." ,
        "The operation was aborted, please try again." ,
        "The server returned a bad status, the unhealthy flag set." ,
        "There was an error, the unhealthy flag set." ,
        "An unexpected error occured, please try again and check the logs." ]



class EMailArchiverDaemonConfiguration:
    """Namespace class for all configurations constants for the :class:`Emailkasten.EMailArchiverDaemon` instances."""

    CYCLE_PERIOD_DEFAULT: int = 60
    """The default cycle period of the daemons in seconds."""

    RESTART_TIME: int = 10
    """The default restart time for the daemons in case of a crash in seconds."""



class StorageConfiguration:
    """Namespace class for all configurations constants for the :class:`Emailkasten.Models.StorageModel`."""

    MAX_SUBDIRS_PER_DIR: int = 1000
    """The maximum numbers of subdirectories in one storage unit. Must not exceed 64000 for ext4 filesystem! """

    STORAGE_PATH: str = "/mnt/archive"
    """The path to the storage for the saved data. Must match the path in the docker-compose.yml to ensure data safety."""

    PRERENDER_IMAGETYPE: str = 'jpg'
    """The image format for the prerendered eml files."""



class LoggerConfiguration:
    """Namespace class for all configurations constants for the application loggers."""

    LOG_DIRECTORY_PATH: str = "" #/var/log
    """The path to directory with the logs.  Must match the path in the docker-compose.yml to store the logs outside the container."""

    APP_LOGFILE_NAME: str = "Emailkasten.log"
    """The name of the Emailkasten logfile."""

    DJANGO_LOGFILE_NAME: str = "django.log"
    """The naeme of the django logfile."""

    APP_LOG_LEVEL: str = os.environ.get('APP_LOG_LEVEL', 'INFO')
    """The loglevel to the Emailkasten logfile. Is being set from an environment variable of the same name."""

    DJANGO_LOG_LEVEL: str = os.environ.get('DJANGO_LOG_LEVEL', 'INFO')
    """The loglevel to the django logfile. Is being set from an environment variable of the same name."""

    ROOT_LOG_LEVEL: str = os.environ.get('ROOT_LOG_LEVEL', 'INFO')
    """The loglevel to the root console logger. Is being set from an environment variable of the same name."""

    LOGFILE_MAXSIZE: int = 10 * 1024 * 1024 # 10 MiB
    """The maximum file size of a logfile."""

    LOGFILE_BACKUP_NUMBER: int = 3
    """The maximum number of backup logfiles to keep."""

    LOG_FORMAT: str = '{asctime} {levelname} - {name}.{funcName}: {message}'
    """The format of the log messages for all loggers."""



class ParsingConfiguration:
    """Namespace class for all configurations constants for the parsing of mails."""

    CHARSET_DEFAULT: str = 'utf-8'
    """The default charset used for parsing of text."""

    STRIP_TEXTS: bool = True
    """Whether or not to strip whitespace from textfields like bodytext and subject."""

    THROW_OUT_SPAM: bool = True
    """Whether or not to ignore emails that have a spam flag."""

    APPLICATION_TYPES: list[str] = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    """A list of application types to parse as attachments."""

    DATE_DEFAULT: str = "1971-01-01 00:00:00"
    """The fallback date to use if none is found in a mail."""

    DATE_FORMAT: str = '%Y-%m-%d %H:%M:%S'
    """The mail datetime format as specified in RFC5322. Must match the pattern of :attr:`DATE_DEFAULT`."""



class ProcessingConfiguration:
    """Namespace class for all configurations constants for the processing, especially the prerendering, of mails."""

    DUMP_DIRECTORY: str = '/tmp/images'
    """The directory path where temporary images of the prerendering process will be placed."""

    HTML_FORMAT: str = """
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    font-size: 14px;
                    white-space: pre-wrap;
                }}
            </style>
        </head>
        <body>
            <pre>%s</pre>
        </body>
        </html>
        """
    """The html template to wrap around plain text before prerendering."""



class FetchingConfiguration:
    """Namespace class for all configurations constants for the fetching of mails."""

    SAVE_TO_EML_DEFAULT: bool = True
    """The default setting whether to store mails as eml. Initially set to True."""

    SAVE_ATTACHMENTS_DEFAULT: bool = True
    """The default setting whether to store attachments. Initially set to True."""

    SAVE_IMAGES_DEFAULT: bool = True
    """The default setting whether to store images. Initially set to True."""



class DatabaseConfiguration:
    """Namespace class for all configurations constants for the database."""

    NAME: str = os.environ.get("DB_NAME", "emailkasten")
    """The name of the database on the mariadb server. Can be set from docker-compose.yml."""

    USER: str = os.environ.get("DB_USER", "user")
    """The name of the database user. Can be set from docker-compose.yml."""

    PASSWORD: str = os.environ.get("DB_PASSWORD", "passwd")
    """The password of the database user. Can be set from docker-compose.yml."""

    RECONNECT_RETRIES: int = 10
    """The number of reconnect attempt in case of database disconnect."""

    RECONNECT_DELAY: int = 30
    """The delay between reconnect attempt in case of database disconnect."""



class ParsedMailKeys:
    #Keys to the dict
    DATA: str = "Raw"
    FULL_MESSAGE: str = "Full"
    SIZE: str = "Size"
    EML_FILE_PATH: str = "EmlFilePath"
    PRERENDER_FILE_PATH: str = "PrerenderFilePath"
    ATTACHMENTS: str = "Attachments"
    IMAGES: str = "Images"
    MAILINGLIST: str = "Mailinglist"
    BODYTEXT: str = "Bodytext"

    class Header:
        """For existing header fields see https://www.iana.org/assignments/message-headers/message-headers.xhtml."""
        MESSAGE_ID: str = "Message-ID"
        IN_REPLY_TO: str = "In-Reply-To"

        DATE: str = "Date"
        SUBJECT: str = "Subject"
        COMMENTS: str = "Comments"
        KEYWORDS: str = "Keywords"

        RECEIVED: str = "Received"
        IMPORTANCE: str = "Importance"
        PRIORITY: str = "Priority"
        PRECEDENCE: str = "Precedence"

        LANGUAGE: str = "Language"
        CONTENT_LANGUAGE: str = "Content-Language"
        CONTENT_LOCATION: str = "Content-Location"
        CONTENT_TYPE: str = "Content-Type"

        USER_AGENT: str = "User-Agent"
        AUTO_SUBMITTED: str = "Auto-Submitted"
        ARCHIVED_AT: str = "Archived-At"

        X_PRIORITY: str = "X-Priority"
        X_ORIGINATING_CLIENT: str = "X-Originating-Client"
        X_SPAM_FLAG: str = "X-Spam-Flag"


    class Correspondent:
        FROM: str = "From"
        TO: str = "To"
        CC: str = "Cc"
        BCC: str = "Bcc"
        SENDER: str = "Sender"
        REPLY_TO: str = "Reply-To"
        RESENT_FROM: str = "Resent-From"
        RESENT_TO: str = "Resent-To"
        RESENT_CC: str = "Resent-Cc"
        RESENT_BCC: str = "Resent-Bcc"
        RESENT_SENDER: str = "Resent-Sender"
        RESENT_REPLY_TO: str = "Resent-Reply-To"
        ENVELOPE_TO: str = "Envelope-To"
        DELIVERED_TO: str = "Delivered-To"
        RETURN_PATH: str = "Return-Path"
        RETURN_RECEIPT_TO: str = "Return-Receipt-To"
        DISPOSITION_NOTIFICATION_TO: str = "Disposition-Notification-To"

        def __iter__(self):
            return iter((attr, value) for attr, value in self.__class__.__dict__.items() if not attr.startswith("__"))

        def __getitem__(self, key):
            return getattr(self, key)


    #attachment keys
    class Attachment:
        DATA: str = "AttachmentData"
        SIZE: str = "AttachmentSize"
        FILE_NAME: str = "AttachmentFileName"
        FILE_PATH: str = "AttachmentFilePath"

    #image keys
    class Image:
        DATA: str = "ImageData"
        SIZE: str = "ImageSize"
        FILE_NAME: str = "ImageFileName"
        FILE_PATH: str = "ImageFilePath"

    #mailinglist keys
    class MailingList:
        ID: str = "List-Id"
        OWNER: str = "List-Owner"
        SUBSCRIBE: str = "List-Subscribe"
        UNSUBSCRIBE: str = "List-Unsubscribe"
        POST: str = "List-Post"
        HELP: str = "List-Help"
        ARCHIVE: str = "List-Archive"
