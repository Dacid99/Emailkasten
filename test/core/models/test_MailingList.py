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

"""Test module for :mod:`core.models.MailingList`."""
from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import pytest
from django.db import IntegrityError
from django.urls import reverse
from model_bakery import baker

from core.models.MailingList import MailingList


if TYPE_CHECKING:
    from unittest.mock import MagicMock


@pytest.fixture(autouse=True)
def mock_logger(mocker) -> MagicMock:
    """Mocks the :class:`core.models.MailingList.logger`.

    Returns:
        The email instance for testing.
    """
    return mocker.patch("core.models.MailingList.logger", autospec=True)


@pytest.fixture
def mock_getHeader(mocker, faker):
    """Fixture mocking :func:`core.models.MailingList.getHeader`."""
    return mocker.patch(
        "core.models.MailingList.getHeader",
        autospec=True,
        return_value=faker.word(),
    )


@pytest.mark.django_db
def test_MailingList_fields(fake_mailingList):
    """Tests the fields of :class:`core.models.MailingList.MailingList`."""

    assert fake_mailingList.list_id is not None
    assert isinstance(fake_mailingList.list_id, str)
    assert fake_mailingList.list_owner is not None
    assert isinstance(fake_mailingList.list_owner, str)
    assert fake_mailingList.list_subscribe is not None
    assert isinstance(fake_mailingList.list_subscribe, str)
    assert fake_mailingList.list_unsubscribe is not None
    assert isinstance(fake_mailingList.list_unsubscribe, str)
    assert fake_mailingList.list_post is not None
    assert isinstance(fake_mailingList.list_post, str)
    assert fake_mailingList.list_help is not None
    assert isinstance(fake_mailingList.list_help, str)
    assert fake_mailingList.list_archive is not None
    assert isinstance(fake_mailingList.list_archive, str)
    assert fake_mailingList.is_favorite is False
    assert fake_mailingList.updated is not None
    assert isinstance(fake_mailingList.updated, datetime.datetime)
    assert fake_mailingList.created is not None
    assert isinstance(fake_mailingList.created, datetime.datetime)


@pytest.mark.django_db
def test_MailingList___str__(fake_mailingList):
    """Tests the string representation of :class:`core.models.MailingList.MailingList`."""
    assert fake_mailingList.list_id in str(fake_mailingList)


@pytest.mark.django_db
def test_MailingList_unique_constraints(fake_mailingList):
    """Tests the unique constraints of :class:`core.models.MailingList.MailingList`."""
    with pytest.raises(IntegrityError):
        baker.make(MailingList, list_id=fake_mailingList.list_id)


@pytest.mark.django_db
def test_MailingList_createFromEmailMessage_success(
    mocker, mock_message, mock_getHeader
):
    """Tests :func:`core.models.MailingList.MailingList.createFromEmailMessage`
    in case of success.
    """
    result = MailingList.createFromEmailMessage(mock_message)

    assert mock_getHeader.call_count == 7
    mock_getHeader.assert_has_calls(
        [
            mocker.call(mock_message, "List-Id"),
            mocker.call(mock_message, "List-Owner"),
            mocker.call(mock_message, "List-Subscribe"),
            mocker.call(mock_message, "List-Unsubscribe"),
            mocker.call(mock_message, "List-Post"),
            mocker.call(mock_message, "List-Help"),
            mocker.call(mock_message, "List-Archive"),
        ]
    )
    assert isinstance(result, MailingList)
    assert result.pk is not None
    assert result.list_id == mock_getHeader.return_value
    assert result.list_owner == mock_getHeader.return_value
    assert result.list_post == mock_getHeader.return_value
    assert result.list_help == mock_getHeader.return_value
    assert result.list_archive == mock_getHeader.return_value
    assert result.list_subscribe == mock_getHeader.return_value
    assert result.list_unsubscribe == mock_getHeader.return_value


@pytest.mark.django_db
def test_MailingList_createFromEmailMessage_duplicate(
    fake_mailingList, mock_message, mock_getHeader
):
    """Tests :func:`core.models.MailingList.MailingList.createFromEmailMessage`
    in case the mailinglist to be prepared is already in the database.
    """
    mock_getHeader.return_value = fake_mailingList.list_id
    result = MailingList.createFromEmailMessage(mock_message)

    assert result == fake_mailingList
    mock_getHeader.assert_called_once_with(mock_message, "List-Id")


@pytest.mark.django_db
def test_MailingList_createFromEmailMessage_no_list_id(
    mock_message, mock_logger, mock_getHeader
):
    """Tests :func:`core.models.MailingList.MailingList.createFromEmailMessage`
    in case there is no List-Id in the message argument.
    """
    mock_getHeader.return_value = None

    result = MailingList.createFromEmailMessage(mock_message)

    assert result is None
    mock_getHeader.assert_called_once_with(mock_message, "List-Id")
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_MailingList_get_absolute_url(fake_mailingList):
    """Tests :func:`core.models.MailingList.MailingList.get_absolute_url`."""
    result = fake_mailingList.get_absolute_url()

    assert result == reverse(
        f"web:{fake_mailingList.BASENAME}-detail",
        kwargs={"pk": fake_mailingList.pk},
    )


@pytest.mark.django_db
def test_MailingList_get_absolute_list_url(fake_mailingList):
    """Tests :func:`core.models.MailingList.MailingList.get_absolute_list_url`."""
    result = fake_mailingList.get_absolute_list_url()

    assert result == reverse(
        f"web:{fake_mailingList.BASENAME}-filter-list",
    )
