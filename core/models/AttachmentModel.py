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

"""Module with the :class:`AttachmentModel` model class."""

from __future__ import annotations

import logging
import os
from hashlib import md5
from typing import TYPE_CHECKING, Any, Final, override

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from core.mixins.FavoriteMixin import FavoriteMixin
from core.mixins.HasDownloadMixin import HasDownloadMixin
from core.mixins.HasThumbnailMixin import HasThumbnailMixin
from core.mixins.URLMixin import URLMixin
from Emailkasten.utils.workarounds import get_config

from ..utils.fileManagment import clean_filename, saveStore
from .StorageModel import StorageModel


if TYPE_CHECKING:
    from email.message import Message
    from io import BufferedWriter

    from .EMailModel import EMailModel


logger = logging.getLogger(__name__)


class AttachmentModel(
    HasDownloadMixin, HasThumbnailMixin, URLMixin, FavoriteMixin, models.Model
):
    """Database model for an attachment file in a mail."""

    file_name = models.CharField(max_length=255)
    """The filename of the attachment."""

    file_path = models.FilePathField(
        path=settings.STORAGE_PATH, max_length=511, recursive=True, null=True
    )
    """The path where the attachment is stored. Unique together with :attr:`email`.
    Can be null if the attachment has not been saved (null does not collide with the unique constraint.).
    Must contain :attr:`constance.get_config('STORAGE_PATH')`.
    When this entry is deleted, the file will be removed by :func:`core.signals.delete_AttachmentModel.post_delete_attachment`."""

    content_disposition = models.CharField(blank=True, default="", max_length=255)
    """The disposition of the file. Typically 'attachment', 'inline' or ''."""

    content_type = models.CharField(max_length=255, default="")
    """The type of the file."""

    datasize = models.PositiveIntegerField()
    """The filesize of the attachment."""

    is_favorite = models.BooleanField(default=False)
    """Flags favorite attachments. False by default."""

    email: models.ForeignKey[EMailModel] = models.ForeignKey(
        "EMailModel", related_name="attachments", on_delete=models.CASCADE
    )
    """The mail that the attachment was found in.  Deletion of that `email` deletes this attachment."""

    created = models.DateTimeField(auto_now_add=True)
    """The datetime this entry was created. Is set automatically."""

    updated = models.DateTimeField(auto_now=True)
    """The datetime this entry was last updated. Is set automatically."""

    BASENAME = "attachment"

    DELETE_NOTICE = _("This will only delete this attachment, not the email.")

    class Meta:
        """Metadata class for the model."""

        db_table = "attachments"
        """The name of the database table for the attachments."""

        constraints: Final[list[models.BaseConstraint]] = [
            models.UniqueConstraint(
                fields=["file_path", "email"],
                name="attachment_unique_together_file_path_email",
            )
        ]
        """:attr:`file_path` and :attr:`email` in combination are unique."""

    @override
    def __str__(self) -> str:
        """Returns a string representation of the model data.

        Returns:
            The string representation of the attachment, using :attr:`file_name` and :attr:`email`.
        """
        return _("Attachment %(file_name)s from %(email)s") % {
            "file_name": self.file_name,
            "email": self.email,
        }

    @override
    def save(self, *args: Any, **kwargs: Any) -> None:
        """Extended :django::func:`django.models.Model.save` method.

        Cleans the filename.
        Saves the data to storage if configured.
        """
        self.file_name = clean_filename(self.file_name)
        attachment_payload = kwargs.pop("attachment_payload", None)
        super().save(*args, **kwargs)
        if attachment_payload is not None and self.email.mailbox.save_attachments:
            self.save_to_storage(attachment_payload)

    @override
    def delete(self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        """Extended :django::func:`django.models.Model.delete` method.

        Deletes :attr:`file_path` file on deletion.
        """
        delete_return = super().delete(*args, **kwargs)

        if self.file_path:
            logger.debug("Removing %s from storage ...", self)
            try:
                os.remove(self.file_path)
                logger.debug(
                    "Successfully removed the attachment file from storage.",
                    exc_info=True,
                )
            except Exception:
                logger.exception("An exception occured removing %s!", self.file_path)

        return delete_return

    def save_to_storage(self, attachment_payload: bytes) -> None:
        """Saves the attachment file to the storage.

        If the file already exists, does not overwrite.
        If an error occurs, removes the incomplete file.

        Note:
            Uses :func:`core.utils.fileManagment.saveStore` to wrap the storing process.

        Args:
            attachmentData: The data of the attachment to be saved.
        """
        if self.file_path:
            logger.debug("%s is already stored.", self)
            return

        @saveStore
        def writeAttachment(file: BufferedWriter, attachmentPayload: bytes) -> None:
            file.write(attachmentPayload)

        logger.debug("Storing %s ...", self)

        dirPath = StorageModel.getSubdirectory(self.email.message_id)
        preliminary_file_path = os.path.join(dirPath, self.file_name)
        file_path = writeAttachment(preliminary_file_path, attachment_payload)
        if file_path:
            self.file_path = file_path
            self.save(update_fields=["file_path"])
            logger.debug("Successfully stored attachment.")
        else:
            logger.error("Failed to store %s!", self)

    @classmethod
    def createFromEmailMessage(
        cls, email_message: Message[str, str], email: EMailModel
    ) -> list[AttachmentModel]:
        if email.pk is None:
            raise ValueError("Email is not in db!")
        SAVE_MAINTYPES = get_config("SAVE_CONTENT_TYPE_PREFIXES")
        IGNORE_SUBTYPES = get_config("DONT_SAVE_CONTENT_TYPE_SUFFIXES")
        new_attachments = []
        for part in email_message.walk():
            if part.is_multipart():
                # for safe get_payload
                continue
            content_disposition = part.get_content_disposition()
            content_type = part.get_content_type()
            if content_disposition or (
                any(content_type.startswith(maintype) for maintype in SAVE_MAINTYPES)
                and not any(
                    content_type.endswith(subtype) for subtype in IGNORE_SUBTYPES
                )
            ):
                part_payload = part.get_payload(decode=True)
                new_attachment = cls(
                    file_name=(
                        part.get_filename()
                        or md5(  # noqa: S324  # no safe hash required here
                            part_payload
                        ).hexdigest()
                        + f".{content_type.rsplit("/", maxsplit=1)[-1]}"
                    ),
                    content_disposition=content_disposition or "",
                    content_type=content_type,
                    datasize=len(part_payload),
                    email=email,
                )
                new_attachment.save(attachment_payload=part_payload)
                new_attachments.append(new_attachment)
        return new_attachments

    @override
    @property
    def has_download(self) -> bool:
        return self.file_path is not None

    @override
    @property
    def has_thumbnail(self) -> bool:
        return self.content_type.startswith("image")

    @override
    def get_absolute_thumbnail_url(self) -> str:
        """Returns the url of the thumbail download api endpoint."""
        return reverse(f"api:v1:{self.BASENAME}-download", kwargs={"pk": self.pk})
