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

from Emailkasten.Filters.CorrespondentFilter import CorrespondentFilter
from Emailkasten.Models.CorrespondentModel import CorrespondentModel

from .conftest import (BOOL_TEST_ITEMS, BOOL_TEST_PARAMETERS,
                       DATETIME_TEST_ITEMS, DATETIME_TEST_PARAMETERS,
                       TEXT_TEST_ITEMS, TEXT_TEST_PARAMETERS)


@pytest.fixture(name='correspondent_queryset')
def fixture_correspondent_queryset():
    for number in range(0,len(TEXT_TEST_ITEMS)):
        with freeze_time(DATETIME_TEST_ITEMS[number]):
            baker.make(
                CorrespondentModel,
                email_name=TEXT_TEST_ITEMS[number],
                email_address=TEXT_TEST_ITEMS[number],
                is_favorite=BOOL_TEST_ITEMS[number]
            )

    return CorrespondentModel.objects.all()


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_email_name_filter(correspondent_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'email_name'+lookup_expr: filterquery}

    filtered_data = CorrespondentFilter(filter, queryset=correspondent_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_email_address_filter(correspondent_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'email_address'+lookup_expr: filterquery}

    filtered_data = CorrespondentFilter(filter, queryset=correspondent_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', BOOL_TEST_PARAMETERS
)
def test_is_favorite_filter(correspondent_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'is_favorite'+lookup_expr: filterquery}

    filtered_data = CorrespondentFilter(filter, queryset=correspondent_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', DATETIME_TEST_PARAMETERS
)
def test_created_filter(correspondent_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'created' + lookup_expr: filterquery}

    filtered_data = CorrespondentFilter(filter, queryset=correspondent_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', DATETIME_TEST_PARAMETERS
)
def test_updated_filter(correspondent_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'updated' + lookup_expr: filterquery}

    filtered_data = CorrespondentFilter(filter, queryset=correspondent_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices
