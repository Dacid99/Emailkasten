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

"""Test module for :mod:`core.models.CorrespondentModel`."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import pytest
from django.db import IntegrityError
from django.urls import reverse
from model_bakery import baker

from core.models.CorrespondentModel import CorrespondentModel


if TYPE_CHECKING:
    from unittest.mock import MagicMock


@pytest.fixture
def fake_correspondentTuple(faker):
    return (faker.name(), faker.email())


@pytest.fixture(autouse=True)
def mock_logger(mocker) -> MagicMock:
    """Mocks the :attr:`core.models.CorrespondentModel.logger`.

    Returns:
        The mocked logger instance.
    """
    return mocker.patch("core.models.CorrespondentModel.logger", autospec=True)


@pytest.mark.django_db
def test_CorrespondentModel_fields(correspondentModel):
    """Tests the fields of :class:`core.models.CorrespondentModel.CorrespondentModel`."""

    assert correspondentModel.email_name is not None
    assert isinstance(correspondentModel.email_name, str)
    assert correspondentModel.email_address is not None
    assert isinstance(correspondentModel.email_address, str)
    assert correspondentModel.is_favorite is False
    assert correspondentModel.updated is not None
    assert isinstance(correspondentModel.updated, datetime.datetime)
    assert correspondentModel.created is not None
    assert isinstance(correspondentModel.created, datetime.datetime)


@pytest.mark.django_db
def test_CorrespondentModel___str__(correspondentModel):
    """Tests the string representation of :class:`core.models.CorrespondentModel.CorrespondentModel`."""
    assert correspondentModel.email_address in str(correspondentModel)


@pytest.mark.django_db
def test_CorrespondentModel_unique_constraints(correspondentModel):
    """Tests the unique constraint in :class:`core.models.CorrespondentModel.CorrespondentModel`."""

    with pytest.raises(IntegrityError):
        baker.make(
            CorrespondentModel,
            email_name=correspondentModel.email_name,
            email_address=correspondentModel.email_address,
        )


@pytest.mark.django_db
def test_CorrespondentModel_createFromCorrespondentTuple_success(
    fake_correspondentTuple,
):
    """Tests :func:`core.models.CorrespondentModel.CorrespondentModel.createFromCorrespondentTuple`
    in case of success.
    """
    assert CorrespondentModel.objects.count() == 0

    result = CorrespondentModel.createFromCorrespondentTuple(fake_correspondentTuple)

    assert isinstance(result, CorrespondentModel)
    assert result.pk is not None
    assert CorrespondentModel.objects.count() == 1
    assert result.email_name == fake_correspondentTuple[0]
    assert result.email_address == fake_correspondentTuple[1]


@pytest.mark.django_db
def test_CorrespondentModel_createFromCorrespondentTuple_duplicate(
    correspondentModel, fake_correspondentTuple
):
    """Tests :func:`core.models.CorrespondentModel.CorrespondentModel.createFromCorrespondentTuple`
    in case the correspondent to be prepared is already being in the database.
    """
    fake_correspondentTuple = (
        fake_correspondentTuple[0],
        correspondentModel.email_address,
    )

    assert CorrespondentModel.objects.count() == 1

    result = CorrespondentModel.createFromCorrespondentTuple(fake_correspondentTuple)

    assert result == correspondentModel
    assert CorrespondentModel.objects.count() == 1


@pytest.mark.django_db
def test_CorrespondentModel_createFromCorrespondentTuple_no_address(
    mock_logger, fake_correspondentTuple
):
    """Tests :func:`core.models.CorrespondentModel.CorrespondentModel.createFromCorrespondentTuple`
    in case of there is no address in the header.
    """
    fake_correspondentTuple = (fake_correspondentTuple[0], "")

    assert CorrespondentModel.objects.count() == 0

    result = CorrespondentModel.createFromCorrespondentTuple(fake_correspondentTuple)

    assert result is None
    assert CorrespondentModel.objects.count() == 0
    mock_logger.debug.assert_called()


@pytest.mark.django_db
def test_CorrespondentModel_get_absolute_url(correspondentModel):
    """Tests :func:`core.models.CorrespondentModel.CorrespondentModel.get_absolute_url`."""
    result = correspondentModel.get_absolute_url()

    assert result == reverse(
        f"web:{correspondentModel.BASENAME}-detail",
        kwargs={"pk": correspondentModel.pk},
    )


@pytest.mark.django_db
def test_CorrespondentModel_get_absolute_edit_url(correspondentModel):
    """Tests :func:`core.models.CorrespondentModel.CorrespondentModel.get_absolute_edit_url`."""
    result = correspondentModel.get_absolute_edit_url()

    assert result == reverse(
        f"web:{correspondentModel.BASENAME}-edit",
        kwargs={"pk": correspondentModel.pk},
    )


@pytest.mark.django_db
def test_CorrespondentModel_get_absolute_list_url(correspondentModel):
    """Tests :func:`core.models.CorrespondentModel.CorrespondentModel.get_absolute_list_url`."""
    result = correspondentModel.get_absolute_list_url()

    assert result == reverse(
        f"web:{correspondentModel.BASENAME}-filter-list",
    )
