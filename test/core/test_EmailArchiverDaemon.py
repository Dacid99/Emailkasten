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

"""Test for :mod:`core.EmailArchiverDaemon`."""

import logging
import time

import pytest
from django.db.models.signals import post_save

from core.EmailArchiverDaemon import EmailArchiverDaemon
from core.models import Daemon
from core.signals.save_Daemon import post_save_daemon


@pytest.fixture(autouse=True)
def mock_logging_FileHandler(mocker):
    return mocker.patch(
        "core.EmailArchiverDaemon.logging.handlers.RotatingFileHandler", autospec=True
    )


@pytest.fixture
def mock_logger(mocker):
    return mocker.MagicMock(spec=logging.Logger)


@pytest.fixture(autouse=True)
def mock_logging_getLogger(mocker, mock_logger):
    return mocker.patch(
        "core.EmailArchiverDaemon.logging.getLogger",
        autospec=True,
        return_value=mock_logger,
    )


@pytest.fixture
def email_archiver_daemon(fake_daemon):
    return EmailArchiverDaemon(daemon=fake_daemon)


@pytest.mark.django_db
def test___init__(mock_logging_getLogger, fake_daemon):
    email_archiver_daemon = EmailArchiverDaemon(fake_daemon)

    assert email_archiver_daemon is not None
    assert email_archiver_daemon.daemon
    assert str(fake_daemon.uuid) in email_archiver_daemon.name
    assert email_archiver_daemon._daemon == fake_daemon
    assert email_archiver_daemon._stop_event is not None
    assert not email_archiver_daemon._stop_event.is_set()
    mock_logging_getLogger.assert_called_with(str(email_archiver_daemon))


@pytest.mark.django_db
def test_setup_logger(
    mock_logging_getLogger, mock_logger, mock_logging_FileHandler, fake_daemon
):
    email_archiver_daemon = EmailArchiverDaemon(daemon=fake_daemon)

    mock_logging_getLogger.assert_called_with(str(email_archiver_daemon))
    mock_logging_FileHandler.assert_called_with(
        filename=fake_daemon.log_filepath,
        backupCount=fake_daemon.log_backup_count,
        maxBytes=fake_daemon.logfile_size,
    )
    mock_logger.addHandler.assert_called_with(mock_logging_FileHandler.return_value)


@pytest.mark.django_db
def test_start_dryrun_success(mocker, fake_daemon, email_archiver_daemon):
    mock_thread_start = mocker.patch(
        "core.EmailArchiverDaemon.threading.Thread.start", autospec=True
    )
    fake_daemon.is_running = False
    fake_daemon.save(update_fields=["is_running"])

    email_archiver_daemon.start()

    fake_daemon.refresh_from_db()
    assert fake_daemon.is_running is True
    mock_thread_start.assert_called_once_with(email_archiver_daemon)
    email_archiver_daemon.logger.info.assert_called()


@pytest.mark.django_db
def test_start_dryrun_failure(mocker, fake_daemon, email_archiver_daemon):
    mock_thread_start = mocker.patch(
        "core.EmailArchiverDaemon.threading.Thread.start",
        autospec=True,
        side_effect=RuntimeError,
    )
    fake_daemon.is_running = True
    fake_daemon.save(update_fields=["is_running"])

    email_archiver_daemon.start()

    fake_daemon.refresh_from_db()
    assert fake_daemon.is_running is True
    mock_thread_start.assert_called_once_with(email_archiver_daemon)
    email_archiver_daemon.logger.debug.assert_called()


@pytest.mark.django_db
def test_stop_dryrun_success(fake_daemon, email_archiver_daemon):
    fake_daemon.is_running = True
    fake_daemon.save(update_fields=["is_running"])

    email_archiver_daemon.stop()

    fake_daemon.refresh_from_db()
    assert fake_daemon.is_running is False
    email_archiver_daemon.logger.info.assert_called()


@pytest.mark.django_db
def test_stop_dryrun_failure(fake_daemon, email_archiver_daemon):
    email_archiver_daemon._stop_event.set()
    fake_daemon.is_running = False
    fake_daemon.save(update_fields=["is_running"])

    email_archiver_daemon.stop()

    fake_daemon.refresh_from_db()
    assert fake_daemon.is_running is False
    email_archiver_daemon.logger.debug.assert_called()


