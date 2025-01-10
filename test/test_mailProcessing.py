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


import pytest
import Emailkasten.mailProcessing
from models.test_AccountModel import fixture_account
from models.test_MailboxModel import fixture_mailbox


@pytest.fixture(name='mock_logger', autouse=True)
def fixture_mock_logger(mocker):
    """Mocks :attr:`Emailkasten.fileManagment.logger` of the module."""
    return mocker.patch('Emailkasten.mailProcessing.logger')


@pytest.mark.parametrize(
    'protocol, expected_call',
    [
        ('IMAP', 'Emailkasten.IMAPFetcher.testAccount'),
        ('POP3', 'Emailkasten.POP3Fetcher.testAccount'),
        ('IMAP_SSl', 'Emailkasten.IMAP_SSL_Fetcher.testAccount'),
        ('POP3_SSL', 'Emailkasten.POP3_SSL_Fetcher.testAccount')
    ]
)
def test_testAccount_success(mocker, mock_logger, account, protocol, expected_call):
    account.protocol = protocol
    mock_testAccount = mocker.patch(expected_call, return_value=1)

    result = Emailkasten.mailProcessing.testAccount(account)

    assert result == 1
    mock_testAccount.assert_called_once_with(account)
    mock_logger.info.assert_called()


@pytest.mark.parametrize(
    'protocol, expected_call',
    [
        ('IMAP', 'Emailkasten.IMAPFetcher.testMailbox'),
        ('POP3', 'Emailkasten.POP3Fetcher.testMailbox'),
        ('IMAP_SSl', 'Emailkasten.IMAP_SSL_Fetcher.testMailbox'),
        ('POP3_SSL', 'Emailkasten.POP3_SSL_Fetcher.testMailbox')
    ]
)
def test_testMailbox_success(mocker, mock_logger, mailbox):
    mailbox.account.protocol = protocol
    mock_testAccount = mocker.patch(expected_call, return_value=1)

    result = Emailkasten.mailProcessing.testMailbox(account)

    assert result == 1
    mock_testAccount.assert_called_once_with(account)
    mock_logger.info.assert_called()
