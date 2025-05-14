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

Global variables:
    logger (:class:`logging.Logger`): The logger for this module.
"""

from __future__ import annotations

import email
import email.header
import email.utils
import logging
from base64 import b64encode
from email import policy
from typing import TYPE_CHECKING

import imap_tools.imap_utf7
from django.utils import timezone
from html_sanitizer.django import get_sanitizer

from Emailkasten.utils.workarounds import get_config


if TYPE_CHECKING:
    import datetime
    from email.header import Header
    from email.message import Message

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
        decodedString += (
            fragment.decode(charset if charset else "utf-8", errors="replace")
            if isinstance(fragment, bytes)
            else fragment
        )

    return decodedString


def getHeader(
    emailMessage: Message[str, str],
    headerName: str,
    joiningString: str = ", ",
) -> str | None:
    """Shorthand to safely get a header from a :class:`email.message.EmailMessage`.

    Todo:
        emailMessage arg should become EmailMessage type after mypy 1.16.0
    Args:
        emailMessage: The message to get the header from.
        headerName: The name of the header field.
        joiningString: The string to join multiple headers with. Default to ', ' which is safe for CharFields.

    Returns:
        The decoded header field as a string if found
        else "".
    """
    encoded_header = emailMessage.get_all(headerName)
    if not encoded_header:
        return ""
    return joiningString.join([decodeHeader(header) for header in encoded_header])


def parseDatetimeHeader(dateHeader: str | None) -> datetime.datetime:
    """Parses the date header into a datetime object.

    If an error occurs uses the current time as fallback.

    Note:
        Uses :func:`email.utils.parsedate_to_datetime`
        and :func:`django.utils.timezone.now`.

    Args:
        dateHeader: The datetime header to parse.

    Returns:
        The datetime version of the header.
        The current time in case of an invalid date header.
    """
    if not dateHeader:
        logger.warning(
            "No Date header found in mail, resorting to current time!",
        )
        return timezone.now()
    try:
        parsedDatetime = email.utils.parsedate_to_datetime(dateHeader)
    except ValueError:
        logger.warning(
            "No parseable Date header found in mail, resorting to current time!",
            exc_info=True,
        )
        return timezone.now()
    return parsedDatetime


def get_bodytexts(email_message: Message[str, str]) -> dict[str, str]:
    """Parses the various bodytexts from a :class:`email.message.Message`.

    Args:
        email_message: The message to parse the bodytexts from.

    Returns:
        A dict containing the bodytexts with their contenttypes as keys.
    """
    bodytexts = {}
    for part in email_message.walk():
        content_maintype = part.get_content_maintype()
        content_subtype = part.get_content_subtype()
        if content_maintype == "text" and not part.get_content_disposition():
            bodytexts[content_subtype] = part.get_content()
    return bodytexts


def parseMailboxName(mailboxBytes: bytes) -> str:
    """Parses the mailbox name as received by the `fetchMailboxes` method in :mod:`core.utils.fetchers`.

    Note:
        Uses :func:`imap_tools.imap_utf7.utf7_decode` to decode IMAPs modified utf7 encoding.
        The result must not be changed afterwards, otherwise opening the mailbox via this name is not possible!
    Args:
        mailboxBytes: The mailbox name in bytes as received from the mail server.

    Returns:
        The serverside name of the mailbox
    """
    return (
        imap_tools.imap_utf7.utf7_decode(mailboxBytes)
        .rsplit('"/"', maxsplit=1)[-1]
        .strip()
    )


def eml2html(emailBytes: bytes) -> str:
    """Creates a html presentation of an email.

    Args:
        emailBytes: The data of the mail to be converted.

    Todo:
        ignoreplaintext mechanism may ignore too broadly

    Returns:
        The html representation of the email.
    """
    emailMessage = email.message_from_bytes(emailBytes, policy=policy.default)  # type: ignore[arg-type]  # email stubs are not up-to-date for EmailMessage, will be fixed by mypy 1.16.0: https://github.com/python/typeshed/issues/13593
    ignorePlainText = False

    htmlWrapper = get_config("HTML_WRAPPER")
    html = ""
    cidContent: dict[str, Message[str, str]] = {}
    attachmentsFooter = ""
    for part in emailMessage.walk():
        if part.get_content_subtype() == "alternative":
            ignorePlainText = True
            continue
        content_maintype = part.get_content_maintype()
        content_subtype = part.get_content_subtype()
        content_disposition = part.get_content_disposition()
        # The order of the conditions is crucial
        if content_maintype == "text":
            if content_subtype == "html":
                charset = part.get_content_charset("utf-8")
                payload = part.get_payload(decode=True)
                if isinstance(payload, bytes):
                    html += payload.decode(charset, errors="replace")
                else:
                    logger.debug(
                        "UNEXPECTED: %s/%s part payload was of type %s.",
                        content_maintype,
                        content_subtype,
                        type(payload),
                    )
            elif not ignorePlainText:
                charset = part.get_content_charset("utf-8")
                payload = part.get_payload(decode=True)
                if isinstance(payload, bytes):
                    text = payload.decode(charset, errors="replace")
                    html += htmlWrapper % text
                else:
                    logger.debug(
                        "UNEXPECTED: %s/%s part payload was of type %s.",
                        content_maintype,
                        content_subtype,
                        type(payload),
                    )
        elif content_maintype == "image":
            if cid := part.get("Content-ID", None):
                cidContent[cid.strip("<>")] = part

        elif content_disposition == "inline":
            if cid := part.get("Content-ID", None):
                cidContent[cid.strip("<>")] = part
            else:
                fileName = (
                    part.get_filename() or f"{hash(part)}.{part.get_content_subtype()}"
                )
                attachmentsFooter += "<li>" + fileName + "</li>"

        elif content_disposition == "attachment":
            fileName = (
                part.get_filename() or f"{hash(part)}.{part.get_content_subtype()}"
            )
            attachmentsFooter += "<li>" + fileName + "</li>"

    for cid, part in cidContent.items():
        content_type = part.get_content_type()
        partBytes = part.get_payload(decode=True)
        if isinstance(partBytes, bytes):
            base64part = b64encode(partBytes).decode("utf-8")
            html = html.replace(
                f'src="cid:{cid}"', f'src="data:{content_type};base64,{base64part}"'
            )
        else:
            logger.debug(
                "UNEXPECTED: %s part payload was of type %s.",
                content_type,
                type(partBytes),
            )
    if attachmentsFooter:
        html = html.replace(
            "</html>",
            f"<p><hr><p><b>Attached Files:</b><p><ul>{attachmentsFooter}</ul></html>",
        )
    return get_sanitizer().sanitize(html)  # type: ignore[no-any-return]  # always returns a str, mypy cant read html_sanitizer


def is_X_Spam(x_spam_header: str | None) -> bool:
    """Evaluates a x_spam header spam marker.

    Args:
        x_spam_header: The X-Spam-Flag header to evaluate.

    Returns:
        Whether the header marks its mail as spam.
    """
    return "YES" in str(x_spam_header)
