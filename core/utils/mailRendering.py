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

"""Provides functions to render images from .eml files."""

from __future__ import annotations

import email
import logging
from base64 import b64encode
from email import policy

from html_sanitizer.django import get_sanitizer

from Emailkasten.utils import get_config


logger = logging.getLogger(__name__)


def eml2html(emailBytes: bytes) -> str:
    """Creates a html presentation of an email.

    Args:
        emailBytes: The data of the mail to be converted.
    """
    emailMessage = email.message_from_bytes(emailBytes, policy=policy.default)
    ignorePlainText = False  # ignores too broadly!

    htmlWrapper = get_config("HTML_WRAPPER")
    html = ""
    cidContent = {}
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
                html += part.get_payload(decode=True).decode(charset, errors="replace")
            elif not ignorePlainText:
                charset = part.get_content_charset("utf-8")
                text = part.get_payload(decode=True).decode(charset, errors="replace")
                html += htmlWrapper % text
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
        partBytes = part.get_payload(decode=True)
        content_type = part.get_content_type()
        base64part = b64encode(partBytes).decode("utf-8")
        html = html.replace(
            f'src="cid:{cid}"', f'src="data:{content_type};base64,{base64part}"'
        )
    if attachmentsFooter:
        html = html.replace(
            "</html>",
            f"<p><hr><p><b>Attached Files:</b><p><ul>{attachmentsFooter}</ul></html>",
        )
    return get_sanitizer().sanitize(html)
