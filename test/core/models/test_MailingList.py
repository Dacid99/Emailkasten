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

from core.models import MailingList


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
def mock_get_header(mocker, faker):
    """Fixture mocking :func:`core.models.MailingList.get_header`."""
    return mocker.patch(
        "core.models.MailingList.get_header",
        autospec=True,
        return_value=faker.word(),
    )


@pytest.mark.django_db
def test_MailingList_fields(fake_mailing_list):
    """Tests the fields of :class:`core.models.MailingList.MailingList`."""

    assert fake_mailing_list.list_id is not None
    assert isinstance(fake_mailing_list.list_id, str)
    assert fake_mailing_list.list_owner is not None
    assert isinstance(fake_mailing_list.list_owner, str)
    assert fake_mailing_list.list_subscribe is not None
    assert isinstance(fake_mailing_list.list_subscribe, str)
    assert fake_mailing_list.list_unsubscribe is not None
    assert isinstance(fake_mailing_list.list_unsubscribe, str)
    assert fake_mailing_list.list_post is not None
    assert isinstance(fake_mailing_list.list_post, str)
    assert fake_mailing_list.list_help is not None
    assert isinstance(fake_mailing_list.list_help, str)
    assert fake_mailing_list.list_archive is not None
    assert isinstance(fake_mailing_list.list_archive, str)
    assert fake_mailing_list.is_favorite is False
    assert fake_mailing_list.updated is not None
    assert isinstance(fake_mailing_list.updated, datetime.datetime)
    assert fake_mailing_list.created is not None
    assert isinstance(fake_mailing_list.created, datetime.datetime)


@pytest.mark.django_db
def test_MailingList___str__(fake_mailing_list):
    """Tests the string representation of :class:`core.models.MailingList.MailingList`."""
    assert fake_mailing_list.list_id in str(fake_mailing_list)


@pytest.mark.django_db
def test_MailingList_unique_constraints(fake_mailing_list):
    """Tests the unique constraints of :class:`core.models.MailingList.MailingList`."""
    with pytest.raises(IntegrityError):
        baker.make(MailingList, list_id=fake_mailing_list.list_id)


@pytest.mark.django_db
def test_MailingList_create_from_email_message_success(
    mocker, mock_message, mock_get_header
):
    """Tests :func:`core.models.MailingList.MailingList.create_from_email_message`
    in case of success.
    """
    result = MailingList.create_from_email_message(mock_message)

    assert mock_get_header.call_count == 7
    mock_get_header.assert_has_calls(
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
    assert result.list_id == mock_get_header.return_value
    assert result.list_owner == mock_get_header.return_value
    assert result.list_post == mock_get_header.return_value
    assert result.list_help == mock_get_header.return_value
    assert result.list_archive == mock_get_header.return_value
    assert result.list_subscribe == mock_get_header.return_value
    assert result.list_unsubscribe == mock_get_header.return_value


@pytest.mark.django_db
def test_MailingList_create_from_email_message_duplicate(
    fake_mailing_list, mock_message, mock_get_header
):
    """Tests :func:`core.models.MailingList.MailingList.create_from_email_message`
    in case the mailinglist to be prepared is already in the database.
    """
    mock_get_header.return_value = fake_mailing_list.list_id
    result = MailingList.create_from_email_message(mock_message)

    assert result == fake_mailing_list
    mock_get_header.assert_called_once_with(mock_message, "List-Id")


@pytest.mark.django_db
def test_MailingList_create_from_email_message_no_list_id(
    mock_message, mock_logger, mock_get_header
):
    """Tests :func:`core.models.MailingList.MailingList.create_from_email_message`
    in case there is no List-Id in the message argument.
    """
    mock_get_header.return_value = None

    result = MailingList.create_from_email_message(mock_message)

    assert result is None
    mock_get_header.assert_called_once_with(mock_message, "List-Id")
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_MailingList_get_absolute_url(fake_mailing_list):
    """Tests :func:`core.models.MailingList.MailingList.get_absolute_url`."""
    result = fake_mailing_list.get_absolute_url()

    assert result == reverse(
        f"web:{fake_mailing_list.BASENAME}-detail",
        kwargs={"pk": fake_mailing_list.pk},
    )


@pytest.mark.django_db
def test_MailingList_get_absolute_list_url(fake_mailing_list):
    """Tests :func:`core.models.MailingList.MailingList.get_absolute_list_url`."""
    result = fake_mailing_list.get_absolute_list_url()

    assert result == reverse(
        f"web:{fake_mailing_list.BASENAME}-filter-list",
    )
