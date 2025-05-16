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

"""Test module for :mod:`api.v1.views.MailboxViewSet`'s basic CRUD actions."""

from __future__ import annotations

import pytest
from rest_framework import status

from api.v1.views.MailboxViewSet import MailboxViewSet
from core.models.Mailbox import Mailbox


@pytest.mark.django_db
def test_list_noauth(fake_mailbox, noauth_apiClient, list_url):
    """Tests the list method on :class:`api.v1.views.MailboxViewSet.MailboxViewSet` with an unauthenticated user client."""
    response = noauth_apiClient.get(list_url(MailboxViewSet))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["results"]


@pytest.mark.django_db
def test_list_auth_other(fake_mailbox, other_apiClient, list_url):
    """Tests the list method on :class:`api.v1.views.MailboxViewSet.MailboxViewSet` with the authenticated other user client."""
    response = other_apiClient.get(list_url(MailboxViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 0
    assert response.data["results"] == []


@pytest.mark.django_db
def test_list_auth_owner(fake_mailbox, owner_apiClient, list_url):
    """Tests the list method on :class:`api.v1.views.MailboxViewSet.MailboxViewSet` with the authenticated owner user client."""
    response = owner_apiClient.get(list_url(MailboxViewSet))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["count"] == 1
    assert len(response.data["results"]) == 1


@pytest.mark.django_db
def test_get_noauth(fake_mailbox, noauth_apiClient, detail_url):
    """Tests the get method on :class:`api.v1.views.MailboxViewSet.MailboxViewSet` with an unauthenticated user client."""
    response = noauth_apiClient.get(detail_url(MailboxViewSet, fake_mailbox))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["name"]


@pytest.mark.django_db
def test_get_auth_other(fake_mailbox, other_apiClient, detail_url):
    """Tests the get method on :class:`api.v1.views.MailboxViewSet.MailboxViewSet` with the authenticated other user client."""
    response = other_apiClient.get(detail_url(MailboxViewSet, fake_mailbox))

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_get_auth_owner(fake_mailbox, owner_apiClient, detail_url):
    """Tests the list method on :class:`api.v1.views.MailboxViewSet.MailboxViewSet` with the authenticated owner user client."""
    response = owner_apiClient.get(detail_url(MailboxViewSet, fake_mailbox))

    assert response.status_code == status.HTTP_200_OK
    assert response.data["name"] == fake_mailbox.name


@pytest.mark.django_db
def test_patch_noauth(fake_mailbox, noauth_apiClient, mailboxPayload, detail_url):
    """Tests the patch method on :class:`api.v1.views.MailboxViewSet.MailboxViewSet` with an unauthenticated user client."""
    response = noauth_apiClient.patch(
        detail_url(MailboxViewSet, fake_mailbox), data=mailboxPayload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["save_attachments"]
    fake_mailbox.refresh_from_db()
    assert fake_mailbox.save_attachments is not mailboxPayload["save_attachments"]


@pytest.mark.django_db
def test_patch_auth_other(fake_mailbox, other_apiClient, mailboxPayload, detail_url):
    """Tests the patch method on :class:`api.v1.views.MailboxViewSet.MailboxViewSet` with the authenticated other user client."""
    response = other_apiClient.patch(
        detail_url(MailboxViewSet, fake_mailbox), data=mailboxPayload
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    with pytest.raises(KeyError):
        response.data["save_attachments"]
    fake_mailbox.refresh_from_db()
    assert fake_mailbox.save_attachments is not mailboxPayload["save_attachments"]


@pytest.mark.django_db
def test_patch_auth_owner(fake_mailbox, owner_apiClient, mailboxPayload, detail_url):
    """Tests the patch method on :class:`api.v1.views.MailboxViewSet.MailboxViewSet` with the authenticated owner user client."""
    response = owner_apiClient.patch(
        detail_url(MailboxViewSet, fake_mailbox), data=mailboxPayload
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.data["save_attachments"] is False
    fake_mailbox.refresh_from_db()
    assert fake_mailbox.save_attachments is mailboxPayload["save_attachments"]


@pytest.mark.django_db
def test_put_noauth(fake_mailbox, noauth_apiClient, mailboxPayload, detail_url):
    """Tests the put method on :class:`api.v1.views.MailboxViewSet.MailboxViewSet` with an unauthenticated user client."""
    response = noauth_apiClient.put(
        detail_url(MailboxViewSet, fake_mailbox), data=mailboxPayload
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["save_attachments"]
    fake_mailbox.refresh_from_db()
    assert fake_mailbox.save_attachments != mailboxPayload["save_attachments"]


@pytest.mark.django_db
def test_put_auth_other(fake_mailbox, other_apiClient, mailboxPayload, detail_url):
    """Tests the put method on :class:`api.v1.views.MailboxViewSet.MailboxViewSet` with the authenticated other user client."""
    response = other_apiClient.put(
        detail_url(MailboxViewSet, fake_mailbox), data=mailboxPayload
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    with pytest.raises(KeyError):
        response.data["save_attachments"]
    fake_mailbox.refresh_from_db()
    assert fake_mailbox.save_attachments != mailboxPayload["save_attachments"]


@pytest.mark.django_db
def test_put_auth_owner(fake_mailbox, owner_apiClient, mailboxPayload, detail_url):
    """Tests the put method on :class:`api.v1.views.MailboxViewSet.MailboxViewSet` with the authenticated owner user client."""
    response = owner_apiClient.put(
        detail_url(MailboxViewSet, fake_mailbox), data=mailboxPayload
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["save_attachments"] == mailboxPayload["save_attachments"]
    fake_mailbox.refresh_from_db()
    assert fake_mailbox.save_attachments == mailboxPayload["save_attachments"]


@pytest.mark.django_db
def test_post_noauth(noauth_apiClient, mailboxPayload, list_url):
    """Tests the post method on :class:`api.v1.views.MailboxViewSet.MailboxViewSet` with an unauthenticated user client."""
    response = noauth_apiClient.post(list_url(MailboxViewSet), data=mailboxPayload)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    with pytest.raises(KeyError):
        response.data["save_attachments"]
    with pytest.raises(Mailbox.DoesNotExist):
        Mailbox.objects.get(save_attachments=mailboxPayload["save_attachments"])


@pytest.mark.django_db
def test_post_auth_other(other_apiClient, mailboxPayload, list_url):
    """Tests the post method on :class:`api.v1.views.MailboxViewSet.MailboxViewSet` with the authenticated other user client."""
    response = other_apiClient.post(list_url(MailboxViewSet), data=mailboxPayload)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data["save_attachments"]
    with pytest.raises(Mailbox.DoesNotExist):
        Mailbox.objects.get(save_attachments=mailboxPayload["save_attachments"])


@pytest.mark.django_db
def test_post_auth_owner(owner_apiClient, mailboxPayload, list_url):
    """Tests the post method on :class:`api.v1.views.MailboxViewSet.MailboxViewSet` with the authenticated owner user client."""
    response = owner_apiClient.post(list_url(MailboxViewSet), data=mailboxPayload)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    with pytest.raises(KeyError):
        response.data["save_attachments"]
    with pytest.raises(Mailbox.DoesNotExist):
        Mailbox.objects.get(save_attachments=mailboxPayload["save_attachments"])


@pytest.mark.django_db
def test_delete_noauth(fake_mailbox, noauth_apiClient, detail_url):
    """Tests the delete method on :class:`api.v1.views.MailboxViewSet.MailboxViewSet` with an unauthenticated user client."""
    response = noauth_apiClient.delete(detail_url(MailboxViewSet, fake_mailbox))

    assert response.status_code == status.HTTP_403_FORBIDDEN
    fake_mailbox.refresh_from_db()
    assert fake_mailbox.name is not None


@pytest.mark.django_db
def test_delete_auth_other(fake_mailbox, other_apiClient, detail_url):
    """Tests the delete method on :class:`api.v1.views.MailboxViewSet.MailboxViewSet` with the authenticated other user client."""
    response = other_apiClient.delete(detail_url(MailboxViewSet, fake_mailbox))

    assert response.status_code == status.HTTP_404_NOT_FOUND
    fake_mailbox.refresh_from_db()
    assert fake_mailbox.name is not None


@pytest.mark.django_db
def test_delete_auth_owner(fake_mailbox, owner_apiClient, detail_url):
    """Tests the delete method on :class:`api.v1.views.MailboxViewSet.MailboxViewSet` with the authenticated owner user client."""
    response = owner_apiClient.delete(detail_url(MailboxViewSet, fake_mailbox))

    assert response.status_code == status.HTTP_204_NO_CONTENT
    with pytest.raises(fake_mailbox.DoesNotExist):
        fake_mailbox.refresh_from_db()
