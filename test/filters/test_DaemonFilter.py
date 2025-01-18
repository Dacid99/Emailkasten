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
from faker import Faker

from Emailkasten.Filters.DaemonFilter import DaemonFilter
from Emailkasten.Models.DaemonModel import DaemonModel

from .conftest import (BOOL_TEST_ITEMS, BOOL_TEST_PARAMETERS,
                       DATETIME_TEST_ITEMS, DATETIME_TEST_PARAMETERS,
                       INT_TEST_ITEMS, INT_TEST_PARAMETERS)
from .test_MailboxFilter import fixture_mailbox_queryset
from .test_AccountFilter import fixture_account_queryset


@pytest.fixture(name='daemon_queryset')
def fixture_daemon_queryset(mailbox_queryset):
    for number in range(0,len(INT_TEST_ITEMS)):
        with freeze_time(DATETIME_TEST_ITEMS[number]):
            baker.make(
                DaemonModel,
                cycle_interval=INT_TEST_ITEMS[number],
                is_running=BOOL_TEST_ITEMS[number],
                is_healthy=BOOL_TEST_ITEMS[number],
                mailbox=mailbox_queryset.get(id=number+1),
                log_filepath=Faker().file_path()
            )

    return DaemonModel.objects.all()


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', INT_TEST_PARAMETERS
)
def test_cycle_interval_filter(daemon_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'cycle_interval'+lookup_expr: filterquery}

    filtered_data = DaemonFilter(filter, queryset=daemon_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', BOOL_TEST_PARAMETERS
)
def test_is_healthy_filter(daemon_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'is_healthy'+lookup_expr: filterquery}

    filtered_data = DaemonFilter(filter, queryset=daemon_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', BOOL_TEST_PARAMETERS
)
def test_is_running_filter(daemon_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'is_running'+lookup_expr: filterquery}

    filtered_data = DaemonFilter(filter, queryset=daemon_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', DATETIME_TEST_PARAMETERS
)
def test_created_filter(daemon_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'created' + lookup_expr: filterquery}

    filtered_data = DaemonFilter(filter, queryset=daemon_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', DATETIME_TEST_PARAMETERS
)
def test_updated_filter(daemon_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'updated' + lookup_expr: filterquery}

    filtered_data = DaemonFilter(filter, queryset=daemon_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', BOOL_TEST_PARAMETERS
)
def test_mailbox__is_healthy_filter(daemon_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'mailbox__is_healthy' + lookup_expr: filterquery}

    filtered_data = DaemonFilter(filter, queryset=daemon_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices
