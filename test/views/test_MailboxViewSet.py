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

from Emailkasten.Models.MailboxModel import MailboxModel
from Emailkasten.Views.MailboxViewSet import MailboxViewSet


@pytest.fixture(name='owner_user')
def fixture_owner_user():
    return baker.make(User)

@pytest.fixture(name='other_user')
def fixture_other_user():
    return baker.make(User)

@pytest.fixture(name='mailboxModel')
def fixture_MailboxModel(owner_user):
    return baker.make(MailboxModel, account__user=owner_user)

@pytest.fixture(name='mailboxPayload')
def fixture_mailboxPayload(owner_user):
    accountData = baker.prepare(MailboxModel, account__user=owner_user)
    payload = model_to_dict(accountData)
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
def test_put_noauth(accountModel, noauth_apiClient, mailboxPayload, detail_url):
    response = noauth_apiClient.put(detail_url, data=mailboxPayload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['save_attachments']
    with pytest.raises(KeyError):
        response.data['password']
    with pytest.raises(MailboxModel.DoesNotExist):
        accountModel.refresh_from_db()


@pytest.mark.django_db
def test_put_auth_other(accountModel, other_apiClient, mailboxPayload, detail_url):
    response = other_apiClient.put(detail_url, data=mailboxPayload)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    with pytest.raises(MailboxModel.DoesNotExist):
        accountModel.refresh_from_db()


@pytest.mark.django_db
def test_put_auth_owner(accountModel, owner_apiClient, mailboxPayload, detail_url):
    response = owner_apiClient.put(detail_url, data=mailboxPayload)

    assert response.status_code == status.HTTP_200_OK
    assert response.data['save_attachments'] == mailboxPayload['save_attachments']
    accountModel.refresh_from_db()
    assert accountModel.save_attachments == mailboxPayload['save_attachments']


@pytest.mark.django_db
def test_post_noauth(noauth_apiClient, mailboxPayload, list_url):
    response = noauth_apiClient.post(list_url, data=mailboxPayload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data['save_attachments']
    with pytest.raises(MailboxModel.DoesNotExist):
        MailboxModel.objects.get(save_attachments = mailboxPayload['save_attachments'])


@pytest.mark.django_db
def test_post_auth_other(other_user, other_apiClient, mailboxPayload, list_url):
    response = other_apiClient.post(list_url, data=mailboxPayload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['save_attachments'] == mailboxPayload['save_attachments']
    postedMailboxModel = MailboxModel.objects.get(save_attachments = mailboxPayload['save_attachments'])
    assert postedMailboxModel is not None
    assert postedMailboxModel.user == other_user


@pytest.mark.django_db
def test_post_auth_owner(owner_apiClient, mailboxPayload, list_url):
    response = owner_apiClient.post(list_url, data=mailboxPayload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['save_attachments'] == mailboxPayload['save_attachments']
    postedMailboxModel = MailboxModel.objects.get(save_attachments = mailboxPayload['save_attachments'])
    assert postedMailboxModel is not None


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
    assert mailboxModel.save_attachments is False


@pytest.mark.django_db
def test_delete_auth_owner(mailboxModel, owner_apiClient, detail_url):
    response = owner_apiClient.delete(detail_url)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    with pytest.raises(mailboxModel.DoesNotExist):
        mailboxModel.refresh_from_db()



@pytest.mark.django_db
def test_scan_mailboxes_noauth(mailboxModel, noauth_apiClient, custom_detail_action_url, mocker):
    mock_scanMailboxes = mocker.patch('Emailkasten.Views.MailboxViewSet.scanMailboxes')
    response = noauth_apiClient.delete(custom_detail_action_url(MailboxViewSet.URL_NAME_SCAN_MAILBOXES))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_scanMailboxes.assert_not_called()
    with pytest.raises(KeyError):
        response.data['save_attachments']


@pytest.mark.django_db
def test_scan_mailboxes_auth_other(mailboxModel, other_apiClient, custom_detail_action_url, mocker):
    mock_scanMailboxes = mocker.patch('Emailkasten.Views.MailboxViewSet.scanMailboxes')
    response = other_apiClient.post(custom_detail_action_url(MailboxViewSet.URL_NAME_SCAN_MAILBOXES))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_scanMailboxes.assert_not_called()
    with pytest.raises(KeyError):
        response.data['save_attachments']


@pytest.mark.django_db
def test_scan_mailboxes_auth_owner(mailboxModel, owner_apiClient, custom_detail_action_url, mocker):
    mock_scanMailboxes = mocker.patch('Emailkasten.Views.MailboxViewSet.scanMailboxes')
    response = owner_apiClient.post(custom_detail_action_url(MailboxViewSet.URL_NAME_SCAN_MAILBOXES))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['account'] == MailboxViewSet.serializer_class(mailboxModel).data
    mock_scanMailboxes.assert_called_once_with(mailboxModel)


@pytest.mark.django_db
def test_test_noauth(mailboxModel, noauth_apiClient, custom_detail_action_url, mocker):
    mock_testAccount = mocker.patch('Emailkasten.Views.MailboxViewSet.testAccount')
    response = noauth_apiClient.delete(custom_detail_action_url(MailboxViewSet.URL_NAME_TEST))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_testAccount.assert_not_called()
    with pytest.raises(KeyError):
        response.data['name']


@pytest.mark.django_db
def test_test_auth_other(mailboxModel, other_apiClient, custom_detail_action_url, mocker):
    mock_testAccount = mocker.patch('Emailkasten.Views.MailboxViewSet.testAccount')
    response = other_apiClient.post(custom_detail_action_url(MailboxViewSet.URL_NAME_TEST))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_testAccount.assert_not_called()
    with pytest.raises(KeyError):
        response.data['name']

@pytest.mark.django_db
def test_test_auth_owner(mailboxModel, owner_apiClient, custom_detail_action_url, mocker):
    mock_testAccount = mocker.patch('Emailkasten.Views.MailboxViewSet.testAccount')
    response = owner_apiClient.post(custom_detail_action_url(MailboxViewSet.URL_NAME_TEST))

    assert response.status_code == status.HTTP_200_OK
    assert response.data['account'] == MailboxViewSet.serializer_class(mailboxModel).data
    mock_testAccount.assert_called_once_with(mailboxModel)


@pytest.mark.django_db
def test_toggle_favorite_noauth(mailboxModel, noauth_apiClient, custom_detail_action_url):
    response = noauth_apiClient.delete(custom_detail_action_url(MailboxViewSet.URL_NAME_TOGGLE_FAVORITE))

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


@pytest.mark.django_db
def test_favorites_noauth(mailboxModel, noauth_apiClient, custom_list_action_url):
    response = noauth_apiClient.get(custom_list_action_url(MailboxViewSet.URL_NAME_FAVORITES))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert not any(item == 'name' for item in response.data)


@pytest.mark.django_db
def test_favorites_auth_other(mailboxModel, other_apiClient, custom_list_action_url):
    mailboxModel.is_favorite = True
    mailboxModel.save()

    response = other_apiClient.get(custom_list_action_url(MailboxViewSet.URL_NAME_FAVORITES))

    assert response.status_code == status.HTTP_200_OK
    assert response.data == []


@pytest.mark.django_db
def test_favorites_auth_owner(mailboxModel, owner_apiClient, custom_list_action_url):
    mailboxModel.is_favorite = True
    mailboxModel.save()

    response = owner_apiClient.get(custom_list_action_url(MailboxViewSet.URL_NAME_FAVORITES))

    assert response.status_code == status.HTTP_200_OK
    assert response.data == MailboxViewSet.serializer_class([mailboxModel], many=True).data
