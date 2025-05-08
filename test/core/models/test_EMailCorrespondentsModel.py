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


"""Test module for :mod:`core.models.EMailCorrespondentsModel`."""

import pytest
from django.db import IntegrityError
from model_bakery import baker

from core.constants import HeaderFields
from core.models.CorrespondentModel import CorrespondentModel
from core.models.EMailCorrespondentsModel import EMailCorrespondentsModel
from core.models.EMailModel import EMailModel


@pytest.fixture
def fake_header_name(faker):
    """Fixture providing a random correspondent header name."""
    return faker.random_element(HeaderFields.Correspondents.values)


@pytest.mark.django_db
def test_EMailCorrespondentsModel_fields(emailCorrespondentModel):
    """Tests the fields of :class:`core.models.CorrespondentModel.CorrespondentModel`."""

    assert emailCorrespondentModel.email is not None
    assert isinstance(emailCorrespondentModel.email, EMailModel)
    assert emailCorrespondentModel.correspondent is not None
    assert isinstance(emailCorrespondentModel.correspondent, CorrespondentModel)
    assert emailCorrespondentModel.mention is not None
    assert any(
        emailCorrespondentModel.mention == mention
        for mention in HeaderFields.Correspondents.values
    )


@pytest.mark.django_db
def test_EMailCorrespondentsModel___str__(emailCorrespondentModel):
    """Tests the string representation of :class:`core.models.EMailCorrespondentsModel.EMailCorrespondentsModel`."""
    assert str(emailCorrespondentModel.email) in str(emailCorrespondentModel)
    assert str(emailCorrespondentModel.correspondent) in str(emailCorrespondentModel)
    assert str(emailCorrespondentModel.mention) in str(emailCorrespondentModel)


@pytest.mark.django_db
def test_EMailCorrespondentsModel_foreign_key_email_deletion(emailCorrespondentModel):
    """Tests the on_delete foreign key constraint on email in :class:`core.models.EMailCorrespondentsModel.EMailCorrespondentsModel`."""
    emailCorrespondentModel.email.delete()

    with pytest.raises(EMailCorrespondentsModel.DoesNotExist):
        emailCorrespondentModel.refresh_from_db()
    emailCorrespondentModel.correspondent.refresh_from_db()
    assert emailCorrespondentModel.correspondent is not None


@pytest.mark.django_db
def test_EMailCorrespondentsModel_foreign_key_correspondent_deletion(
    emailCorrespondentModel,
):
    """Tests the on_delete foreign key constraint on correspondent in :class:`core.models.EMailCorrespondentsModel.EMailCorrespondentsModel`."""
    emailCorrespondentModel.correspondent.delete()

    with pytest.raises(EMailCorrespondentsModel.DoesNotExist):
        emailCorrespondentModel.refresh_from_db()
    emailCorrespondentModel.email.refresh_from_db()
    assert emailCorrespondentModel.email is not None


@pytest.mark.django_db
def test_EMailCorrespondentsModel_unique_constraints(emailCorrespondentModel):
    """Tests the unique constraint in :class:`core.models.CorrespondentModel.CorrespondentModel`."""
    with pytest.raises(IntegrityError):
        baker.make(
            EMailCorrespondentsModel,
            email=emailCorrespondentModel.email,
            correspondent=emailCorrespondentModel.correspondent,
            mention=emailCorrespondentModel.mention,
        )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "header, expectedResults",
    [
        ("test <test@test.org>", [("test", "test@test.org")]),
        ("someone@somedomain.us", [("", "someone@somedomain.us")]),
        ("<the@dude.eu>", [("", "the@dude.eu")]),
        ("abc<alpha@beta.de>", [("abc", "alpha@beta.de")]),
        (
            "one <one@eins.de>, two <two@due.it>",
            [("one", "one@eins.de"), ("two", "two@due.it")],
        ),
        ("a <addr@sub.dom.tld>", [("a", "addr@sub.dom.tld")]),
    ],
)
def test_EMailCorrespondentsModel_createFromHeader_success(
    emailModel, fake_header_name, header, expectedResults
):
    """Tests :func:`core.models.EMailCorrespondentsModel.EMailCorrespondentsModel.createFromHeader`
    in case of success.
    """
    assert EMailCorrespondentsModel.objects.count() == 0
    assert CorrespondentModel.objects.count() == 0

    result = EMailCorrespondentsModel.createFromHeader(
        header, fake_header_name, emailModel
    )

    assert EMailCorrespondentsModel.objects.count() == len(expectedResults)
    assert CorrespondentModel.objects.count() == len(expectedResults)
    assert isinstance(result, list)
    assert len(result) == len(expectedResults)
    for item, expectedResult in zip(result, expectedResults, strict=True):
        assert isinstance(item, EMailCorrespondentsModel)
        assert item.pk is not None
        assert item.correspondent.email_name == expectedResult[0]
        assert item.correspondent.email_address == expectedResult[1]
        assert item.email == emailModel
        assert item.mention == fake_header_name


@pytest.mark.django_db
def test_EMailCorrespondentsModel_createFromHeader_no_correspondent(
    emailModel, fake_header_name
):
    """Tests :func:`core.models.EMailCorrespondentsModel.EMailCorrespondentsModel.createFromHeader`
    in case of the correspondent cannot be set up.
    """
    assert EMailCorrespondentsModel.objects.count() == 0
    assert CorrespondentModel.objects.count() == 0

    result = EMailCorrespondentsModel.createFromHeader("", fake_header_name, emailModel)

    assert result == []
    assert EMailCorrespondentsModel.objects.count() == 0
    assert CorrespondentModel.objects.count() == 0


@pytest.mark.django_db
def test_EMailCorrespondentsModel_createFromHeader_no_address(
    emailModel, fake_header_name
):
    """Tests :func:`core.models.EMailCorrespondentsModel.EMailCorrespondentsModel.createFromHeader`
    in case of the correspondent cannot be set up.
    """
    assert EMailCorrespondentsModel.objects.count() == 0
    assert CorrespondentModel.objects.count() == 0

    result = EMailCorrespondentsModel.createFromHeader(
        "<>", fake_header_name, emailModel
    )

    assert result == []
    assert EMailCorrespondentsModel.objects.count() == 0
    assert CorrespondentModel.objects.count() == 0


@pytest.mark.django_db
def test_EMailCorrespondentsModel_createFromHeader_no_email(fake_header_name, faker):
    """Tests :func:`core.models.EMailCorrespondentsModel.EMailCorrespondentsModel.createFromHeader`
    in case the email argument is not in the database.
    """
    assert EMailCorrespondentsModel.objects.count() == 0
    assert CorrespondentModel.objects.count() == 0

    with pytest.raises(ValueError):
        EMailCorrespondentsModel.createFromHeader(
            faker.sentence(), fake_header_name, EMailModel()
        )

    assert EMailCorrespondentsModel.objects.count() == 0
    assert CorrespondentModel.objects.count() == 0
