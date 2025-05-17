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


"""Test module for :mod:`core.models.EmailCorrespondent`."""

import pytest
from django.db import IntegrityError
from model_bakery import baker

from core.constants import HeaderFields
from core.models.Correspondent import Correspondent
from core.models.Email import Email
from core.models.EmailCorrespondent import EmailCorrespondent


@pytest.fixture
def fake_header_name(faker):
    """Fixture providing a random correspondent header name."""
    return faker.random_element(HeaderFields.Correspondents.values)


@pytest.mark.django_db
def test_EmailCorrespondent_fields(fake_email_correspondent):
    """Tests the fields of :class:`core.models.Correspondent.Correspondent`."""

    assert fake_email_correspondent.email is not None
    assert isinstance(fake_email_correspondent.email, Email)
    assert fake_email_correspondent.correspondent is not None
    assert isinstance(fake_email_correspondent.correspondent, Correspondent)
    assert fake_email_correspondent.mention is not None
    assert any(
        fake_email_correspondent.mention == mention
        for mention in HeaderFields.Correspondents.values
    )


@pytest.mark.django_db
def test_EmailCorrespondent___str__(fake_email_correspondent):
    """Tests the string representation of :class:`core.models.EmailCorrespondent.EmailCorrespondent`."""
    assert str(fake_email_correspondent.email) in str(fake_email_correspondent)
    assert str(fake_email_correspondent.correspondent) in str(fake_email_correspondent)
    assert str(fake_email_correspondent.mention) in str(fake_email_correspondent)


@pytest.mark.django_db
def test_EmailCorrespondent_foreign_key_email_deletion(fake_email_correspondent):
    """Tests the on_delete foreign key constraint on email in :class:`core.models.EmailCorrespondent.EmailCorrespondent`."""
    fake_email_correspondent.email.delete()

    with pytest.raises(EmailCorrespondent.DoesNotExist):
        fake_email_correspondent.refresh_from_db()
    fake_email_correspondent.correspondent.refresh_from_db()
    assert fake_email_correspondent.correspondent is not None


@pytest.mark.django_db
def test_EmailCorrespondent_foreign_key_correspondent_deletion(
    fake_email_correspondent,
):
    """Tests the on_delete foreign key constraint on correspondent in :class:`core.models.EmailCorrespondent.EmailCorrespondent`."""
    fake_email_correspondent.correspondent.delete()

    with pytest.raises(EmailCorrespondent.DoesNotExist):
        fake_email_correspondent.refresh_from_db()
    fake_email_correspondent.email.refresh_from_db()
    assert fake_email_correspondent.email is not None


@pytest.mark.django_db
def test_EmailCorrespondent_unique_constraints(fake_email_correspondent):
    """Tests the unique constraint in :class:`core.models.Correspondent.Correspondent`."""
    with pytest.raises(IntegrityError):
        baker.make(
            EmailCorrespondent,
            email=fake_email_correspondent.email,
            correspondent=fake_email_correspondent.correspondent,
            mention=fake_email_correspondent.mention,
        )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "header, expected_results",
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
def test_EmailCorrespondent_create_from_header_success(
    fake_email, fake_header_name, header, expected_results
):
    """Tests :func:`core.models.EmailCorrespondent.EmailCorrespondent.create_from_header`
    in case of success.
    """
    assert EmailCorrespondent.objects.count() == 0
    assert Correspondent.objects.count() == 0

    result = EmailCorrespondent.create_from_header(header, fake_header_name, fake_email)

    assert EmailCorrespondent.objects.count() == len(expected_results)
    assert Correspondent.objects.count() == len(expected_results)
    assert isinstance(result, list)
    assert len(result) == len(expected_results)
    for item, expected_result in zip(result, expected_results, strict=True):
        assert isinstance(item, EmailCorrespondent)
        assert item.pk is not None
        assert item.correspondent.email_name == expected_result[0]
        assert item.correspondent.email_address == expected_result[1]
        assert item.email == fake_email
        assert item.mention == fake_header_name


@pytest.mark.django_db
def test_EmailCorrespondent_create_from_header_no_correspondent(
    fake_email, fake_header_name
):
    """Tests :func:`core.models.EmailCorrespondent.EmailCorrespondent.create_from_header`
    in case of the correspondent cannot be set up.
    """
    assert EmailCorrespondent.objects.count() == 0
    assert Correspondent.objects.count() == 0

    result = EmailCorrespondent.create_from_header("", fake_header_name, fake_email)

    assert result == []
    assert EmailCorrespondent.objects.count() == 0
    assert Correspondent.objects.count() == 0


@pytest.mark.django_db
def test_EmailCorrespondent_create_from_header_no_address(fake_email, fake_header_name):
    """Tests :func:`core.models.EmailCorrespondent.EmailCorrespondent.create_from_header`
    in case of the correspondent cannot be set up.
    """
    assert EmailCorrespondent.objects.count() == 0
    assert Correspondent.objects.count() == 0

    result = EmailCorrespondent.create_from_header("<>", fake_header_name, fake_email)

    assert result == []
    assert EmailCorrespondent.objects.count() == 0
    assert Correspondent.objects.count() == 0


@pytest.mark.django_db
def test_EmailCorrespondent_create_from_header_no_email(fake_header_name, faker):
    """Tests :func:`core.models.EmailCorrespondent.EmailCorrespondent.create_from_header`
    in case the email argument is not in the database.
    """
    assert EmailCorrespondent.objects.count() == 0
    assert Correspondent.objects.count() == 0

    with pytest.raises(ValueError):
        EmailCorrespondent.create_from_header(
            faker.sentence(), fake_header_name, Email()
        )

    assert EmailCorrespondent.objects.count() == 0
    assert Correspondent.objects.count() == 0
