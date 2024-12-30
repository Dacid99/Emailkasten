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

"""Test module for :mod:`Emailkasten.Views.AccountViewSet`.

Fixtures:
    :func:`fixture_accountModel`: Creates an account owned by `owner_user`.
    :func:`fixture_daemonModel`: Creates an mailbox in `accountModel`.
    :func:`fixture_mailboxPayload`: Creates clean :class:`Emailkasten.Models.DaemonModel.DaemonModel` payload for a post or put request.
    :func:`fixture_list_url`: Gets the viewsets url for list actions.
    :func:`fixture_detail_url`: Gets the viewsets url for detail actions.
    :func:`fixture_custom_detail_list_url`: Gets the viewsets url for custom list actions.
    :func:`fixture_custom_detail_action_url`: Gets the viewsets url for custom detail actions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from django.forms.models import model_to_dict
from django.urls import reverse
from faker import Faker
from model_bakery import baker
from rest_framework import status

import Emailkasten.Views.DaemonViewSet
from Emailkasten.Models.AccountModel import AccountModel
from Emailkasten.Models.DaemonModel import DaemonModel, MailboxModel
from Emailkasten.Models.EMailModel import EMailModel
from Emailkasten.Views.DaemonViewSet import DaemonViewSet

if TYPE_CHECKING:
    from typing import Any, Callable


@pytest.fixture(name='accountModel')
def fixture_accountModel(owner_user) -> AccountModel:
    """Creates an :class:`Emailkasten.Models.AccountModel.AccountModel` owned by :attr:`owner_user`.

    Args:
        owner_user: Depends on :func:`fixture_owner_user`.

    Returns:
        The account instance for testing.
    """
    return baker.make(AccountModel, user = owner_user)

@pytest.fixture(name='mailboxModel')
def fixture_mailboxModel(accountModel) -> MailboxModel:
    """Creates an :class:`Emailkasten.Models.MailboxModel.MailboxModel` owned by :attr:`owner_user`.

    Args:
        accountModel: Depends on :func:`fixture_accountModel`.

    Returns:
        The mailbox instance for testing.
    """
    return baker.make(DaemonModel, account=accountModel)

@pytest.fixture(name='daemonModel')
def fixture_daemonModel(mailboxModel) -> DaemonModel:
    """Creates an :class:`Emailkasten.Models.DaemonModel.DaemonModel` owned by :attr:`owner_user`.

    Args:
        mailboxModel: Depends on :func:`fixture_mailboxModel`.

    Returns:
        The daemon instance for testing.
    """
    return baker.make(DaemonModel, mailbox=mailboxModel, log_filepath=Faker().file_path(extension='log'))

@pytest.fixture(name='daemonPayload')
def fixture_daemonPayload(mailboxModel) -> dict[str, Any]:
    """Creates clean :class:`Emailkasten.Models.DaemonModel.DaemonModel` payload for a post or put request.

    Args:
        mailboxModel: Depends on :func:`fixture_mailboxModel`.

    Returns:
        The clean payload.
    """
    mailboxData = baker.prepare(DaemonModel, mailbox=mailboxModel, log_filepath=Faker().file_path(extension='log'))
    payload = model_to_dict(mailboxData)
    payload.pop('id')
    cleanPayload = {key: value for key, value in payload.items() if value is not None}
    return cleanPayload

@pytest.fixture(name='list_url')
def fixture_list_url() -> str:
    """Gets the viewsets url for list actions.

    Returns:
        The list url.
    """
    return reverse(f'{DaemonViewSet.BASENAME}-list')

@pytest.fixture(name='detail_url')
def fixture_detail_url(daemonModel) -> str:
    """Gets the viewsets url for detail actions.

    Args:
        daemonModel: Depends on :func:`fixture_daemonModel`.

    Returns:
        The detail url."""
    return reverse(f'{DaemonViewSet.BASENAME}-detail', args=[daemonModel.id])

@pytest.fixture(name='custom_list_action_url')
def fixture_custom_list_action_url() -> Callable[[str],str]:
    """Gets the viewsets url for custom list actions.

    Returns:
        A callable that gets the list url of the viewset from the custom action name.
    """
    return lambda custom_list_action_url_name: reverse(f'{DaemonViewSet.BASENAME}-{custom_list_action_url_name}')

@pytest.fixture(name='custom_detail_action_url')
def fixture_custom_detail_action_url(daemonModel)-> Callable[[str],str]:
    """Gets the viewsets url for custom detail actions.

    Args:
        daemonModel: Depends on :func:`fixture_daemonModel`.

    Returns:
        A callable that gets the detail url of the viewset from the custom action name.
    """
    return lambda custom_detail_action_url_name: reverse(f'{DaemonViewSet.BASENAME}-{custom_detail_action_url_name}', args=[daemonModel.id])


@pytest.mark.django_db
def test_list_noauth(daemonModel, noauth_apiClient, list_url):
    """Tests the list method with an unauthenticated user client."""
    response = noauth_apiClient.get(list_url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['results']


@pytest.mark.django_db
def test_list_auth_other(daemonModel, other_apiClient, list_url):
    """Tests the list method with the authenticated other user client."""
    response = other_apiClient.get(list_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 0
    assert response.data['results'] == []


@pytest.mark.django_db
def test_list_auth_owner(daemonModel, owner_apiClient, list_url):
    """Tests the list method with the authenticated owner user client."""
    response = owner_apiClient.get(list_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1
    assert len(response.data['results']) == 1


@pytest.mark.django_db
def test_get_noauth(daemonModel, noauth_apiClient, detail_url):
    """Tests the get method with an unauthenticated user client."""
    response = noauth_apiClient.get(detail_url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['name']


@pytest.mark.django_db
def test_get_auth_other(daemonModel, other_apiClient, detail_url):
    """Tests the get method with the authenticated other user client."""
    response = other_apiClient.get(detail_url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get_auth_owner(daemonModel, owner_apiClient, detail_url):
    """Tests the list method with the authenticated owner user client."""
    response = owner_apiClient.get(detail_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['name'] == daemonModel.name


@pytest.mark.django_db
def test_patch_noauth(daemonModel, noauth_apiClient, detail_url):
    """Tests the patch method with an unauthenticated user client."""
    response = noauth_apiClient.patch(detail_url, data={'save_attachments': False})

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['save_attachments']
    daemonModel.refresh_from_db()
    assert daemonModel.save_attachments is True

@pytest.mark.django_db
def test_patch_auth_other(daemonModel, other_apiClient, detail_url):
    """Tests the patch method with the authenticated other user client."""
    response = other_apiClient.patch(detail_url, data={'save_attachments': False})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    with pytest.raises(KeyError):
        response.data['save_attachments']
    daemonModel.refresh_from_db()
    assert daemonModel.save_attachments is True


@pytest.mark.django_db
def test_patch_auth_owner(daemonModel, owner_apiClient, detail_url):
    """Tests the patch method with the authenticated owner user client."""
    response = owner_apiClient.patch(detail_url, data={'save_attachments': False})

    assert response.status_code == status.HTTP_200_OK
    assert response.data['save_attachments'] is False
    daemonModel.refresh_from_db()
    assert daemonModel.save_attachments is False


@pytest.mark.django_db
def test_put_noauth(daemonModel, noauth_apiClient, mailboxPayload, detail_url):
    """Tests the put method with an unauthenticated user client."""
    response = noauth_apiClient.put(detail_url, data=mailboxPayload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['save_attachments']
    daemonModel.refresh_from_db()
    assert daemonModel.save_attachments != mailboxPayload['save_attachments']


@pytest.mark.django_db
def test_put_auth_other(daemonModel, other_apiClient, mailboxPayload, detail_url):
    """Tests the put method with the authenticated other user client."""
    response = other_apiClient.put(detail_url, data=mailboxPayload)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    with pytest.raises(KeyError):
        response.data['save_attachments']
    daemonModel.refresh_from_db()
    assert daemonModel.save_attachments != mailboxPayload['save_attachments']


@pytest.mark.django_db
def test_put_auth_owner(daemonModel, owner_apiClient, mailboxPayload, detail_url):
    """Tests the put method with the authenticated owner user client."""
    response = owner_apiClient.put(detail_url, data=mailboxPayload)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['save_attachments'] == mailboxPayload['save_attachments']
    daemonModel.refresh_from_db()
    assert daemonModel.save_attachments == mailboxPayload['save_attachments']


@pytest.mark.django_db
def test_post_noauth(noauth_apiClient, mailboxPayload, list_url):
    """Tests the post method with an unauthenticated user client."""
    response = noauth_apiClient.post(list_url, data=mailboxPayload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['save_attachments']
    with pytest.raises(DaemonModel.DoesNotExist):
        MailboxModel.objects.get(save_attachments = mailboxPayload['save_attachments'])


@pytest.mark.django_db
def test_post_auth_other(other_apiClient, mailboxPayload, list_url):
    """Tests the post method with the authenticated other user client."""
    response = other_apiClient.post(list_url, data=mailboxPayload)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data['save_attachments']
    with pytest.raises(DaemonModel.DoesNotExist):
        MailboxModel.objects.get(save_attachments = mailboxPayload['save_attachments'])


@pytest.mark.django_db
def test_post_auth_owner(owner_apiClient, mailboxPayload, list_url):
    """Tests the post method with the authenticated owner user client."""
    response = owner_apiClient.post(list_url, data=mailboxPayload)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data['save_attachments']
    with pytest.raises(DaemonModel.DoesNotExist):
        MailboxModel.objects.get(save_attachments = mailboxPayload['save_attachments'])


@pytest.mark.django_db
def test_delete_noauth(daemonModel, noauth_apiClient, detail_url):
    """Tests the delete method with an unauthenticated user client."""
    response = noauth_apiClient.delete(detail_url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    daemonModel.refresh_from_db()
    assert daemonModel.name is not None


@pytest.mark.django_db
def test_delete_auth_other(daemonModel, other_apiClient, detail_url):
    """Tests the delete method with the authenticated other user client."""
    response = other_apiClient.delete(detail_url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    daemonModel.refresh_from_db()
    assert daemonModel.name is not None


@pytest.mark.django_db
def test_delete_auth_owner(daemonModel, owner_apiClient, detail_url):
    """Tests the delete method with the authenticated owner user client."""
    response = owner_apiClient.delete(detail_url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    with pytest.raises(daemonModel.DoesNotExist):
        daemonModel.refresh_from_db()



@pytest.mark.django_db
def test_add_daemon_noauth(daemonModel, noauth_apiClient, custom_detail_action_url):
    """Tests the post method :func:`Emailkasten.Views.DaemonViewSet.DaemonViewSet.add_daemon` action with an unauthenticated user client."""
    response = noauth_apiClient.post(custom_detail_action_url(DaemonViewSet.URL_NAME_ADD_DAEMON))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['save_attachments']
    with pytest.raises(DaemonModel.DoesNotExist):
        DaemonModel.objects.get(mailbox=daemonModel)
    assert DaemonModel.objects.all().count() == 0


@pytest.mark.django_db
def test_add_daemon_auth_other(daemonModel, other_apiClient, custom_detail_action_url):
    """Tests the post method :func:`Emailkasten.Views.DaemonViewSet.DaemonViewSet.add_daemon` action with the authenticated other user client."""
    response = other_apiClient.post(custom_detail_action_url(DaemonViewSet.URL_NAME_ADD_DAEMON))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    with pytest.raises(KeyError):
        response.data['save_attachments']
    with pytest.raises(DaemonModel.DoesNotExist):
        DaemonModel.objects.get(mailbox=daemonModel)
    assert DaemonModel.objects.all().count() == 0


@pytest.mark.django_db
def test_add_daemon_auth_owner(daemonModel, owner_apiClient, custom_detail_action_url):
    """Tests the post method :func:`Emailkasten.Views.DaemonViewSet.DaemonViewSet.add_daemon` action with the authenticated owner user client."""
    response = owner_apiClient.post(custom_detail_action_url(DaemonViewSet.URL_NAME_ADD_DAEMON))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['mailbox'] == DaemonViewSet.serializer_class(daemonModel).data

    daemonModel = DaemonModel.objects.get(mailbox=daemonModel)
    assert daemonModel is not None
    assert DaemonModel.objects.all().count() == 1


@pytest.mark.django_db
def test_test_mailbox_noauth(daemonModel, noauth_apiClient, custom_detail_action_url, mocker):
    """Tests the post method :func:`Emailkasten.Views.DaemonViewSet.DaemonViewSet.test_mailbox` action with an unauthenticated user client."""
    mock_testMailbox = mocker.patch('Emailkasten.Views.DaemonViewSet.testMailbox')
    previous_is_healthy = daemonModel.is_healthy

    response = noauth_apiClient.post(custom_detail_action_url(DaemonViewSet.URL_NAME_TEST))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_testMailbox.assert_not_called()
    daemonModel.refresh_from_db()
    assert daemonModel.is_healthy is previous_is_healthy
    with pytest.raises(KeyError):
        response.data['name']


@pytest.mark.django_db
def test_test_mailbox_auth_other(daemonModel, other_apiClient, custom_detail_action_url, mocker):
    """Tests the post method :func:`Emailkasten.Views.DaemonViewSet.DaemonViewSet.test_mailbox` action with the authenticated other user client."""
    mock_testMailbox = mocker.patch('Emailkasten.Views.DaemonViewSet.testMailbox')
    previous_is_healthy = daemonModel.is_healthy

    response = other_apiClient.post(custom_detail_action_url(DaemonViewSet.URL_NAME_TEST))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_testMailbox.assert_not_called()
    daemonModel.refresh_from_db()
    assert daemonModel.is_healthy is previous_is_healthy
    with pytest.raises(KeyError):
        response.data['name']


@pytest.mark.django_db
def test_test_mailbox_auth_owner(daemonModel, owner_apiClient, custom_detail_action_url, mocker):
    """Tests the post method :func:`Emailkasten.Views.DaemonViewSet.DaemonViewSet.test_mailbox` action with the authenticated owner user client."""
    mock_testMailbox = mocker.patch('Emailkasten.Views.DaemonViewSet.testMailbox')

    response = owner_apiClient.post(custom_detail_action_url(DaemonViewSet.URL_NAME_TEST))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['mailbox'] == DaemonViewSet.serializer_class(daemonModel).data
    mock_testMailbox.assert_called_once_with(daemonModel)


@pytest.mark.django_db
def test_fetch_all_noauth(daemonModel, noauth_apiClient, custom_detail_action_url, mocker):
    """Tests the post method :func:`Emailkasten.Views.DaemonViewSet.DaemonViewSet.fetch_all` action with an unauthenticated user client."""
    mock_fetchAndProcessMails = mocker.patch('Emailkasten.Views.DaemonViewSet.fetchAndProcessMails')

    response = noauth_apiClient.post(custom_detail_action_url(DaemonViewSet.URL_NAME_FETCH_ALL))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_fetchAndProcessMails.assert_not_called()
    assert EMailModel.objects.all().count() == 0
    with pytest.raises(KeyError):
        response.data['name']


@pytest.mark.django_db
def test_fetch_all_auth_other(daemonModel, other_apiClient, custom_detail_action_url, mocker):
    """Tests the post method :func:`Emailkasten.Views.DaemonViewSet.DaemonViewSet.fetch_all` action with the authenticated other user client."""
    mock_fetchAndProcessMails = mocker.patch('Emailkasten.Views.DaemonViewSet.fetchAndProcessMails')

    response = other_apiClient.post(custom_detail_action_url(DaemonViewSet.URL_NAME_FETCH_ALL))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_fetchAndProcessMails.assert_not_called()
    assert EMailModel.objects.all().count() == 0
    with pytest.raises(KeyError):
        response.data['name']


@pytest.mark.django_db
def test_fetch_all_auth_owner(daemonModel, owner_apiClient, custom_detail_action_url, mocker):
    """Tests the post method :func:`Emailkasten.Views.DaemonViewSet.DaemonViewSet.fetch_all` action with the authenticated owner user client."""
    mock_fetchAndProcessMails = mocker.patch('Emailkasten.Views.DaemonViewSet.fetchAndProcessMails')

    response = owner_apiClient.post(custom_detail_action_url(DaemonViewSet.URL_NAME_FETCH_ALL))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['mailbox'] == DaemonViewSet.serializer_class(daemonModel).data
    mock_fetchAndProcessMails.assert_called_once_with(daemonModel, daemonModel.account, Emailkasten.Views.DaemonViewSet.constants.MailFetchingCriteria.ALL)


@pytest.mark.django_db
def test_toggle_favorite_noauth(daemonModel, noauth_apiClient, custom_detail_action_url):
    """Tests the post method :func:`Emailkasten.Views.DaemonViewSet.DaemonViewSet.toggle_favorite` action with an unauthenticated user client."""
    response = noauth_apiClient.post(custom_detail_action_url(DaemonViewSet.URL_NAME_TOGGLE_FAVORITE))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    daemonModel.refresh_from_db()
    assert daemonModel.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_other(daemonModel, other_apiClient, custom_detail_action_url):
    """Tests the post method :func:`Emailkasten.Views.DaemonViewSet.DaemonViewSet.toggle_favorite` action with the authenticated other user client."""
    response = other_apiClient.post(custom_detail_action_url(DaemonViewSet.URL_NAME_TOGGLE_FAVORITE))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    daemonModel.refresh_from_db()
    assert daemonModel.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_owner(daemonModel, owner_apiClient, custom_detail_action_url):
    """Tests the post method :func:`Emailkasten.Views.DaemonViewSet.DaemonViewSet.toggle_favorite` action with the authenticated owner user client."""
    response = owner_apiClient.post(custom_detail_action_url(DaemonViewSet.URL_NAME_TOGGLE_FAVORITE))

    assert response.status_code == status.HTTP_200_OK
    daemonModel.refresh_from_db()
    assert daemonModel.is_favorite is True
