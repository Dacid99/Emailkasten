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

"""Conftest for :mod:`test.core`.

Fixtures:
    :func:`fixture_accountModel`: Fixture creating an :class:`core.models.AccountModel.AccountModel` instance for testing.
    :func:`fixture_attachmentModel`: Fixture creating an :class:`core.models.AttachmentModel.AttachmentModel` instance for testing.
    :func:`fixture_correspondentModel`: Fixture creating an :class:`core.models.CorrespondentModel.CorrespondentModel` instance for testing.
    :func:`fixture_daemonModel`: Fixture creating an :class:`core.models.DaemonModel.DaemonModel` instance for testing.
    :func:`fixture_emailModel`: Fixture creating an :class:`core.models.EMailCorrespondentsModel.EMailCorrespondentsModel` instance for testing.
    :func:`fixture_emailCorrespondentsModel`: Fixture creating an :class:`core.models.EMailModel.EMailModel` instance for testing.
    :func:`fixture_mailboxModel`: Fixture creating an :class:`core.models.MailboxModel.MailboxModel` instance for testing.
    :func:`fixture_mailinglistModel`: Fixture creating an :class:`core.models.MailingListModel.MailingListModel` instance for testing.
"""

from __future__ import annotations

from email.message import Message

import pytest
from model_bakery import baker

from core.models.AccountModel import AccountModel
from core.models.AttachmentModel import AttachmentModel
from core.models.CorrespondentModel import CorrespondentModel
from core.models.DaemonModel import DaemonModel
from core.models.EMailCorrespondentsModel import EMailCorrespondentsModel
from core.models.EMailModel import EMailModel
from core.models.MailboxModel import MailboxModel
from core.models.MailingListModel import MailingListModel


@pytest.fixture
def accountModel() -> AccountModel:
    """Fixture creating an :class:`core.models.AccountModel.AccountModel` .

    Returns:
        The accountModel instance for testing.
    """
    return baker.make(AccountModel)


@pytest.fixture
def attachmentModel(faker) -> AttachmentModel:
    """Fixture creating an :class:`core.models.AttachmentModel.AttachmentModel` owned by :attr:`owner_user`.

    Returns:
        The attachment instance for testing.
    """
    return baker.make(AttachmentModel, file_path=faker.file_path(extension="pdf"))


@pytest.fixture
def correspondentModel() -> CorrespondentModel:
    """Fixture creating an :class:`core.models.CorrespondentModel.CorrespondentModel` instance for testing.

    Returns:
        The correspondentModel instance for testing.
    """
    return baker.make(CorrespondentModel)


@pytest.fixture
def daemonModel(faker) -> DaemonModel:
    """Fixture creating an :class:`core.models.DaemonModel.DaemonModel`.

    Returns:
        The daemonModel instance for testing.
    """
    return baker.make(DaemonModel, log_filepath=faker.file_path(extension="log"))


@pytest.fixture
def emailModel() -> EMailModel:
    """Fixture creating an :class:`core.models.EMailModel.EMailModel`.

    Returns:
        The emailModel instance for testing.
    """
    return baker.make(EMailModel)


@pytest.fixture
def emailCorrespondentModel() -> EMailCorrespondentsModel:
    """Fixture creating an :class:`core.models.EMailModel.EMailModel` instance for testing.

    Returns:
        The emailCorrespondentModel instance for testing.
    """
    return baker.make(EMailCorrespondentsModel)


@pytest.fixture
def mailboxModel(faker) -> MailboxModel:
    """Fixture creating an :class:`core.models.MailboxModel.MailboxModel`.

    Note:
        `name` must contain non-ASCII chars to allow testing utf7 encoding.

    Returns:
        The mailboxModel instance for testing.
    """
    return baker.make(MailboxModel, name=faker.name() + "äßμ")


@pytest.fixture
def mailingListModel() -> MailingListModel:
    """Fixture creating an :class:`core.models.MailboxModel.MailboxModel`.

    Returns:
        The mailingListModel instance for testing.
    """
    return baker.make(MailingListModel)


@pytest.fixture
def mock_message(mocker):
    """Fixture providing a mock :class:`email.message.Message` instance.

    Returns:
        :class:`unittest.mock.MagicMock`: The mock :class:`email.message.Message`.
    """
    return mocker.MagicMock(spec=Message)
