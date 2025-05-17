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

"""Module with the :class:`Storage` model class."""

from __future__ import annotations

import logging
import os
from typing import Any, override

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from Emailkasten.utils.workarounds import get_config

from ..utils.file_managment import clean_filename


logger = logging.getLogger(__name__)
"""The logger instance for this module."""


class Storage(models.Model):
    """A database model to keep track of and manage the sharded storage's status and structure.

    Important:
        Use the custom methods to create new instances, never use :func:`create`!
    """

    directory_number = models.PositiveIntegerField(unique=True)
    """The number of the directory tracked by this entry. Unique."""

    path = models.FilePathField(unique=True, path=settings.STORAGE_PATH)
    """The path of the tracked directory. Unique.
    Must contain :attr:`settings.STORAGE_PATH`."""

    subdirectory_count = models.PositiveSmallIntegerField(default=0)
    """The number of subdirectories in this directory. 0 by default.
    Managed to not exceed :attr:`constance.get_config('STORAGE_MAX_SUBDIRS_PER_DIR')`."""

    current = models.BooleanField(default=False)
    """Flags whether this directory is the one where new data is being stored. False by default.
    There must only be one entry where this is set to True."""

    created = models.DateTimeField(auto_now_add=True)
    """The datetime this entry was created. Is set automatically."""

    updated = models.DateTimeField(auto_now=True)
    """The datetime this entry was last updated. Is set automatically."""

    class Meta:
        """Metadata class for the model."""

        db_table = "storage"
        """The name of the database table for the storage status."""

    @override
    def __str__(self) -> str:
        """Returns a string representation of the model data.

        Returns:
            The string representation of the storage directory, using :attr:`path` and the state of the directory.
        """
        state = "Current" if self.current else "Archived"
        return _("%(state)s storage directory %(path)s") % {
            "state": state,
            "path": self.path,
        }

    @override
    def save(self, *args: Any, **kwargs: Any) -> None:
        """Extended :django::func:`django.models.Model.save` method with storage directory creation for new entries.

        Sets the :attr:`path` if it is null and creates the directory at that path if it doesnt exist.
        If the path points to a file, suffixes are added to the path until the path becomes valid.
        """
        if not self.path:
            self.path = os.path.join(settings.STORAGE_PATH, str(self.directory_number))
            while os.path.isfile(self.path):
                self.path += ".a"
            if not os.path.exists(self.path):
                logger.info("Creating new storage directory %s ...", self.path)
                os.makedirs(self.path)
                logger.info("Successfully created new storage directory.")

        super().save(*args, **kwargs)

    def increment_subdirectory_count(self) -> None:
        """Increments the :attr:`subdirectory_count` within the limits of :attr:`constance.get_config('STORAGE_MAX_SUBDIRS_PER_DIR')`.

        If the result exceeds this limit, creates a new storage directory via :func:`_add_new_directory`.
        """
        logger.debug("Incrementing subdirectory count of %s ..", self)

        self.subdirectory_count += 1
        self.save(update_fields=["subdirectory_count"])
        if self.subdirectory_count >= get_config("STORAGE_MAX_SUBDIRS_PER_DIR"):
            logger.debug(
                "Max number of subdirectories in %s reached, adding new storage ...",
                self,
            )
            self._add_new_directory()
            logger.debug("Successfully added new storage.")

        logger.debug("Successfully incremented subdirectory count.")

    def _add_new_directory(self) -> None:
        """Adds a new storage directory.

        Setting this entries :attr:`current` to `False`
        and creates a new database entry with incremented :attr:`directory_number` and :attr:`current` set to `True`.
        """
        self.current = False
        self.save(update_fields=["current"])
        Storage.objects.create(
            directory_number=self.directory_number + 1,
            current=True,
            subdirectory_count=0,
        )

    @staticmethod
    def get_subdirectory(subdirectory_name: str) -> str:
        """Static utility to acquire a path for a subdirectory in the storage.

        If that subdirectory does not exist yet,
        creates it and increments the :attr:`subdirectory_count` of the current storage directory.
        If a file exists at the projected path, adds suffixes to the path until it does no longer point to a file.

        Args:
            subdirectory_name: The name of the subdirectory to be stored.

        Returns:
            The path of the subdirectory in the storage.
        """
        storage_entry = Storage.objects.filter(current=True).first()
        if not storage_entry:
            logger.info("Creating first storage directory...")
            storage_entry = Storage.objects.create(
                directory_number=0, current=True, subdirectory_count=0
            )
            logger.info("Successfully created first storage directory.")

        clean_subdirectory_path = clean_filename(subdirectory_name)
        subdirectory_path = os.path.join(storage_entry.path, clean_subdirectory_path)
        if not os.path.isdir(subdirectory_path):
            while os.path.isfile(subdirectory_path):
                subdirectory_path += ".a"
            logger.debug(
                "Creating new subdirectory in the current storage directory ..."
            )
            os.makedirs(subdirectory_path)

            storage_entry.increment_subdirectory_count()
            logger.debug(
                "Successfully created new subdirectory in the current storage directory."
            )

        return subdirectory_path

    @staticmethod
    def healthcheck() -> bool:
        """Provides a healthcheck for the storage.

        Returns:
            True if storage is healthy,
            False if there is no unique current storage directory
            or the count of subdirectories for one of the directories is wrong.
        """
        unique_current = Storage.objects.filter(current=True).count() < 2
        if not unique_current:
            logger.critical("More than one currently used storage direcory!!!")
            return False

        correct_dir_count = Storage.objects.count() == len(
            os.listdir(settings.STORAGE_PATH)
        )
        if not correct_dir_count:
            logger.critical(
                "Number of paths in storage doesnt match the index in the database!!!"
            )
            return False

        correct_subdir_count = all(
            storage.subdirectory_count == len(os.listdir(storage.path))
            for storage in Storage.objects.all()
        )
        if not correct_subdir_count:
            logger.critical(
                "Number of paths in a storage directory doesnt match the index in the database!!!"
            )
            return False

        return True
