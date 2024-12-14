# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import factory
import pytest
from django.contrib.auth.models import User

import Emailkasten.EMailArchiverDaemon
from Emailkasten.Models.AccountModel import AccountModel
from Emailkasten.Models.DaemonModel import DaemonModel
from Emailkasten.Models.MailboxModel import MailboxModel


@pytest.fixture(name='mock_getLogger', autouse=True)
def fixture_mock_getLogger(mocker):
    mock_logger = mocker.patch('Emailkasten.EMailArchiverDaemon.logging.Logger')
    return mocker.patch('Emailkasten.EMailArchiverDaemon.logging.getLogger', return_value = mock_logger)

@pytest.fixture(name='mock_runningDaemons')
def fixture_mock_runningDaemons():
    return {}

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    password = factory.PostGenerationMethodCall('set_password', 'password123')

class AccountModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AccountModel

    mail_address = factory.Faker("email")
    password = factory.Faker("password")
    mail_host = factory.Faker("domain_name")
    protocol = factory.Faker("random_element", elements = AccountModel.PROTOCOL_CHOICES.keys())
    user = factory.SubFactory(UserFactory)

class MailboxModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MailboxModel

    name = factory.Faker("name")
    account = factory.SubFactory(AccountModelFactory)

class DaemonModelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DaemonModel

    mailbox = factory.SubFactory(MailboxModelFactory)


@pytest.mark.django_db
@pytest.fixture(name='mock_daemonModel')
def fixture_mock_daemonModel():
    return DaemonModelFactory()


@pytest.mark.django_db
def test___init__(mock_daemonModel):
    daemonInstance = Emailkasten.EMailArchiverDaemon.EMailArchiverDaemon(mock_daemonModel)
    assert daemonInstance.thread is None
    assert daemonInstance is not None
    assert daemonInstance.isRunning is False


@pytest.mark.parametrize(
    'is_running',
    [
        True,
        False
    ]
)
@pytest.mark.django_db
def test_start(mocker, is_running):
    mock_threading = mocker.patch('Emailkasten.EMailArchiverDaemon.threading.Thread')
    daemonEntry = DaemonModelFactory(is_running = is_running)
    daemonInstance = Emailkasten.EMailArchiverDaemon.EMailArchiverDaemon(daemonEntry)
    daemonInstance.isRunning = is_running

    daemonInstance.start()

    assert daemonEntry.is_running is True
    assert daemonInstance.isRunning is True
    mock_threading.assert_called_once()
    assert mock_threading.start.call_count == 1 if is_running else 0

    daemonInstance.logger.info.assert_called()
