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


"""Provides functions for parsing features from the maildata.
Functions starting with _ are helpers and are used only within the scope of this module.

Global variables:
    logger (:class:`logging.Logger`): The logger for this module.
"""

from __future__ import annotations

import datetime
import email
import email.header
import email.message
import email.utils
import logging
from typing import TYPE_CHECKING, Callable

import imap_tools.imap_utf7
from django.utils import timezone

from core.constants import ParsedMailKeys

if TYPE_CHECKING:
    from email.header import Header
    from email.message import EmailMessage

logger = logging.getLogger(__name__)


def decodeHeader(header: Header | str) -> str:
    """Decodes an email header field.

    Note:
        Uses :func:`email.header.decode_header`.

    Args:
        header: The mail header to decode.

    Returns:
        The decoded mail header.
    """
    decodedFragments = email.header.decode_header(header)
    decodedString = ""
    for fragment, charset in decodedFragments:
        if not charset:
            decodedString += (
                fragment.decode(errors="replace")
                if isinstance(fragment, bytes)
                else fragment
            )
        else:
            decodedString += (
                fragment.decode(charset, errors="replace")
                if isinstance(fragment, bytes)
                else fragment
            )

    return decodedString


def getHeader(
    emailMessage: EmailMessage,
    headerName: str,
    joiningString=", ",
    fallbackCallable: Callable[[], str] = lambda: None,
) -> str:
    """Shorthand to safely get a header from a :class:`email.message.EmailMessage`.
    Args:
        emailMessage: The message to get the header from.
        headerName: The name of the header field.
        fallbackCallable: A callable that provides a fallback if the field is not found.
            Is only executed if required. Defaults to `lambda: None`.
    Returns:
        The decoded header field as a string if found
        else the return of the :attr:`fallbackCallable`.
    """
    encoded_header = emailMessage.get_all(headerName)
    if not encoded_header:
        return fallbackCallable()
    return joiningString.join([decodeHeader(header) for header in encoded_header])


def getDatetimeHeader(mailMessage: EmailMessage) -> datetime.datetime:
    """Parses the date header of the given mailmessage.
    If an error occurs uses the current time as fallback.

    Note:
        Uses :func:`email.utils.parsedate_to_datetime`
        and :func:`django.utils.timezone.now`.

    Args:
        mailMessage: The mailmessage to get the datetime header from.

    Returns:
        The datetime header.
    """
    date = getHeader(mailMessage, ParsedMailKeys.Header.DATE)
    if not date:
        logger.warning("No Date header found in mail, resorting to current time!")
        return timezone.now()
    else:
        try:
            parsedDatetime = email.utils.parsedate_to_datetime(date)
        except ValueError:
            logger.warning(
                "No parseable Date header found in mail, resorting to current time!",
                exc_info=True,
            )
            return timezone.now()
        return parsedDatetime


def parseMailboxName(mailboxBytes: bytes) -> str:
    """Parses the mailbox name as received by the `fetchMailboxes` method in :mod:`core.utils.fetchers`.

    Note:
        Uses :func:`imap_tools.imap_utf7.utf7_decode` to decode IMAPs modified utf7 encoding.

    Args:
        mailboxBytes: The mailbox name in bytes as received from the mail server.

    Returns:
        The name of the mailbox independent of its parent folders
    """
    mailbox = imap_tools.imap_utf7.utf7_decode(mailboxBytes)
    # if "/" in mailbox:
    #     mailboxName = mailbox.split('"/"')[1].strip()
    # if mailboxName == "":
    #     mailboxName = mailbox.split('" "')[1].strip()
    return mailbox
