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
from model_bakery import baker

from .conftest import TEXT_TEST_ITEMS, TEXT_TEST_PARAMETERS, INT_TEST_ITEMS, INT_TEST_PARAMETERS, BOOL_TEST_ITEMS, BOOL_TEST_PARAMETERS
from Emailkasten.Filters.AttachmentFilter import AttachmentFilter
from Emailkasten.Models.AttachmentModel import AttachmentModel


@pytest.fixture(name='queryset')
def fixture_queryset():
    for number in range(0,3):
        baker.make(
            AttachmentModel,
            file_path='/path/' + TEXT_TEST_ITEMS[number],
            file_name=TEXT_TEST_ITEMS[number],
            datasize=INT_TEST_ITEMS[number],
            is_favorite=BOOL_TEST_ITEMS[number]
        )

    return AttachmentModel.objects.all()


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_count', TEXT_TEST_PARAMETERS
)
def test_file_name_filter(queryset, lookup_expr, filterquery, expected_count):
    filter = {'file_name'+lookup_expr: filterquery}

    filtered_data = AttachmentFilter(filter, queryset=queryset).qs

    assert filtered_data.count() == expected_count


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_count', INT_TEST_PARAMETERS
)
def test_datasize_filter(queryset, lookup_expr, filterquery, expected_count):
    filter = {'datasize'+lookup_expr: filterquery}

    filtered_data = AttachmentFilter(filter, queryset=queryset).qs

    assert filtered_data.count() == expected_count


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_count', BOOL_TEST_PARAMETERS
)
def test_is_favorite_filter(queryset, lookup_expr, filterquery, expected_count):
    filter = {'is_favorite'+lookup_expr: filterquery}

    filtered_data = AttachmentFilter(filter, queryset=queryset).qs

    assert filtered_data.count() == expected_count
