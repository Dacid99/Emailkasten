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

import datetime
from email.message import Message

import pytest

import Emailkasten.constants
import Emailkasten.mailParsing


@pytest.fixture(name="mock_logger", autouse=True)
def fixture_mock_logger(mocker):
    return mocker.patch('Emailkasten.mailParsing.logger')

@pytest.fixture(name="mock_good_mailMessage", scope='module')
def fixture_mock_good_mailMessage():
    testMessage = Message()
    testMessage.add_header("Message-ID", 'abcdefgäöüß§')
    testMessage.add_header("Subject", 'This a test SUBJEcT line äöüß§')
    testMessage.add_header("Date", 'Fri, 09 Nov 2001 01:08:47 -0000')
    testMessage.add_header("test", 'test äöüß§')
    testMessage.add_header("multi", 'test')
    testMessage.add_header("multi", 'äöüß§\t')
    testMessage.add_header("multi", '123456')
    return testMessage

@pytest.fixture(name="mock_special_mailMessage", scope='module')
def fixture_mock_special_mailMessage():
    testMessage = Message()
    testMessage.add_header("Subject", 'This a test SUBJEcT line äöüß§ \t ')
    return testMessage

@pytest.fixture(name="mock_bad_mailMessage", scope='module')
def fixture_mock_bad_mailMessage():
    testMessage = Message()
    return testMessage

@pytest.fixture(name="mock_no_mailMessage", scope='module')
def fixture_mock_no_mailMessage():
    testMessage = None
    return testMessage


@pytest.mark.parametrize(
    'testHeader, expectedResult',
    [
        ('test äöüß§', "test äöüß§")
    ]
)
def test__decodeHeader(mock_logger, testHeader, expectedResult):
    decodedHeader = Emailkasten.mailParsing._decodeHeader(testHeader)
    assert decodedHeader == expectedResult


@pytest.mark.parametrize(
        'testMailers, expectedResult, warningCalled',
        [
            (["Test äöüß§ <test@testdomain.tld>"], [("Test äöüß§", "test@testdomain.tld")], False),
            (["Test Persön <testtestdomain.tld>"], [("Test Persön", "testtestdomain.tld")], True),
            (["test@testdomain.tld"], [("", "test@testdomain.tld")], False)
        ])
def test__separateRFC2822MailAddressFormat(mock_logger, testMailers, expectedResult, warningCalled):
    separatedMailers = Emailkasten.mailParsing._separateRFC2822MailAddressFormat(testMailers)

    assert separatedMailers == expectedResult


def test__parseMessageID_success(mock_logger, mock_good_mailMessage):
    messageID = Emailkasten.mailParsing._parseMessageID(mock_good_mailMessage)

    assert messageID == 'abcdefgäöüß§'
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()


def test__parseMessageID_emptyMessage(mock_logger, mock_bad_mailMessage):
    messageID = Emailkasten.mailParsing._parseMessageID(mock_bad_mailMessage)

    assert messageID == str(hash(mock_bad_mailMessage))
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_called()
    mock_logger.error.assert_not_called()


def test__parseMessageID_noMessage(mock_logger, mock_no_mailMessage):
    with pytest.raises(AttributeError):
        messageID = Emailkasten.mailParsing._parseMessageID(mock_no_mailMessage)


def test__parseDate_success(mock_logger, mock_good_mailMessage):
    date = Emailkasten.mailParsing._parseDate(mock_good_mailMessage)

    assert date == datetime.datetime(2001, 11, 9, 1, 8, 47)
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()


def test__parseDate_emptyMessage(mock_logger, mock_bad_mailMessage):
    date = Emailkasten.mailParsing._parseDate(mock_bad_mailMessage)

    assert date == datetime.datetime(1971, 1, 1, 0, 0, 0)
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_called()
    mock_logger.error.assert_not_called()


def test__parseDate_noMessage(mock_logger, mock_no_mailMessage):
    with pytest.raises(AttributeError):
        date = Emailkasten.mailParsing._parseDate(mock_no_mailMessage)


@pytest.mark.parametrize(
    "stripTexts, expectedResult",
    [(True, "This a test SUBJEcT line äöüß§"), (False, "This a test SUBJEcT line äöüß§ \t ")],
)
def test__parseSubject_success(mock_logger, stripTexts, expectedResult, mocker, mock_special_mailMessage):
    mock_parsingConfiguration = mocker.patch('Emailkasten.mailParsing.ParsingConfiguration')
    mock_parsingConfiguration.STRIP_TEXTS = stripTexts

    subject = Emailkasten.mailParsing._parseSubject(mock_special_mailMessage)

    assert subject == expectedResult
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()


def test__parseSubject_emptyMessage(mock_logger, mock_bad_mailMessage):
    subject = Emailkasten.mailParsing._parseSubject(mock_bad_mailMessage)

    assert subject == ''
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_called()
    mock_logger.error.assert_not_called()


def test__parseSubject_noMessage(mock_logger, mock_no_mailMessage):
    with pytest.raises(AttributeError):
        subject = Emailkasten.mailParsing._parseSubject(mock_no_mailMessage)


def test__parseHeader_success(mock_logger, mock_good_mailMessage):
    header = Emailkasten.mailParsing._parseHeader(mock_good_mailMessage, "test")

    assert header == "test äöüß§"
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()


def test__parseHeader_emptyMessage(mock_logger, mock_bad_mailMessage):
    header = Emailkasten.mailParsing._parseHeader(mock_bad_mailMessage, "test")

    assert header == ''
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()


def test__parseHeader_noMessage(mock_logger, mock_no_mailMessage):
    with pytest.raises(AttributeError):
        header = Emailkasten.mailParsing._parseHeader(mock_no_mailMessage, "test")


def test__parseMultipleHeader_success(mock_logger, mock_good_mailMessage):
    header = Emailkasten.mailParsing._parseMultipleHeader(mock_good_mailMessage, "multi")

    assert header == "test\näöüß§\t\n123456"
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()


def test__parseMultipleHeader_emptyMessage(mock_logger, mock_bad_mailMessage):
    header = Emailkasten.mailParsing._parseMultipleHeader(mock_bad_mailMessage, "multi")

    assert header == ''
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()


def test__parseMultipleHeader_noMessage(mock_logger, mock_no_mailMessage):
    with pytest.raises(AttributeError):
        header = Emailkasten.mailParsing._parseMultipleHeader(mock_no_mailMessage, "multi")


#def test_parseMail(mocker):