@pytest.mark.django_db
def test_start_stop(mocker, fake_daemon, email_archiver_daemon):
    mock_cycle = mocker.patch(
        "core.EmailArchiverDaemon.EmailArchiverDaemon.cycle", autospec=True
    )
    mock_sleep = mocker.patch("core.EmailArchiverDaemon.time.sleep", autospec=True)
    fake_daemon.is_running = False
    fake_daemon.save(update_fields=["is_running"])

    email_archiver_daemon.start()
    email_archiver_daemon.stop()
    email_archiver_daemon.join()

    fake_daemon.refresh_from_db()
    assert fake_daemon.is_running is False
    assert not email_archiver_daemon.is_alive()
    email_archiver_daemon.logger.info.assert_called()


@pytest.mark.django_db
def test_update(fake_daemon, email_archiver_daemon):
    post_save.disconnect(post_save_daemon, Daemon)

    fake_daemon = Daemon.objects.get(id=fake_daemon.id)
    old_cycle_interval = fake_daemon.cycle_interval
    fake_daemon.cycle_interval = old_cycle_interval * 12
    fake_daemon.save()
    assert email_archiver_daemon._daemon.cycle_interval == old_cycle_interval

    email_archiver_daemon.update()

    assert email_archiver_daemon._daemon.cycle_interval == fake_daemon.cycle_interval
    email_archiver_daemon.logger.debug.assert_called()

    post_save.connect(post_save_daemon, Daemon)


@pytest.mark.django_db
def test_cycle_success(mocker, email_archiver_daemon):
    mock_mailbox_fetch = mocker.patch(
        "core.models.Mailbox.Mailbox.fetch", autospec=True
    )
    email_archiver_daemon._daemon.is_healthy = False
    email_archiver_daemon._daemon.save(update_fields=["is_healthy"])

    email_archiver_daemon.cycle()

    mock_mailbox_fetch.assert_called_once_with(
        email_archiver_daemon._daemon.mailbox,
        email_archiver_daemon._daemon.fetching_criterion,
    )
    assert email_archiver_daemon._daemon.is_healthy is True
    email_archiver_daemon.logger.debug.assert_called()


@pytest.mark.django_db
def test_cycle_exception(mocker, email_archiver_daemon):
    mock_mailbox_fetch = mocker.patch(
        "core.models.Mailbox.Mailbox.fetch",
        autospec=True,
        side_effect=AssertionError,
    )
    email_archiver_daemon._daemon.is_healthy = False
    email_archiver_daemon._daemon.save(update_fields=["is_healthy"])

    with pytest.raises(AssertionError):
        email_archiver_daemon.cycle()

    mock_mailbox_fetch.assert_called_once_with(
        email_archiver_daemon._daemon.mailbox,
        email_archiver_daemon._daemon.fetching_criterion,
    )
    assert email_archiver_daemon._daemon.is_healthy is False
    email_archiver_daemon.logger.debug.assert_called()


@pytest.mark.django_db
def test_run_success(mocker, email_archiver_daemon):
    mock_cycle = mocker.patch(
        "core.EmailArchiverDaemon.EmailArchiverDaemon.cycle", autospec=True
    )
    mock_sleep = mocker.patch("core.EmailArchiverDaemon.time.sleep", autospec=True)

    email_archiver_daemon.start()

    assert email_archiver_daemon.is_alive()
    mock_sleep.assert_called_with(email_archiver_daemon._daemon.cycle_interval)
    mock_cycle.assert_called()

    email_archiver_daemon.stop()
    email_archiver_daemon.join()

    assert not email_archiver_daemon.is_alive()


@pytest.mark.django_db
def test_run_exception(mocker, email_archiver_daemon):
    mock_cycle = mocker.patch(
        "core.EmailArchiverDaemon.EmailArchiverDaemon.cycle",
        autospec=True,
        side_effect=AssertionError,
    )
    mock_sleep = mocker.patch("core.EmailArchiverDaemon.time.sleep", autospec=True)

    email_archiver_daemon.start()

    assert email_archiver_daemon.is_alive()
    mock_cycle.assert_called()
    email_archiver_daemon.logger.exception.assert_called()
    mock_sleep.assert_called_with(email_archiver_daemon._daemon.restart_time)
    assert email_archiver_daemon._daemon.is_healthy is False

    email_archiver_daemon.stop()
    email_archiver_daemon.join()

    assert not email_archiver_daemon.is_alive()
