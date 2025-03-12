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

"""Test module for :mod:`api.v1.views.EMailViewSet`'s custom actions."""

from __future__ import annotations

import os

import pytest
from rest_framework import status

from api.v1.views.EMailViewSet import EMailViewSet


@pytest.mark.django_db
def test_download_noauth(
    mocker, emailModel, noauth_apiClient, custom_detail_action_url
):
    """Tests the get method :func:`api.v1.views.EMailViewSet.EMailViewSet.download` action with an unauthenticated user client."""
    mock_open = mocker.patch("api.v1.views.EMailViewSet.open")
    mock_os_path_exists = mocker.patch(
        "api.v1.views.EMailViewSet.os.path.exists", autospec=True, return_value=False
    )

    response = noauth_apiClient.get(
        custom_detail_action_url(
            EMailViewSet, EMailViewSet.URL_NAME_DOWNLOAD, emailModel
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_open.assert_not_called()
    mock_os_path_exists.assert_not_called()


@pytest.mark.django_db
def test_download_auth_other(
    mocker, emailModel, other_apiClient, custom_detail_action_url
):
    """Tests the get method :func:`api.v1.views.EMailViewSet.EMailViewSet.download` action with the authenticated other user client."""
    mock_open = mocker.patch("api.v1.views.EMailViewSet.open")
    mock_os_path_exists = mocker.patch(
        "api.v1.views.EMailViewSet.os.path.exists", autospec=True, return_value=False
    )

    response = other_apiClient.get(
        custom_detail_action_url(
            EMailViewSet, EMailViewSet.URL_NAME_DOWNLOAD, emailModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_open.assert_not_called()
    mock_os_path_exists.assert_not_called()


@pytest.mark.django_db
def test_download_no_file_auth_owner(
    mocker, emailModel, owner_apiClient, custom_detail_action_url
):
    """Tests the get method :func:`api.v1.views.EMailViewSet.EMailViewSet.download` action with the authenticated owner user client."""
    mock_open = mocker.patch("api.v1.views.EMailViewSet.open")
    mock_os_path_exists = mocker.patch(
        "api.v1.views.EMailViewSet.os.path.exists", autospec=True, return_value=False
    )

    response = owner_apiClient.get(
        custom_detail_action_url(
            EMailViewSet, EMailViewSet.URL_NAME_DOWNLOAD, emailModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_open.assert_not_called()
    mock_os_path_exists.assert_called_once_with(emailModel.eml_filepath)


@pytest.mark.django_db
def test_download_auth_owner(
    mocker, emailModel, owner_apiClient, custom_detail_action_url
):
    """Tests the get method :func:`api.v1.views.EMailViewSet.EMailViewSet.download` action with the authenticated owner user client."""
    mockedFileContent = b"This is a 24 bytes file."
    mock_open = mocker.mock_open(read_data=mockedFileContent)
    mocker.patch("api.v1.views.EMailViewSet.open", mock_open)
    mock_os_path_exists = mocker.patch(
        "api.v1.views.EMailViewSet.os.path.exists", autospec=True, return_value=True
    )

    response = owner_apiClient.get(
        custom_detail_action_url(
            EMailViewSet, EMailViewSet.URL_NAME_DOWNLOAD, emailModel
        )
    )

    assert response.status_code == status.HTTP_200_OK
    mock_os_path_exists.assert_called_once_with(emailModel.eml_filepath)
    mock_open.assert_called_once_with(emailModel.eml_filepath, "rb")
    assert "Content-Disposition" in response.headers
    assert (
        f'filename="{os.path.basename(emailModel.eml_filepath)}"'
        in response["Content-Disposition"]
    )
    assert b"".join(response.streaming_content) == mockedFileContent


@pytest.mark.django_db
def test_prerender_noauth(
    mocker, emailModel, noauth_apiClient, custom_detail_action_url
):
    """Tests the get method :func:`api.v1.views.EMailViewSet.EMailViewSet.prerender` action with an unauthenticated user client."""
    mock_open = mocker.patch("api.v1.views.EMailViewSet.open")
    mock_os_path_exists = mocker.patch(
        "api.v1.views.EMailViewSet.os.path.exists", autospec=True, return_value=True
    )

    response = noauth_apiClient.get(
        custom_detail_action_url(
            EMailViewSet, EMailViewSet.URL_NAME_PRERENDER, emailModel
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_open.assert_not_called()
    mock_os_path_exists.assert_not_called()


@pytest.mark.django_db
def test_prerender_auth_other(
    mocker, emailModel, other_apiClient, custom_detail_action_url
):
    """Tests the get method :func:`api.v1.views.EMailViewSet.EMailViewSet.prerender` action with the authenticated other user client."""
    mock_open = mocker.patch("api.v1.views.EMailViewSet.open")
    mock_os_path_exists = mocker.patch(
        "api.v1.views.EMailViewSet.os.path.exists", autospec=True, return_value=True
    )

    response = other_apiClient.get(
        custom_detail_action_url(
            EMailViewSet, EMailViewSet.URL_NAME_PRERENDER, emailModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_open.assert_not_called()
    mock_os_path_exists.assert_not_called()


@pytest.mark.django_db
def test_prerender_no_file_auth_owner(
    mocker, emailModel, owner_apiClient, custom_detail_action_url
):
    """Tests the get method :func:`api.v1.views.EMailViewSet.EMailViewSet.prerender` action with the authenticated owner user client."""
    mock_open = mocker.patch("api.v1.views.EMailViewSet.open")
    mock_os_path_exists = mocker.patch(
        "api.v1.views.EMailViewSet.os.path.exists", autospec=True, return_value=False
    )

    response = owner_apiClient.get(
        custom_detail_action_url(
            EMailViewSet, EMailViewSet.URL_NAME_PRERENDER, emailModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_open.assert_not_called()
    mock_os_path_exists.assert_called_once_with(emailModel.prerender_filepath)


@pytest.mark.django_db
def test_prerender_auth_owner(
    mocker, emailModel, owner_apiClient, custom_detail_action_url
):
    """Tests the get method :func:`api.v1.views.EMailViewSet.EMailViewSet.prerender` action with the authenticated owner user client."""
    mockedFileContent = b"This is a 24 bytes file."
    mock_open = mocker.mock_open(read_data=mockedFileContent)
    mocker.patch("api.v1.views.EMailViewSet.open", mock_open)
    mock_os_path_exists = mocker.patch(
        "api.v1.views.EMailViewSet.os.path.exists", autospec=True, return_value=True
    )

    response = owner_apiClient.get(
        custom_detail_action_url(
            EMailViewSet, EMailViewSet.URL_NAME_PRERENDER, emailModel
        )
    )

    assert response.status_code == status.HTTP_200_OK
    mock_os_path_exists.assert_called_once_with(emailModel.prerender_filepath)
    mock_open.assert_called_once_with(emailModel.prerender_filepath, "rb")
    assert "Content-Disposition" in response.headers
    assert (
        f'filename="{os.path.basename(emailModel.prerender_filepath)}"'
        in response["Content-Disposition"]
    )
    assert b"".join(response.streaming_content) == mockedFileContent


@pytest.mark.django_db
def test_subConversation_noauth(
    mocker, emailModel, noauth_apiClient, custom_detail_action_url
):
    """Tests the get method :func:`api.v1.views.EMailViewSet.EMailViewSet.download` action with an unauthenticated user client."""
    mock_subConversation = mocker.patch(
        "api.v1.views.EMailViewSet.EMailModel.subConversation", autospec=True
    )

    response = noauth_apiClient.get(
        custom_detail_action_url(
            EMailViewSet, EMailViewSet.URL_NAME_SUBCONVERSATION, emailModel
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_subConversation.assert_not_called()


@pytest.mark.django_db
def test_subConversation_auth_other(
    mocker, emailModel, other_apiClient, custom_detail_action_url
):
    """Tests the get method :func:`api.v1.views.EMailViewSet.EMailViewSet.download` action with the authenticated other user client."""
    mock_subConversation = mocker.patch(
        "api.v1.views.EMailViewSet.EMailModel.subConversation", autospec=True
    )

    response = other_apiClient.get(
        custom_detail_action_url(
            EMailViewSet, EMailViewSet.URL_NAME_SUBCONVERSATION, emailModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_subConversation.assert_not_called()


@pytest.mark.django_db
def test_subConversation_auth_owner(
    mocker, emailModel, owner_apiClient, custom_detail_action_url
):
    """Tests the get method :func:`api.v1.views.EMailViewSet.EMailViewSet.download` action with the authenticated owner user client."""
    mock_subConversation = mocker.patch(
        "api.v1.views.EMailViewSet.EMailModel.subConversation",
        autospec=True,
        return_value=[emailModel],
    )

    response = owner_apiClient.get(
        custom_detail_action_url(
            EMailViewSet, EMailViewSet.URL_NAME_SUBCONVERSATION, emailModel
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["emails"]) == 1
    assert response.data["emails"][0]["id"] == emailModel.id
    mock_subConversation.assert_called_once_with(emailModel)


@pytest.mark.django_db
def test_fullConversation_noauth(
    mocker, emailModel, noauth_apiClient, custom_detail_action_url
):
    """Tests the get method :func:`api.v1.views.EMailViewSet.EMailViewSet.download` action with an unauthenticated user client."""
    mock_fullConversation = mocker.patch(
        "api.v1.views.EMailViewSet.EMailModel.fullConversation", autospec=True
    )

    response = noauth_apiClient.get(
        custom_detail_action_url(
            EMailViewSet, EMailViewSet.URL_NAME_FULLCONVERSATION, emailModel
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    mock_fullConversation.assert_not_called()


@pytest.mark.django_db
def test_fullConversation_auth_other(
    mocker, emailModel, other_apiClient, custom_detail_action_url
):
    """Tests the get method :func:`api.v1.views.EMailViewSet.EMailViewSet.download` action with the authenticated other user client."""
    mock_fullConversation = mocker.patch(
        "api.v1.views.EMailViewSet.EMailModel.fullConversation", autospec=True
    )

    response = other_apiClient.get(
        custom_detail_action_url(
            EMailViewSet, EMailViewSet.URL_NAME_FULLCONVERSATION, emailModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    mock_fullConversation.assert_not_called()


@pytest.mark.django_db
def test_fullConversation_auth_owner(
    mocker, emailModel, owner_apiClient, custom_detail_action_url
):
    """Tests the get method :func:`api.v1.views.EMailViewSet.EMailViewSet.download` action with the authenticated owner user client."""
    mock_fullConversation = mocker.patch(
        "api.v1.views.EMailViewSet.EMailModel.fullConversation",
        autospec=True,
        return_value=[emailModel],
    )

    response = owner_apiClient.get(
        custom_detail_action_url(
            EMailViewSet, EMailViewSet.URL_NAME_FULLCONVERSATION, emailModel
        )
    )

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["emails"]) == 1
    assert response.data["emails"][0]["id"] == emailModel.id
    mock_fullConversation.assert_called_once_with(emailModel)


@pytest.mark.django_db
def test_toggle_favorite_noauth(emailModel, noauth_apiClient, custom_detail_action_url):
    """Tests the post method :func:`api.v1.views.EMailViewSet.EMailViewSet.toggle_favorite` action with an unauthenticated user client."""
    response = noauth_apiClient.post(
        custom_detail_action_url(
            EMailViewSet, EMailViewSet.URL_NAME_TOGGLE_FAVORITE, emailModel
        )
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    emailModel.refresh_from_db()
    assert emailModel.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_other(
    emailModel, other_apiClient, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.EMailViewSet.EMailViewSet.toggle_favorite` action with the authenticated other user client."""
    response = other_apiClient.post(
        custom_detail_action_url(
            EMailViewSet, EMailViewSet.URL_NAME_TOGGLE_FAVORITE, emailModel
        )
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    emailModel.refresh_from_db()
    assert emailModel.is_favorite is False


@pytest.mark.django_db
def test_toggle_favorite_auth_owner(
    emailModel, owner_apiClient, custom_detail_action_url
):
    """Tests the post method :func:`api.v1.views.EMailViewSet.EMailViewSet.toggle_favorite` action with the authenticated owner user client."""
    response = owner_apiClient.post(
        custom_detail_action_url(
            EMailViewSet, EMailViewSet.URL_NAME_TOGGLE_FAVORITE, emailModel
        )
    )

    assert response.status_code == status.HTTP_200_OK
    emailModel.refresh_from_db()
    assert emailModel.is_favorite is True
