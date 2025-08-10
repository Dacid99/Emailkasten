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

"""Module with the tasks for celery."""

import logging
import time
from uuid import UUID

from celery import shared_task

from core.utils.fetchers.exceptions import MailAccountError, MailboxError

from .models.Daemon import Daemon


@shared_task
def fetch_emails(  # this must not be renamed or moved, otherwise existing daemons will break!
    daemon_uuid_string: str,
) -> None:
    """Celery task to fetch and store emails.

    Args:
        daemon_uuid_string: The uuid of the daemon instance that manages this task.

    Raises:
        Exception: Any exception that is raised during fetching.
    """
    logger = logging.getLogger(daemon_uuid_string)

    logger.info(
        "-------------------------------------------\nPerforming fetching emails task ..."
    )
    start_time = time.time()

    try:
        daemon = Daemon.objects.select_related("mailbox").get(
            uuid=UUID(daemon_uuid_string)
        )
    except Daemon.DoesNotExist:
        return
    try:
        daemon.mailbox.fetch(daemon.fetching_criterion)
    except Exception as exc:
        logger.exception(
            "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\nFailed to fetch emails!\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",
        )
        daemon.is_healthy = False
        daemon.save(update_fields=["is_healthy"])
        if isinstance(exc, ValueError):
            logger.warning(
                "The chosen fetching criterion is not available for this mailbox! Change it to a valid choice to fix this error.",
                exc_info=True,
            )
        elif isinstance(exc, MailAccountError):
            daemon.mailbox.account.is_healthy = False
            daemon.mailbox.account.save(update_fields=["is_healthy"])
            logger.exception(
                "There was an issue with the account. Please test them before continuing."
            )
        elif isinstance(exc, MailboxError):
            daemon.mailbox.is_healthy = False
            daemon.mailbox.save(update_fields=["is_healthy"])
        else:
            logger.exception("This is an unexpected error!")
        raise
    else:
        logger.info("Successfully fetched emails.")
        daemon.is_healthy = True
        daemon.save(update_fields=["is_healthy"])

    end_time = time.time()
    logger.info(
        "Fetching emails task finished in %s seconds\n!------------------------------------------",
        end_time - start_time,
    )
