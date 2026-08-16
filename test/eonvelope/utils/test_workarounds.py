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

"""Test file for the :mod:`eonvelope.utils` module."""

import logging

import pytest

from eonvelope.utils.workarounds import get_config


@pytest.fixture
def mock_getattr(mocker):
    """Fixture mocking `getattr` to mock accessing constance values."""
    return mocker.patch("eonvelope.utils.workarounds.getattr")


def test_get_config__success(monkeypatch, faker, caplog_all, mock_getattr):
    """Tests getting a constance value in case of success."""
    fake_config_default = faker.word()
    monkeypatch.setattr(
        "eonvelope.utils.workarounds.CONSTANCE_CONFIG",
        {"TEST_CONFIG": (fake_config_default, "A test value", str)},
    )
    fake_config = faker.word()
    mock_getattr.return_value = fake_config

    config_value = get_config("TEST_CONFIG")

    mock_getattr.assert_called_once()
    assert config_value == fake_config
    assert not any(record.levelno == logging.DEBUG for record in caplog_all.records)
    assert not any(record.levelno == logging.INFO for record in caplog_all.records)
    assert not any(record.levelno == logging.ERROR for record in caplog_all.records)
    assert not any(record.levelno == logging.CRITICAL for record in caplog_all.records)


def test_get_config_workaround__success(monkeypatch, faker, caplog_all, mock_getattr):
    """Tests getting a constance value in case of success via the workaround."""
    fake_config_default = faker.word()
    monkeypatch.setattr(
        "eonvelope.utils.workarounds.CONSTANCE_CONFIG",
        {"TEST_CONFIG": (fake_config_default, "A test value", str)},
    )
    mock_getattr.side_effect = Exception

    config_value = get_config("TEST_CONFIG")

    mock_getattr.assert_called_once()
    assert config_value == fake_config_default

    assert any(record.levelno == logging.DEBUG for record in caplog_all.records)
    assert not any(record.levelno == logging.INFO for record in caplog_all.records)
    assert not any(record.levelno == logging.ERROR for record in caplog_all.records)
    assert not any(record.levelno == logging.CRITICAL for record in caplog_all.records)


def test_get_config_workaround__failure(monkeypatch, faker, caplog_all, mock_getattr):
    """Tests getting a constance value in case of failure."""
    fake_config_default = faker.word()
    monkeypatch.setattr(
        "eonvelope.utils.workarounds.CONSTANCE_CONFIG",
        {"TEST_CONFIG": (fake_config_default, "A test value", str)},
    )
    mock_getattr.side_effect = ValueError("Constance value not found")

    with pytest.raises(KeyError):
        get_config("NO_CONFIG")

    mock_getattr.assert_called_once()
    assert any(record.levelno == logging.DEBUG for record in caplog_all.records)
    assert any(record.levelno == logging.CRITICAL for record in caplog_all.records)
    assert not any(record.levelno == logging.INFO for record in caplog_all.records)
    assert not any(record.levelno == logging.ERROR for record in caplog_all.records)
