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
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.urls import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APIClient

import Emailkasten.Views.MailboxViewSet
from Emailkasten.Models.AccountModel import AccountModel
from Emailkasten.Models.DaemonModel import DaemonModel
from Emailkasten.Models.EMailModel import EMailModel
from Emailkasten.Models.MailboxModel import MailboxModel
from Emailkasten.Views.MailboxViewSet import MailboxViewSet


@pytest.fixture(name='owner_user')
def fixture_owner_user():
    return baker.make(User)

@pytest.fixture(name='other_user')
def fixture_other_user():
    return baker.make(User)

@pytest.fixture(name='accountModel')
def fixture_accountModel(owner_user):
    return baker.make(AccountModel, user = owner_user)

@pytest.fixture(name='mailboxModel')
def fixture_MailboxModel(accountModel):
    return baker.make(MailboxModel, account=accountModel)

@pytest.fixture(name='mailboxPayload')
def fixture_mailboxPayload(accountModel):
    mailboxData = baker.prepare(MailboxModel, account=accountModel, save_attachments=False)
    payload = model_to_dict(mailboxData)
    payload.pop('id')
    cleanPayload = {key: value for key, value in payload.items() if value is not None}
    return cleanPayload

@pytest.fixture(name='list_url')
def fixture_list_url():
    return reverse(f'{MailboxViewSet.BASENAME}-list')

@pytest.fixture(name='detail_url')
def fixture_detail_url(mailboxModel):
    return reverse(f'{MailboxViewSet.BASENAME}-detail', args=[mailboxModel.id])

@pytest.fixture(name='custom_list_action_url')
def fixture_custom_list_action_url():
    return lambda custom_list_action_url_name: reverse(f'{MailboxViewSet.BASENAME}-{custom_list_action_url_name}')

@pytest.fixture(name='custom_detail_action_url')
def fixture_custom_detail_action_url(mailboxModel):
    return lambda custom_detail_action_url_name: reverse(f'{MailboxViewSet.BASENAME}-{custom_detail_action_url_name}', args=[mailboxModel.id])

@pytest.fixture(name='noauth_apiClient')
def fixture_noauth_apiClient():
    return APIClient()

@pytest.fixture(name='owner_apiClient')
def fixture_owner_apiClient(noauth_apiClient, owner_user):
    noauth_apiClient.force_authenticate(user=owner_user)
    return noauth_apiClient

@pytest.fixture(name='other_apiClient')
def fixture_other_apiClient(noauth_apiClient, other_user):
    noauth_apiClient.force_authenticate(user=other_user)
    return noauth_apiClient


