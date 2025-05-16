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

"""Test module for :mod:`api.v1.views.AccountViewSet`'s basic CRUD actions."""

from __future__ import annotations

import pytest
from django.forms.models import model_to_dict
from rest_framework import status

from api.v1.views.AccountViewSet import AccountViewSet
from core.models.Account import Account


@pytest.mark.django_db
def test_list_noauth(fake_account, noauth_apiClient, list_url):
    """Tests the list method on :class:`api.v1.views.AccountViewSet.AccountViewSet` with an unauthenticated user client."""
    response = noauth_apiClient.get(list_url(AccountViewSet))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["results"]


@pytest.mark.django_db
def test_list_auth_other(fake_account, other_apiClient, list_url):
    """Tests the list method on :class:`api.v1.views.AccountViewSet.AccountViewSet` with the authenticated other user client."""
    response = other_apiClient.get(list_url(AccountViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []


@pytest.mark.django_db
def test_list_auth_owner(fake_account, owner_apiClient, list_url):
    """Tests the list method on :class:`api.v1.views.AccountViewSet.AccountViewSet` with the authenticated owner user client."""
    response = owner_apiClient.get(list_url(AccountViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1
    with pytest.raises(KeyError):
        response.data["results"][0]["password"]


@pytest.mark.django_db
def test_get_noauth(fake_account, noauth_apiClient, detail_url):
    """Tests the get method on :class:`api.v1.views.AccountViewSet.AccountViewSet` with an unauthenticated user client."""
    response = noauth_apiClient.get(detail_url(AccountViewSet, fake_account))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["mail_address"]


@pytest.mark.django_db
def test_get_auth_other(fake_account, other_apiClient, detail_url):
    """Tests the get method on :class:`api.v1.views.AccountViewSet.AccountViewSet` with the authenticated other user client."""
    response = other_apiClient.get(detail_url(AccountViewSet, fake_account))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    with pytest.raises(KeyError):
        response.data["password"]


@pytest.mark.django_db
def test_get_auth_owner(fake_account, owner_apiClient, detail_url):
    """Tests the list method on :class:`api.v1.views.AccountViewSet.AccountViewSet` with the authenticated owner user client."""
    response = owner_apiClient.get(detail_url(AccountViewSet, fake_account))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["mail_address"] == fake_account.mail_address
    with pytest.raises(KeyError):
        response.data["password"]


@pytest.mark.django_db
def test_patch_noauth(fake_account, noauth_apiClient, accountPayload, detail_url):
    """Tests the patch method on :class:`api.v1.views.AccountViewSet.AccountViewSet` with an unauthenticated user client."""
    response = noauth_apiClient.patch(
        detail_url(AccountViewSet, fake_account), data=accountPayload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["mail_address"]
    with pytest.raises(KeyError):
        response.data["password"]
    fake_account.refresh_from_db()
    assert fake_account.mail_address != accountPayload["mail_address"]
    assert fake_account.password != accountPayload["password"]


@pytest.mark.django_db
def test_patch_auth_other(fake_account, other_apiClient, accountPayload, detail_url):
    """Tests the patch method on :class:`api.v1.views.AccountViewSet.AccountViewSet` with the authenticated other user client."""
    response = other_apiClient.patch(
        detail_url(AccountViewSet, fake_account), data=accountPayload
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    with pytest.raises(KeyError):
        response.data["mail_address"]
    with pytest.raises(KeyError):
        response.data["password"]
    fake_account.refresh_from_db()
    assert fake_account.mail_address != accountPayload["mail_address"]
    assert fake_account.password != accountPayload["password"]


@pytest.mark.django_db
def test_patch_auth_owner(fake_account, owner_apiClient, accountPayload, detail_url):
    """Tests the patch method on :class:`api.v1.views.AccountViewSet.AccountViewSet` with the authenticated owner user client."""
    response = owner_apiClient.patch(
        detail_url(AccountViewSet, fake_account), data=accountPayload
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["mail_address"] == accountPayload["mail_address"]
    with pytest.raises(KeyError):
        response.data["password"]
    fake_account.refresh_from_db()
    assert fake_account.mail_address == accountPayload["mail_address"]
    assert fake_account.password == accountPayload["password"]


@pytest.mark.django_db
def test_put_noauth(fake_account, noauth_apiClient, accountPayload, detail_url):
    """Tests the put method on :class:`api.v1.views.AccountViewSet.AccountViewSet` with an unauthenticated user client."""
    response = noauth_apiClient.put(
        detail_url(AccountViewSet, fake_account), data=accountPayload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["mail_host"]
    with pytest.raises(KeyError):
        response.data["password"]
    fake_account.refresh_from_db()
    assert fake_account.mail_host != accountPayload["mail_host"]


@pytest.mark.django_db
def test_put_auth_other(fake_account, other_apiClient, accountPayload, detail_url):
    """Tests the put method on :class:`api.v1.views.AccountViewSet.AccountViewSet` with the authenticated other user client."""
    response = other_apiClient.put(
        detail_url(AccountViewSet, fake_account), data=accountPayload
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    with pytest.raises(KeyError):
        response.data["mail_host"]
    with pytest.raises(KeyError):
        response.data["password"]
    fake_account.refresh_from_db()
    assert fake_account.mail_host != accountPayload["mail_host"]


@pytest.mark.django_db
def test_put_auth_owner(fake_account, owner_apiClient, accountPayload, detail_url):
    """Tests the put method on :class:`api.v1.views.AccountViewSet.AccountViewSet` with the authenticated owner user client."""
    response = owner_apiClient.put(
        detail_url(AccountViewSet, fake_account), data=accountPayload
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["mail_host"] == accountPayload["mail_host"]
    with pytest.raises(KeyError):
        response.data["password"]
    fake_account.refresh_from_db()
    assert fake_account.mail_host == accountPayload["mail_host"]


@pytest.mark.django_db
def test_post_noauth(noauth_apiClient, accountPayload, list_url):
    """Tests the post method on :class:`api.v1.views.AccountViewSet.AccountViewSet` with an unauthenticated user client."""
    response = noauth_apiClient.post(list_url(AccountViewSet), data=accountPayload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["mail_host"]
    with pytest.raises(KeyError):
        response.data["password"]
    with pytest.raises(Account.DoesNotExist):
        Account.objects.get(mail_host=accountPayload["mail_host"])


@pytest.mark.django_db
def test_post_auth_other(other_user, other_apiClient, accountPayload, list_url):
    """Tests the post method on :class:`api.v1.views.AccountViewSet.AccountViewSet` with the authenticated other user client."""
    response = other_apiClient.post(list_url(AccountViewSet), data=accountPayload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["mail_host"] == accountPayload["mail_host"]
    with pytest.raises(KeyError):
        response.data["password"]
    postedAccount = Account.objects.get(mail_host=accountPayload["mail_host"])
    assert postedAccount is not None
    assert postedAccount.user == other_user


@pytest.mark.django_db
def test_post_auth_owner(owner_user, owner_apiClient, accountPayload, list_url):
    """Tests the post method on :class:`api.v1.views.AccountViewSet.AccountViewSet` with the authenticated owner user client."""
    response = owner_apiClient.post(list_url(AccountViewSet), data=accountPayload)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["mail_host"] == accountPayload["mail_host"]
    with pytest.raises(KeyError):
        response.data["password"]
    postedAccount = Account.objects.get(mail_host=accountPayload["mail_host"])
    assert postedAccount is not None
    assert postedAccount.user == owner_user


@pytest.mark.django_db
def test_post_duplicate_auth_owner(fake_account, owner_apiClient, list_url):
    """Tests the post method on :class:`api.v1.views.AccountViewSet.AccountViewSet` with the authenticated owner user client and duplicate data."""
    payload = model_to_dict(fake_account)
    payload.pop("id")
    cleanPayload = {key: value for key, value in payload.items() if value is not None}

    response = owner_apiClient.post(list_url(AccountViewSet), data=cleanPayload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_delete_noauth(fake_account, noauth_apiClient, detail_url):
    """Tests the delete method on :class:`api.v1.views.AccountViewSet.AccountViewSet` with an unauthenticated user client."""
    response = noauth_apiClient.delete(detail_url(AccountViewSet, fake_account))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    fake_account.refresh_from_db()
    assert fake_account.mail_address is not None


@pytest.mark.django_db
def test_delete_auth_other(fake_account, other_apiClient, detail_url):
    """Tests the delete method on :class:`api.v1.views.AccountViewSet.AccountViewSet` with the authenticated other user client."""
    response = other_apiClient.delete(detail_url(AccountViewSet, fake_account))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    fake_account.refresh_from_db()
    assert fake_account.mail_address is not None


@pytest.mark.django_db
def test_delete_auth_owner(fake_account, owner_apiClient, detail_url):
    """Tests the delete method on :class:`api.v1.views.AccountViewSet.AccountViewSet` with the authenticated owner user client."""
    response = owner_apiClient.delete(detail_url(AccountViewSet, fake_account))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    with pytest.raises(Account.DoesNotExist):
        fake_account.refresh_from_db()
