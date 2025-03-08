# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""Module with the constant values for the :mod:`core` app."""

from __future__ import annotations

from typing import Final

from django.db.models import TextChoices


class EmailFetchingCriterionChoices(TextChoices):
    """Namespace class for all implemented mail fetching criteria constants.

    For a list of all existing IMAP criteria see https://datatracker.ietf.org/doc/html/rfc3501.html#section-6.4.4
    Note that IMAP does not support time just dates. So we are always refering to full days.
    POP does not support queries at all, so everything will be fetched.
    """

    RECENT = "RECENT", "RECENT"
    """Filter by "RECENT" flag."""

    UNSEEN = "UNSEEN", "UNSEEN"
    """Filter by "UNSEEN" flag."""

    ALL = "ALL", "ALL"
    """Filter by "ALL" flag."""

    NEW = "NEW", "NEW"
    """Filter by "NEW" flag."""

    OLD = "OLD", "OLD"
    """Filter by "OLD" flag."""

    FLAGGED = "FLAGGED", "FLAGGED"
    """Filter by "FLAGGED" flag."""

    DRAFT = "DRAFT", "DRAFT"
    """Filter by "DRAFT" flag."""

    ANSWERED = "ANSWERED", "ANSWERED"
    """Filter by "ANSWERED" flag."""

    DAILY = "DAILY", "Last DAY"
    """Filter using "SENTSINCE" for mails sent the previous day."""

    WEEKLY = "WEEKLY", "Last WEEK"
    """Filter using "SENTSINCE" for mails sent the previous week."""

    MONTHLY = "MONTHLY", "Last MONTH"
    """Filter using "SENTSINCE" for mails sent the previous 4 weeks."""

    ANNUALLY = "ANNUALLY", "Last YEAR"
    """Filter using "SENTSINCE" for mails sent the previous 52 weeks."""


class EmailProtocolChoices(TextChoices):
    """Namespace class for all implemented mail protocols constants."""

    IMAP = "IMAP", "IMAP4"
    """The IMAP4 protocol"""

    IMAP_SSL = "IMAP_SSL", "IMAP4 over SSL"
    """The IMAP4 protocol over SSL"""

    POP3 = "POP3", "POP3"
    """The POP3 protocol"""

    POP3_SSL = "POP3_SSL", "POP3 over SSL"
    """The POP3 protocol over SSL"""

    # EXCHANGE = "EXCHANGE", "Microsoft Exchange"
    """Microsofts Exchange protocol"""


class HeaderFields:
    """Namespace class with all header fields that have their own column in the emails table.

    For existing header fields see https://www.iana.org/assignments/message-headers/message-headers.xhtml.
    """

    MESSAGE_ID: Final[str] = "Message-ID"
    IN_REPLY_TO: Final[str] = "In-Reply-To"
    DATE: Final[str] = "Date"
    SUBJECT: Final[str] = "Subject"
    X_SPAM: Final[str] = "X-Spam-Flag"

    class MailingList:
        """Headers that are included in the mailinglists table."""

        ID: Final[str] = "List-Id"
        OWNER: Final[str] = "List-Owner"
        SUBSCRIBE: Final[str] = "List-Subscribe"
        UNSUBSCRIBE: Final[str] = "List-Unsubscribe"
        POST: Final[str] = "List-Post"
        HELP: Final[str] = "List-Help"
        ARCHIVE: Final[str] = "List-Archive"

    class Correspondents(TextChoices):
        """Headers that are treated as correspondents.

        This class holds the choices for `core.models.EMailCorrespondentsModel.mention`.
        """

        FROM = "From", "From"
        TO = "To", "To"
        CC = "Cc", "CC"
        BCC = "Bcc", "BCC"
        SENDER = "Sender", "Sender"
        REPLY_TO = "Reply-To", "Reply-To"
        RESENT_FROM = "Resent-From", "Resent-From"
        RESENT_TO = "Resent-To", "Resent-To"
        RESENT_CC = "Resent-Cc", "Resent-Cc"
        RESENT_BCC = "Resent-Bcc", "Resent-Bcc"
        RESENT_SENDER = "Resent-Sender", "Resent-Sender"
        RESENT_REPLY_TO = "Resent-Reply-To", "Resent-Reply-To"
        ENVELOPE_TO = (
            "Envelope-To",
            "Envelope-To",
        )
        DELIVERED_TO = "Delivered-To", "Delivered-To"
        RETURN_PATH = "Return-Path", "Return-Path"
        RETURN_RECEIPT_TO = "Return-Receipt-To", "Return-Receipt-To"
        DISPOSITION_NOTIFICATION_TO = (
            "Disposition-Notification-To",
            "Disposition-Notification-To",
        )
