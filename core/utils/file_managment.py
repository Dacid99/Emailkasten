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


"""Provides functions for saving various files to the storage.

Global variables:
    logger (:class:`logging.Logger`): The logger for this module.
"""

from __future__ import annotations

import logging
import os.path
import re
from builtins import open  # required for testing
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from collections.abc import Callable
    from io import BufferedWriter


logger = logging.getLogger(__name__)


def save_store(
    storing_func: Callable[[BufferedWriter, Any], None],
) -> Callable[[str, Any], str | None]:
    """Decorator to ensure no files are overwriten and errors are handled when storing files.

    Exchanges the first file buffer argument with a filepath argument.

    Todo:
        Needs a test that doesnt require workarounds, e.g. using tempfile.

    Args:
        storing_func: The function writing a file into the storage to wrap.

    Returns:
        save_storing_func: The wrapped function.
    """

    def save_storing_func(file_path: str, *args: Any, **kwargs: Any) -> str | None:
        if os.path.exists(file_path):
            try:
                if os.path.getsize(file_path) > 0:
                    logger.debug(
                        "Not writing to file %s, it already exists and is not empty.",
                        file_path,
                    )
                    return file_path
            except PermissionError:
                pass  # this is only relevant for fakefs testing
            logger.debug(
                "Writing to file %s, it already exists but is empty.", file_path
            )
        else:
            logger.debug("Creating and writing to file %s...", file_path)

        try:
            with open(file_path, "wb") as file:
                storing_func(file, *args, **kwargs)
        except PermissionError:
            logger.exception(
                "Failed to write to file %s, it is not writeable!",
                file_path,
            )
            return None
        except Exception:
            logger.exception("Failed to write to file %s!", file_path)
            if os.path.exists(file_path):
                logger.debug("Clearing incomplete file ...")
                try:
                    with open(file_path, "wb") as file:
                        file.truncate(0)

                    logger.debug("Successfully cleared incomplete file.")

                except OSError:
                    logger.exception("Failed to clear the incomplete file!")
            else:
                logger.debug("File was not created")
            return None
        else:
            logger.debug("Successfully wrote to file.")
            return file_path

    return save_storing_func


DANGEROUS_CHAR_REGEX = r"[/~]"


def clean_filename(filename: str) -> str:
    r"""Sanitizes dangerous chars and strips whitespace from a filename.

    Chars /, ~ are replaced with _.

    Args:
        filename: The filename without extension.

    Returns:
        The cleaned filename without extension.
    """
    cleaned_filename = re.sub(DANGEROUS_CHAR_REGEX, "_", filename)
    return re.sub(r"\s+", "", cleaned_filename).strip()
