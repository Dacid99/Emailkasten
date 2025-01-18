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

import datetime

import pytest
from freezegun import freeze_time
from model_bakery import baker

from Emailkasten.Filters.EMailFilter import EMailFilter
from Emailkasten.Models.EMailModel import EMailModel

from .conftest import (BOOL_TEST_ITEMS, BOOL_TEST_PARAMETERS,
                       DATETIME_TEST_ITEMS, DATETIME_TEST_PARAMETERS,
                       INT_TEST_ITEMS, INT_TEST_PARAMETERS, TEXT_TEST_ITEMS,
                       TEXT_TEST_PARAMETERS)
from .test_AccountFilter import fixture_account_queryset
from .test_CorrespondentFilter import fixture_correspondent_queryset
from .test_MailingListFilter import fixture_mailinglist_queryset


@pytest.fixture(name='email_queryset')
def fixture_email_queryset(account_queryset, mailinglist_queryset):
    for number in range(0,len(TEXT_TEST_ITEMS)):
        with freeze_time(DATETIME_TEST_ITEMS[number]):
            baker.make(
                EMailModel,
                message_id=TEXT_TEST_ITEMS[number],
                datetime=datetime.datetime.now(tz=datetime.UTC),
                email_subject=TEXT_TEST_ITEMS[number],
                bodytext=TEXT_TEST_ITEMS[number],
                datasize=INT_TEST_ITEMS[number],
                is_favorite=BOOL_TEST_ITEMS[number],
                account=account_queryset.get(id=number+1),
                mailinglist=mailinglist_queryset.get(id=number+1),
                comments = TEXT_TEST_ITEMS[number],
                keywords = TEXT_TEST_ITEMS[number],
                importance = TEXT_TEST_ITEMS[number],
                priority = TEXT_TEST_ITEMS[number],
                precedence = TEXT_TEST_ITEMS[number],
                received = TEXT_TEST_ITEMS[number],
                user_agent = TEXT_TEST_ITEMS[number],
                auto_submitted = TEXT_TEST_ITEMS[number],
                content_type = TEXT_TEST_ITEMS[number],
                content_language = TEXT_TEST_ITEMS[number],
                content_location = TEXT_TEST_ITEMS[number],
                x_priority = TEXT_TEST_ITEMS[number],
                x_originated_client = TEXT_TEST_ITEMS[number],
                x_spam = TEXT_TEST_ITEMS[number]
            )

    return EMailModel.objects.all()


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_message_id_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'message_id'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', DATETIME_TEST_PARAMETERS
)
def test_datetime_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'datetime'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_email_subject_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'email_subject'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_bodytext_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'bodytext'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', INT_TEST_PARAMETERS
)
def test_datasize_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'datasize'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', BOOL_TEST_PARAMETERS
)
def test_is_favorite_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'is_favorite'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_comments_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'comments'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_keywords_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'keywords'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_importance_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'importance'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_priority_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'priority'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_precedence_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'precedence'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_received_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'received'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_user_agent_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'user_agent'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_auto_submitted_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'auto_submitted'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_content_type_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'content_type'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_content_language_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'content_language'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_content_location_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'content_location'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_x_priority_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'x_priority'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_x_originated_client_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'x_originated_client'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_x_spam_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'x_spam'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', DATETIME_TEST_PARAMETERS
)
def test_created_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'created'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', DATETIME_TEST_PARAMETERS
)
def test_updated_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'updated'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_account__mail_address_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'account__mail_address'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_account__mail_host_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'account__mail_host'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_mailinglist__list_id_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'mailinglist__list_id'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices


@pytest.mark.django_db
@pytest.mark.parametrize(
    'lookup_expr, filterquery, expected_indices', TEXT_TEST_PARAMETERS
)
def test_mailinglist__list_owner_filter(email_queryset, lookup_expr, filterquery, expected_indices):
    filter = {'mailinglist__list_owner'+lookup_expr: filterquery}

    filtered_data = EMailFilter(filter, queryset=email_queryset).qs

    assert filtered_data.distinct().count() == filtered_data.count()
    assert filtered_data.count() == len(expected_indices)
    for data in filtered_data:
        assert data.id - 1 in expected_indices