@pytest.mark.django_db
def test_list_noauth(mailboxModel, noauth_apiClient, list_url):
    response = noauth_apiClient.get(list_url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['results']


@pytest.mark.django_db
def test_list_auth_other(mailboxModel, other_apiClient, list_url):
    response = other_apiClient.get(list_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 0
    assert response.data['results'] == []


@pytest.mark.django_db
def test_list_auth_owner(mailboxModel, owner_apiClient, list_url):
    response = owner_apiClient.get(list_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1
    assert len(response.data['results']) == 1


@pytest.mark.django_db
def test_get_noauth(mailboxModel, noauth_apiClient, detail_url):
    response = noauth_apiClient.get(detail_url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['name']


@pytest.mark.django_db
def test_get_auth_other(mailboxModel, other_apiClient, detail_url):
    response = other_apiClient.get(detail_url)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get_auth_owner(mailboxModel, owner_apiClient, detail_url):
    response = owner_apiClient.get(detail_url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['name'] == mailboxModel.name


@pytest.mark.django_db
def test_patch_noauth(mailboxModel, noauth_apiClient, detail_url):
    response = noauth_apiClient.patch(detail_url, data={'save_attachments': True})

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['save_attachments']


@pytest.mark.django_db
def test_patch_auth_other(mailboxModel, other_apiClient, detail_url):
    response = other_apiClient.patch(detail_url, data={'save_attachments': True})

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mailboxModel.refresh_from_db()
    assert mailboxModel.save_attachments is False


@pytest.mark.django_db
def test_patch_auth_owner(mailboxModel, owner_apiClient, detail_url):
    response = owner_apiClient.patch(detail_url, data={'save_attachments': True})

    assert response.status_code == status.HTTP_200_OK
    assert response.data['save_attachments'] is True
    mailboxModel.refresh_from_db()
    assert mailboxModel.save_attachments is True


@pytest.mark.django_db
def test_put_noauth(mailboxModel, noauth_apiClient, mailboxPayload, detail_url):
    response = noauth_apiClient.put(detail_url, data=mailboxPayload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['save_attachments']
    mailboxModel.refresh_from_db()
    assert mailboxModel.save_attachments != mailboxPayload['save_attachments']


@pytest.mark.django_db
def test_put_auth_other(mailboxModel, other_apiClient, mailboxPayload, detail_url):
    response = other_apiClient.put(detail_url, data=mailboxPayload)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    with pytest.raises(KeyError):
        response.data['save_attachments']
    mailboxModel.refresh_from_db()
    assert mailboxModel.save_attachments != mailboxPayload['save_attachments']


@pytest.mark.django_db
def test_put_auth_owner(mailboxModel, owner_apiClient, mailboxPayload, detail_url):
    response = owner_apiClient.put(detail_url, data=mailboxPayload)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['save_attachments'] == mailboxPayload['save_attachments']
    mailboxModel.refresh_from_db()
    assert mailboxModel.save_attachments == mailboxPayload['save_attachments']


@pytest.mark.django_db
def test_post_noauth(noauth_apiClient, mailboxPayload, list_url):
    response = noauth_apiClient.post(list_url, data=mailboxPayload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['save_attachments']
    with pytest.raises(MailboxModel.DoesNotExist):
        MailboxModel.objects.get(save_attachments = mailboxPayload['save_attachments'])


@pytest.mark.django_db
def test_post_auth_other(other_apiClient, mailboxPayload, list_url):
    response = other_apiClient.post(list_url, data=mailboxPayload)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data['save_attachments']
    with pytest.raises(MailboxModel.DoesNotExist):
        MailboxModel.objects.get(save_attachments = mailboxPayload['save_attachments'])



@pytest.mark.django_db
def test_post_auth_owner(owner_apiClient, mailboxPayload, list_url):
    response = owner_apiClient.post(list_url, data=mailboxPayload)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data['save_attachments']
    with pytest.raises(MailboxModel.DoesNotExist):
        MailboxModel.objects.get(save_attachments = mailboxPayload['save_attachments'])


@pytest.mark.django_db
def test_delete_noauth(mailboxModel, noauth_apiClient, detail_url):
    response = noauth_apiClient.delete(detail_url)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mailboxModel.refresh_from_db()
    assert mailboxModel.name is not None


@pytest.mark.django_db
def test_delete_auth_other(mailboxModel, other_apiClient, detail_url):
    response = other_apiClient.delete(detail_url)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mailboxModel.refresh_from_db()
    assert mailboxModel.name is not None


@pytest.mark.django_db
def test_delete_auth_owner(mailboxModel, owner_apiClient, detail_url):
    response = owner_apiClient.delete(detail_url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    with pytest.raises(mailboxModel.DoesNotExist):
        mailboxModel.refresh_from_db()



@pytest.mark.django_db
def test_add_daemon_noauth(mailboxModel, noauth_apiClient, custom_detail_action_url):
    response = noauth_apiClient.post(custom_detail_action_url(MailboxViewSet.URL_NAME_ADD_DAEMON))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['save_attachments']
    with pytest.raises(DaemonModel.DoesNotExist):
        DaemonModel.objects.get(mailbox=mailboxModel)
    assert DaemonModel.objects.all().count() == 0


@pytest.mark.django_db
def test_add_daemon_auth_other(mailboxModel, other_apiClient, custom_detail_action_url):
    response = other_apiClient.post(custom_detail_action_url(MailboxViewSet.URL_NAME_ADD_DAEMON))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    with pytest.raises(KeyError):
        response.data['save_attachments']
    with pytest.raises(DaemonModel.DoesNotExist):
        DaemonModel.objects.get(mailbox=mailboxModel)
    assert DaemonModel.objects.all().count() == 0


@pytest.mark.django_db
def test_add_daemon_auth_owner(mailboxModel, owner_apiClient, custom_detail_action_url):
    response = owner_apiClient.post(custom_detail_action_url(MailboxViewSet.URL_NAME_ADD_DAEMON))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['mailbox'] == MailboxViewSet.serializer_class(mailboxModel).data

    daemonModel = DaemonModel.objects.get(mailbox=mailboxModel)
    assert daemonModel is not None
    assert DaemonModel.objects.all().count() == 1


@pytest.mark.django_db
def test_test_mailbox_noauth(mailboxModel, noauth_apiClient, custom_detail_action_url, mocker):
    mock_testMailbox = mocker.patch('Emailkasten.Views.MailboxViewSet.testMailbox')
    previous_is_healthy = mailboxModel.is_healthy

    response = noauth_apiClient.post(custom_detail_action_url(MailboxViewSet.URL_NAME_TEST))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_testMailbox.assert_not_called()
    mailboxModel.refresh_from_db()
    assert mailboxModel.is_healthy is previous_is_healthy
    with pytest.raises(KeyError):
        response.data['name']


@pytest.mark.django_db
def test_test_mailbox_auth_other(mailboxModel, other_apiClient, custom_detail_action_url, mocker):
    mock_testMailbox = mocker.patch('Emailkasten.Views.MailboxViewSet.testMailbox')
    previous_is_healthy = mailboxModel.is_healthy

    response = other_apiClient.post(custom_detail_action_url(MailboxViewSet.URL_NAME_TEST))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_testMailbox.assert_not_called()
    mailboxModel.refresh_from_db()
    assert mailboxModel.is_healthy is previous_is_healthy
    with pytest.raises(KeyError):
        response.data['name']


@pytest.mark.django_db
def test_test_mailbox_auth_owner(mailboxModel, owner_apiClient, custom_detail_action_url, mocker):
    mock_testMailbox = mocker.patch('Emailkasten.Views.MailboxViewSet.testMailbox')

    response = owner_apiClient.post(custom_detail_action_url(MailboxViewSet.URL_NAME_TEST))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['mailbox'] == MailboxViewSet.serializer_class(mailboxModel).data
    mock_testMailbox.assert_called_once_with(mailboxModel)


@pytest.mark.django_db
def test_fetch_all_noauth(mailboxModel, noauth_apiClient, custom_detail_action_url, mocker):
    mock_fetchAndProcessMails = mocker.patch('Emailkasten.Views.MailboxViewSet.fetchAndProcessMails')

    response = noauth_apiClient.post(custom_detail_action_url(MailboxViewSet.URL_NAME_FETCH_ALL))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_fetchAndProcessMails.assert_not_called()
    assert EMailModel.objects.all().count() == 0
    with pytest.raises(KeyError):
        response.data['name']


@pytest.mark.django_db
def test_fetch_all_auth_other(mailboxModel, other_apiClient, custom_detail_action_url, mocker):
    mock_fetchAndProcessMails = mocker.patch('Emailkasten.Views.MailboxViewSet.fetchAndProcessMails')

    response = other_apiClient.post(custom_detail_action_url(MailboxViewSet.URL_NAME_FETCH_ALL))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_fetchAndProcessMails.assert_not_called()
    assert EMailModel.objects.all().count() == 0
    with pytest.raises(KeyError):
        response.data['name']


@pytest.mark.django_db
def test_fetch_all_auth_owner(mailboxModel, owner_apiClient, custom_detail_action_url, mocker):
    mock_fetchAndProcessMails = mocker.patch('Emailkasten.Views.MailboxViewSet.fetchAndProcessMails')

    response = owner_apiClient.post(custom_detail_action_url(MailboxViewSet.URL_NAME_FETCH_ALL))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['mailbox'] == MailboxViewSet.serializer_class(mailboxModel).data
    mock_fetchAndProcessMails.assert_called_once_with(mailboxModel, mailboxModel.account, Emailkasten.Views.MailboxViewSet.constants.MailFetchingCriteria.ALL)


@pytest.mark.django_db
def test_toggle_favorite_noauth(mailboxModel, noauth_apiClient, custom_detail_action_url):
    response = noauth_apiClient.post(custom_detail_action_url(MailboxViewSet.URL_NAME_TOGGLE_FAVORITE))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mailboxModel.refresh_from_db()
    assert mailboxModel.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_other(mailboxModel, other_apiClient, custom_detail_action_url):
    response = other_apiClient.post(custom_detail_action_url(MailboxViewSet.URL_NAME_TOGGLE_FAVORITE))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mailboxModel.refresh_from_db()
    assert mailboxModel.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_owner(mailboxModel, owner_apiClient, custom_detail_action_url):
    response = owner_apiClient.post(custom_detail_action_url(MailboxViewSet.URL_NAME_TOGGLE_FAVORITE))

    assert response.status_code == status.HTTP_200_OK
    mailboxModel.refresh_from_db()
    assert mailboxModel.is_favorite is True
