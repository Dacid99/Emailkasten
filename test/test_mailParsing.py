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

"""Test module for :mod:`core.utils.mailParsing`.

Fixtures:
    :func:`fixture_mock_logger`: Mocks :attr:`logger` of the module.
    :func:`fixture_mock_good_mailMessage`: Mocks a valid :class:`email.message.Message`.
    :func:`fixture_mock_special_mailMessage`: Mocks a valid :class:`email.message.Message` with special contents.
    :func:`fixture_mock_bad_mailMessage`: Mocks an invalid :class:`email.message.Message`.
    :func:`fixture_mock_no_mailMessage`: Mocks a none message.
    :func:`fixture_mock_empty_parsedMailDict`: Mocks an empty parsedMail :class:`dict` that the mail is parsed into.
"""

import zoneinfo
from datetime import datetime
from email.message import EmailMessage
from email.utils import format_datetime

import pytest

import core.constants
import core.utils.mailParsing


@pytest.fixture(name="mock_logger", autouse=True)
def fixture_mock_logger(mocker):
    """Mocks :attr:`logger` of the module."""
    return mocker.patch("core.utils.mailParsing.logger")


@pytest.fixture(name="fake_single_header")
def fixture_fake_single_header(faker):
    return (faker.word(), faker.sentence(nb_words=5))


@pytest.fixture(name="fake_date_headervalue")
def fixture_fake_date_headervalue(faker):
    return faker.date_time(tzinfo=zoneinfo.ZoneInfo(faker.timezone()))


@pytest.fixture(name="fake_multi_header")
def fixture_fake_multi_header(faker):
    return (faker.word(), [faker.sentence(nb_words=5), faker.name(), faker.file_name()])


@pytest.fixture(name="emailMessage")
def fixture_emailMessage(fake_single_header, fake_multi_header):
    """A valid :class:`email.message.EmailMessage`."""
    testMessage = EmailMessage()
    testMessage.add_header(*fake_single_header)
    for value in fake_multi_header[1]:
        testMessage.add_header(fake_multi_header[0], value)
    return testMessage


@pytest.fixture(name="bad_emailMessage")
def fixture_bad_emailMessage():
    """A valid :class:`email.message.EmailMessage`."""
    testMessage = EmailMessage()
    testMessage.add_header("Date", "not a datetime str")
    return testMessage


@pytest.fixture(name="empty_emailMessage")
def fixture_empty_emailMessage():
    """An invalid :class:`email.message.Message`."""
    testMessage = EmailMessage()
    return testMessage


@pytest.fixture(name="no_emailMessage")
def fixture_no_emailMessage():
    """A none message."""
    testMessage = None
    return testMessage


@pytest.fixture(name="mock_timezone_now")
def fixture_mock_timezone(mocker, faker):
    """Mocks :func:`django.utils.timezone.now`."""
    return mocker.patch("django.utils.timezone.now", return_value=faker.date_time())


@pytest.mark.parametrize(
    "header, expectedResult",
    [
        (
            "Some header text without special chars",
            "Some header text without special chars",
        ),
        (
            "=?utf-8?q?H=C3=A4ng=C3=B1en_Loch_Junge_also_m=C3=BCssen=C3=A1?= Wetter.",
            "Hängñen Loch Junge also müssená Wetter.",
        ),
        (
            "Ms. Cassandra =?utf-8?b?R2lsbGVz0JRwafCfmIpl?= <aliciaward@example.com>",
            "Ms. Cassandra GillesДpi😊e <aliciaward@example.com>",
        ),
        (
            "=?utf-8?q?=C3=89tabl=C3=A9ir_mur_souffler_casser=C3=AD?= comprendre.",
            "Établéir mur souffler casserí comprendre.",
        ),
        (
            "=?utf-8?b?5Lit5bO24piF0Jkg6Zm95a2Q?= <kenichiito@example.com>",
            "中島★Й 陽子 <kenichiito@example.com>",
        ),
    ],
)
def test_decodeHeader_success(header, expectedResult):
    result = core.utils.mailParsing.decodeHeader(header)

    assert result == expectedResult


def test_getHeader_single_success(emailMessage, fake_single_header):
    result = core.utils.mailParsing.getHeader(emailMessage, fake_single_header[0])

    assert result == fake_single_header[1]


def test_getHeader_multi_success(emailMessage, fake_multi_header):
    result = core.utils.mailParsing.getHeader(emailMessage, fake_multi_header[0])

    assert result == ", ".join(fake_multi_header[1])


def test_getHeader_multi_joinparam_success(emailMessage, fake_multi_header):
    result = core.utils.mailParsing.getHeader(
        emailMessage, fake_multi_header[0], joiningString="test"
    )

    assert result == "test".join(fake_multi_header[1])


def test_getHeader_fallback(empty_emailMessage, fake_single_header):
    result = core.utils.mailParsing.getHeader(empty_emailMessage, fake_single_header[0])

    assert result is None


def test_getHeader_fallbackparam_fallback(empty_emailMessage, fake_single_header):
    result = core.utils.mailParsing.getHeader(
        empty_emailMessage, fake_single_header[0], fallbackCallable=lambda: "fallback"
    )

    assert result == "fallback"


def test_getHeader_failure(no_emailMessage, fake_single_header):
    with pytest.raises(AttributeError):
        core.utils.mailParsing.getHeader(
            no_emailMessage, fake_single_header[0], fallbackCallable=lambda: "fallback"
        )


def test_getDatetimeHeader_success(
    emailMessage, mock_logger, mock_timezone_now, fake_date_header
):
    result = core.utils.mailParsing.getDatetimeHeader(emailMessage)
    mock_logger.warning.assert_not_called()
    mock_timezone_now.assert_not_called()
    assert isinstance(result, datetime)
    assert format_datetime(result) == format_datetime(fake_date_header[1])


def test_getDatetimeHeader_fallback(empty_emailMessage, mock_logger, mock_timezone_now):
    result = core.utils.mailParsing.getDatetimeHeader(empty_emailMessage)
    mock_logger.warning.assert_called()
    mock_timezone_now.assert_called()
    assert isinstance(result, datetime)
    assert format_datetime(result) == format_datetime(mock_timezone_now.return_value)


def test_getDatetimeHeader_badHeader_fallback(
    bad_emailMessage, mock_logger, mock_timezone_now
):
    result = core.utils.mailParsing.getDatetimeHeader(bad_emailMessage)
    mock_logger.warning.assert_called()
    mock_timezone_now.assert_called()
    assert isinstance(result, datetime)
    assert format_datetime(result) == format_datetime(mock_timezone_now.return_value)


@pytest.mark.parametrize(
    "nameBytes, expectedName",
    [
        (b"INBOX", "INBOX"),
        (
            b"Dr&AOc-. Bianka F&APY-rste&BBk-r",
            "Drç. Bianka FörsteЙr",
        ),
        (
            b"Yves Pr&AN8EGQ-uvost",
            "Yves PrßЙuvost",
        ),
        (
            b"&ZY4mBQDfheQ- &Zg5,jg-",
            "斎★ß藤 明美",
        ),
    ],
)
def test_parseMailboxName_success(nameBytes, expectedName):
    result = core.utils.mailParsing.parseMailboxName(nameBytes)

    assert result == expectedName
