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

import contextlib

import pytest

from core.EmailArchiverDaemon import EmailArchiverDaemon
from core.EmailArchiverDaemonRegistry import EmailArchiverDaemonRegistry


@pytest.fixture(autouse=True)
def mock_logger(mocker):
    return mocker.patch(
        "core.EmailArchiverDaemonRegistry.EmailArchiverDaemonRegistry.logger",
        autospec=True,
    )


@pytest.fixture
def mock_running_daemon(mocker, fake_daemon):
    mock_running_daemon = mocker.MagicMock()
    EmailArchiverDaemonRegistry._running_daemons[fake_daemon.id] = mock_running_daemon
    yield mock_running_daemon
    with contextlib.suppress(KeyError):
        EmailArchiverDaemonRegistry._running_daemons.pop(fake_daemon.id)


@pytest.fixture
def mock_EmailArchiverDaemon(mocker):
    return mocker.patch(
        "core.EmailArchiverDaemonRegistry.EmailArchiverDaemon",
        autospec=True,
        return_value=mocker.Mock(spec=EmailArchiverDaemon),
    )


@pytest.mark.django_db
def test_is_running_active(mock_running_daemon, fake_daemon):
    result = EmailArchiverDaemonRegistry.is_running(fake_daemon)

    assert result is True


@pytest.mark.django_db
def test_is_running_inactive(fake_daemon):
    result = EmailArchiverDaemonRegistry.is_running(fake_daemon)

    assert result is False


@pytest.mark.django_db
def test_update_daemon(mock_logger, mock_running_daemon, fake_daemon):
    EmailArchiverDaemonRegistry.update_daemon(fake_daemon)

    mock_running_daemon.update.assert_called_once()
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_test_daemon_success(mock_logger, mock_EmailArchiverDaemon, fake_daemon):
    result = EmailArchiverDaemonRegistry.test_daemon(fake_daemon)

    assert result is True
    mock_EmailArchiverDaemon.assert_called_once_with(fake_daemon)
    mock_EmailArchiverDaemon.return_value.cycle.assert_called_once_with()
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_test_daemon_failure_exception(
    mock_logger, mock_EmailArchiverDaemon, fake_daemon
):
    mock_EmailArchiverDaemon.return_value.cycle.side_effect = Exception

    result = EmailArchiverDaemonRegistry.test_daemon(fake_daemon)

    assert result is False
    mock_EmailArchiverDaemon.assert_called_once_with(fake_daemon)
    mock_EmailArchiverDaemon.return_value.cycle.assert_called_once_with()
    mock_logger.debug.assert_called()
    mock_logger.exception.assert_called()


@pytest.mark.django_db
def test_start_daemon_active(
    mock_logger, mock_EmailArchiverDaemon, mock_running_daemon, fake_daemon
):
    result = EmailArchiverDaemonRegistry.start_daemon(fake_daemon)

    assert result is False
    mock_EmailArchiverDaemon.assert_not_called()
    mock_EmailArchiverDaemon.return_value.start.assert_not_called()
    assert fake_daemon.id in EmailArchiverDaemonRegistry._running_daemons
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_start_daemon_inactive(mock_logger, mock_EmailArchiverDaemon, fake_daemon):
    result = EmailArchiverDaemonRegistry.start_daemon(fake_daemon)

    assert result is True
    mock_EmailArchiverDaemon.assert_called_once_with(fake_daemon)
    mock_EmailArchiverDaemon.return_value.start.assert_called_once_with()
    assert fake_daemon.id in EmailArchiverDaemonRegistry._running_daemons
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_stop_daemon_active(mock_logger, mock_running_daemon, fake_daemon):
    result = EmailArchiverDaemonRegistry.stop_daemon(fake_daemon)

    assert result is True
    mock_running_daemon.stop.assert_called_once_with()
    assert fake_daemon.id not in EmailArchiverDaemonRegistry._running_daemons
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_stop_daemon_inactive(mock_logger, fake_daemon):
    result = EmailArchiverDaemonRegistry.stop_daemon(fake_daemon)

    assert result is False
    assert fake_daemon.id not in EmailArchiverDaemonRegistry._running_daemons
    mock_logger.debug.assert_called()
