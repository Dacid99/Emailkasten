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

"""Module with the :class:`MailingListModel` model class."""
from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import models

from ..constants import ParsedMailKeys
from ..utils.mailParsing import _parseHeader

if TYPE_CHECKING:
    from email.message import Message


class MailingListModel(models.Model):
    """Database model for a mailinglist."""

    list_id = models.CharField(max_length=255)
    """The List-ID header of the mailinglist. Unique together with :attr:`correspondent`."""

    list_owner = models.CharField(max_length=255, null=True)
    """The List-Owner header of the mailinglist. Can be null."""

    list_subscribe = models.EmailField(max_length=255, null=True)
    """The List-Subscribe header of the mailinglist. Can be null."""

    list_unsubscribe = models.EmailField(max_length=255, null=True)
    """The List-Unsubscribe header of the mailinglist. Can be null."""

    list_post = models.CharField(max_length=255, null=True)
    """The List-Post header of the mailinglist. Can be null."""

    list_help = models.CharField(max_length=255, null=True)
    """The List-Help header of the mailinglist. Can be null."""

    list_archive = models.CharField(max_length=255, null=True)
    """The List-Archive header of the mailinglist. Can be null."""

    is_favorite = models.BooleanField(default=False)
    """Flags favorite mailingslists. False by default."""

    correspondent = models.ForeignKey(
        "CorrespondentModel", related_name="mailinglist", on_delete=models.CASCADE
    )
    """The correspondent that sends the mailinglist. Unique together with :attr:`list_id`. Deletion of that `correspondent` deletes this mailinglist."""

    created = models.DateTimeField(auto_now_add=True)
    """The datetime this entry was created. Is set automatically."""

    updated = models.DateTimeField(auto_now=True)
    """The datetime this entry was last updated. Is set automatically."""

    def __str__(self):
        return f"Mailinglist {self.list_id}"

    class Meta:
        """Metadata class for the model."""

        db_table = "mailinglists"
        """The name of the database table for the mailinglists."""

        constraints = [
            models.UniqueConstraint(
                fields=["list_id", "correspondent"],
                name="mailinglist_unique_together_list_id_correspondent",
            )
        ]
        """:attr:`list_id` and :attr:`correspondent` in combination are unique."""

    @staticmethod
    def fromMessage(emailMessage: Message) -> MailingListModel | None:
        if not (list_id := emailMessage.get(ParsedMailKeys.MailingList.ID, None)):
            return None

        new_mailinglist = MailingListModel(list_id=list_id)
        new_mailinglist.list_owner = emailMessage.get(
            ParsedMailKeys.MailingList.ID, None
        )
        new_mailinglist.list_subscribe = emailMessage.get(
            ParsedMailKeys.MailingList.SUBSCRIBE, None
        )
        new_mailinglist.list_unsubscribe = emailMessage.get(
            ParsedMailKeys.MailingList.UNSUBSCRIBE, None
        )
        new_mailinglist.list_post = emailMessage.get(
            ParsedMailKeys.MailingList.POST, None
        )
        new_mailinglist.list_help = emailMessage.get(
            ParsedMailKeys.MailingList.HELP, None
        )
        new_mailinglist.list_archive = emailMessage.get(
            ParsedMailKeys.MailingList.ARCHIVE, None
        )
        return new_mailinglist
