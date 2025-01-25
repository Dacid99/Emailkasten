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

"""Test file for :mod:`Emailkasten.signals.delete_EMailModel`."""

import pytest
from faker import Faker

from core.models.EMailModel import EMailModel

from ..models.test_EMailModel import fixture_emailModel


@pytest.fixture(name='mock_logger', autouse=True)
def fixture_mock_logger(mocker):
    """Mocks :attr:`Emailkasten.signals.delete_EMailModel.logger` of the module."""
    return mocker.patch('Emailkasten.signals.delete_EMailModel.logger')

@pytest.mark.django_db
def test_post_delete_email_success(mocker, mock_logger, email):
    """Tests :func:`Emailkasten.signals.deleteEMailModel.post_delete_email`
    if the file removal is successful.
    """
    mock_os_remove = mocker.patch('Emailkasten.signals.delete_EMailModel.os.remove')
    email.eml_filepath = Faker().file_path(extension='eml')
    email.prerender_filepath = Faker().file_path(extension='png')
    email.save()
    eml_file_path = email.eml_filepath
    prerender_file_path = email.prerender_filepath

    email.delete()

    with pytest.raises(EMailModel.DoesNotExist):
        email.refresh_from_db()
    mock_os_remove.assert_any_call(eml_file_path)
    mock_os_remove.assert_any_call(prerender_file_path)
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()
    mock_logger.critical.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize(
    'side_effects',
    [
        [Exception, None],
        [None, Exception],
        [Exception, Exception],
    ]
)
def test_post_delete_email_failure(mocker, email, mock_logger, side_effects):
    """Tests :func:`Emailkasten.signals.deleteEMailModel.post_delete_email`
    if the file removal throws an exception.
    """
    mock_os_remove = mocker.patch('Emailkasten.signals.delete_EMailModel.os.remove', side_effect=side_effects)
    email.eml_filepath = Faker().file_path(extension='eml')
    email.prerender_filepath = Faker().file_path(extension='png')
    email.save()
    eml_file_path = email.eml_filepath
    prerender_file_path = email.prerender_filepath

    email.delete()

    with pytest.raises(EMailModel.DoesNotExist):
        email.refresh_from_db()
    mock_os_remove.assert_any_call(eml_file_path)
    mock_os_remove.assert_any_call(prerender_file_path)
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_called()
    mock_logger.critical.assert_not_called()
