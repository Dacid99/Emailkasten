# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Eonvelope - a open-source self-hostable email archiving server
# Copyright (C) 2024 David Aderbauer & The Eonvelope Contributors
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

"""Test module for :mod:`core.signals.save_Account`."""

import logging

import pytest
from django.contrib.auth import get_user_model


@pytest.mark.django_db
def test_User_post_save_created(faker, caplog_all):
    """Tests the post_save function of :class:`django.contrib.auth.models.User`
    in case the user is newly created.
    """
    new_user = get_user_model().objects.create(
        username=faker.name(), password=faker.password()
    )

    assert hasattr(new_user, "profile")
    assert any(record.levelno == logging.DEBUG for record in caplog_all.records)


@pytest.mark.django_db
def test_User_post_save_exists(owner_user, caplog_all):
    """Tests the post_save function of :class:`django.contrib.auth.models.User`.
    in case the user already exists.
    """
    assert hasattr(owner_user, "profile")
    caplog_all.clear()

    owner_user.save()

    assert hasattr(owner_user, "profile")
    assert not caplog_all.records
