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
from freezegun import freeze_time
from model_bakery import baker

from Emailkasten.Filters.MailboxFilter import MailboxFilter
from Emailkasten.Models.MailboxModel import MailboxModel

from .conftest import (BOOL_TEST_ITEMS, BOOL_TEST_PARAMETERS,
                       DATETIME_TEST_ITEMS, DATETIME_TEST_PARAMETERS,
                       TEXT_TEST_ITEMS, TEXT_TEST_PARAMETERS)
from .test_AccountFilter import fixture_account_queryset


@pytest.fixture(name='mailbox_queryset')
def fixture_mailbox_queryset(account_queryset):
    for number in range(0,len(TEXT_TEST_ITEMS)):
        with freeze_time(DATETIME_TEST_ITEMS[number]):
            baker.make(
                MailboxModel,
                name=TEXT_TEST_ITEMS[number],
                save_toEML=BOOL_TEST_ITEMS[number],
                save_attachments=BOOL_TEST_ITEMS[number],
                save_images=BOOL_TEST_ITEMS[number],
                is_favorite=BOOL_TEST_ITEMS[number],
                is_healthy=BOOL_TEST_ITEMS[number],
                account=account_queryset.get(id=number+1)
            )

    return MailboxModel.objects.all()


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_name_filter(mailbox_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'name'+lookup_expr: filterquery}

    filtered_data = MailboxFilter(filter, queryset=mailbox_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', BOOL_TEST_PARAMETERS
)
def test_save_toEML_filter(mailbox_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'save_toEML'+lookup_expr: filterquery}

    filtered_data = MailboxFilter(filter, queryset=mailbox_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', BOOL_TEST_PARAMETERS
)
def test_save_attachments_filter(mailbox_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'save_attachments'+lookup_expr: filterquery}

    filtered_data = MailboxFilter(filter, queryset=mailbox_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', BOOL_TEST_PARAMETERS
)
def test_save_images_filter(mailbox_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'save_images'+lookup_expr: filterquery}

    filtered_data = MailboxFilter(filter, queryset=mailbox_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', BOOL_TEST_PARAMETERS
)
def test_is_healthy_filter(mailbox_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'is_healthy'+lookup_expr: filterquery}

    filtered_data = MailboxFilter(filter, queryset=mailbox_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', BOOL_TEST_PARAMETERS
)
def test_is_favorite_filter(mailbox_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'is_favorite'+lookup_expr: filterquery}

    filtered_data = MailboxFilter(filter, queryset=mailbox_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', DATETIME_TEST_PARAMETERS
)
def test_created_filter(mailbox_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'created' + lookup_expr: filterquery}

    filtered_data = MailboxFilter(filter, queryset=mailbox_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', DATETIME_TEST_PARAMETERS
)
def test_updated_filter(mailbox_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'updated' + lookup_expr: filterquery}

    filtered_data = MailboxFilter(filter, queryset=mailbox_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_account__mail_address_filter(mailbox_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'account__mail_address'+lookup_expr: filterquery}

    filtered_data = MailboxFilter(filter, queryset=mailbox_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_account__mail_host_filter(mailbox_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'account__mail_host'+lookup_expr: filterquery}

    filtered_data = MailboxFilter(filter, queryset=mailbox_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', BOOL_TEST_PARAMETERS
)
def test_account__is_healthy_filter(mailbox_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'account__is_healthy' + lookup_expr: filterquery}

    filtered_data = MailboxFilter(filter, queryset=mailbox_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices
