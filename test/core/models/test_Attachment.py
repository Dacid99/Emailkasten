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

"""Test module for :mod:`core.models.Attachment`."""

import datetime
import email
import os
from zipfile import ZipFile

import django.db.models
import pytest
from django.db import IntegrityError
from django.urls import reverse
from model_bakery import baker

from core.models import Attachment, Email

from ...conftest import TEST_EMAIL_PARAMETERS


@pytest.fixture(autouse=True)
def mock_logger(mocker):
    """Fixture mocking the logger :attr:`core.models.Attachment.logger` of the module."""
    return mocker.patch("core.models.Attachment.logger", autospec=True)


@pytest.fixture
def mock_open(mocker, fake_file_bytes):
    """Fixture to mock the builtin :func:`open`."""
    mock_open = mocker.mock_open(read_data=fake_file_bytes)
    mocker.patch("core.utils.file_managment.open", mock_open)
    return mock_open


@pytest.fixture
def mock_Storage_get_subdirectory(mocker, faker):
    fake_directory_path = os.path.dirname(faker.file_path())
    mock_Storage_get_subdirectory = mocker.patch(
        "core.models.Storage.Storage.get_subdirectory", autospec=True
    )
    mock_Storage_get_subdirectory.return_value = fake_directory_path
    return mock_Storage_get_subdirectory


@pytest.fixture
def mock_Attachment_save_to_storage(mocker):
    return mocker.patch(
        "core.models.Attachment.Attachment.save_to_storage", autospec=True
    )


@pytest.fixture
def spy__save(mocker):
    return mocker.spy(django.db.models.Model, "save")


@pytest.mark.django_db
def test_Attachment_fields(fake_attachment):
    """Tests the fields of :class:`core.models.Attachment.Attachment`."""

    assert fake_attachment.file_name is not None
    assert isinstance(fake_attachment.file_name, str)
    assert fake_attachment.file_path is not None
    assert isinstance(fake_attachment.file_path, str)
    assert fake_attachment.datasize is not None
    assert isinstance(fake_attachment.datasize, int)
    assert fake_attachment.is_favorite is False
    assert fake_attachment.email is not None
    assert isinstance(fake_attachment.email, Email)
    assert fake_attachment.updated is not None
    assert isinstance(fake_attachment.updated, datetime.datetime)
    assert fake_attachment.created is not None
    assert isinstance(fake_attachment.created, datetime.datetime)


@pytest.mark.django_db
def test_Attachment___str__(fake_attachment):
    """Tests the string representation of :class:`core.models.Attachment.Attachment`."""
    assert fake_attachment.file_name in str(fake_attachment)
    assert str(fake_attachment.email) in str(fake_attachment)


@pytest.mark.django_db
def test_Attachment_foreign_key_deletion(fake_attachment):
    """Tests the on_delete foreign key constraint in :class:`core.models.Attachment.Attachment`."""

    assert fake_attachment is not None
    fake_attachment.email.delete()
    with pytest.raises(Attachment.DoesNotExist):
        fake_attachment.refresh_from_db()


@pytest.mark.django_db
def test_Attachment_unique_constraints():
    """Tests the unique constraints of :class:`core.models.Attachment.Attachment`."""

    attachment_1 = baker.make(Attachment, file_path="test")
    attachment_2 = baker.make(Attachment, file_path="test")
    assert attachment_1.file_path == attachment_2.file_path
    assert attachment_1.email != attachment_2.email

    email = baker.make(Email, x_spam="NO")

    attachment_1 = baker.make(Attachment, file_path="path_1", email=email)
    attachment_2 = baker.make(Attachment, file_path="path_2", email=email)
    assert attachment_1.file_path != attachment_2.file_path
    assert attachment_1.email == attachment_2.email

    baker.make(Attachment, file_path="test", email=email)
    with pytest.raises(IntegrityError):
        baker.make(Attachment, file_path="test", email=email)


@pytest.mark.django_db
def test_Attachment_delete_attachmentfile_success(
    fake_attachment, mock_logger, mock_os_remove
):
    """Tests :func:`core.models.Attachment.Attachment.delete`
    in case the file removal is successful.
    """
    file_path = fake_attachment.file_path

    fake_attachment.delete()

    with pytest.raises(Attachment.DoesNotExist):
        fake_attachment.refresh_from_db()
    mock_os_remove.assert_called_with(file_path)
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.error.assert_not_called()
    mock_logger.critical.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize("side_effect", [FileNotFoundError, OSError, Exception])
def test_Attachment_delete_attachmentfile_failure(
    fake_attachment, mock_logger, mock_os_remove, side_effect
):
    """Tests :func:`core.models.Attachment.Attachment.delete`
    in case the file removal raises an exception.
    """
    mock_os_remove.side_effect = side_effect
    file_path = fake_attachment.file_path

    fake_attachment.delete()

    mock_os_remove.assert_called_with(file_path)
    with pytest.raises(Attachment.DoesNotExist):
        fake_attachment.refresh_from_db()
    mock_logger.debug.assert_called()
    mock_logger.warning.assert_not_called()
    mock_logger.exception.assert_called()
    mock_logger.critical.assert_not_called()


@pytest.mark.django_db
def test_Attachment_delete_attachmentfile_delete_error(
    mocker,
    fake_attachment,
    mock_logger,
    mock_os_remove,
):
    """Tests :func:`core.models.Attachment.Attachment.delete`
    in case delete raises an exception.
    """
    mock_delete = mocker.patch(
        "core.models.Attachment.models.Model.delete",
        autospec=True,
        side_effect=AssertionError,
    )

    with pytest.raises(AssertionError):
        fake_attachment.delete()

    mock_delete.assert_called_once()
    mock_os_remove.assert_not_called()
    mock_logger.debug.assert_not_called()


@pytest.mark.django_db
def test_save_to_storage_success(
    fake_file_bytes,
    fake_attachment,
    mock_logger,
    mock_open,
    mock_Storage_get_subdirectory,
):
    fake_attachment.file_path = None

    fake_attachment.save_to_storage(fake_file_bytes)

    mock_Storage_get_subdirectory.assert_called_once_with(
        fake_attachment.email.message_id
    )
    mock_open.assert_called_once_with(
        os.path.join(
            mock_Storage_get_subdirectory.return_value, fake_attachment.file_name
        ),
        "wb",
    )
    mock_open.return_value.write.assert_called_once_with(fake_file_bytes)
    fake_attachment.refresh_from_db()
    assert fake_attachment.file_path == os.path.join(
        mock_Storage_get_subdirectory.return_value, fake_attachment.file_name
    )
    mock_logger.debug.assert_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_save_to_storage_file_path_set(
    faker,
    mock_message,
    fake_attachment,
    mock_logger,
    mock_open,
    mock_Storage_get_subdirectory,
):
    fake_message_payload = faker.text().encode()
    mock_message.get_payload.return_value = fake_message_payload
    previous_file_path = fake_attachment.file_path

    fake_attachment.save_to_storage(mock_message)

    mock_Storage_get_subdirectory.assert_not_called()
    mock_open.assert_not_called()
    fake_attachment.refresh_from_db()
    assert fake_attachment.file_path == previous_file_path
    mock_logger.debug.assert_called()
    mock_logger.error.assert_not_called()


@pytest.mark.django_db
def test_save_to_storage_open_os_error(
    fake_file_bytes,
    fake_attachment,
    mock_logger,
    mock_open,
    mock_Storage_get_subdirectory,
):
    fake_attachment.file_path = None
    mock_open.side_effect = OSError

    fake_attachment.save_to_storage(fake_file_bytes)

    mock_Storage_get_subdirectory.assert_called_once_with(
        fake_attachment.email.message_id
    )
    mock_open.assert_called_once_with(
        os.path.join(
            mock_Storage_get_subdirectory.return_value, fake_attachment.file_name
        ),
        "wb",
    )
    mock_open.return_value.write.assert_not_called()
    assert fake_attachment.file_path is None
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
def test_save_to_storage_write_os_error(
    fake_file_bytes,
    mock_message,
    fake_attachment,
    mock_logger,
    mock_open,
    mock_Storage_get_subdirectory,
):
    fake_attachment.file_path = None
    mock_open.return_value.write.side_effect = OSError

    fake_attachment.save_to_storage(fake_file_bytes)

    mock_Storage_get_subdirectory.assert_called_once_with(
        fake_attachment.email.message_id
    )
    mock_open.assert_called_once_with(
        os.path.join(
            mock_Storage_get_subdirectory.return_value, fake_attachment.file_name
        ),
        "wb",
    )
    mock_open.return_value.write.assert_called_once_with(fake_file_bytes)
    assert fake_attachment.file_path is None
    mock_logger.debug.assert_called()
    mock_logger.error.assert_called()


@pytest.mark.django_db
@pytest.mark.parametrize("save_attachments, expected_calls", [(True, 1), (False, 0)])
def test_Attachment_save_with_data_success(
    fake_attachment,
    fake_file_bytes,
    mock_Attachment_save_to_storage,
    spy__save,
    save_attachments,
    expected_calls,
):
    """Tests :func:`core.models.Attachment.Attachment.save`
    in case of success with data to be saved.
    """
    fake_attachment.email.mailbox.save_attachments = save_attachments

    fake_attachment.save(attachment_payload=fake_file_bytes)

    assert mock_Attachment_save_to_storage.call_count == expected_calls
    spy__save.assert_called()


@pytest.mark.django_db
def test_Attachment_save_no_data(
    fake_attachment, mock_Attachment_save_to_storage, spy__save
):
    """Tests :func:`core.models.Attachment.Attachment.save`
    in case of success without data to be saved.
    """
    fake_attachment.email.mailbox.save_attachment_models = True

    fake_attachment.save()

    spy__save.assert_called_once_with(fake_attachment)
    mock_Attachment_save_to_storage.assert_not_called()


@pytest.mark.django_db
def test_Attachment_save_with_data_failure(
    fake_attachment,
    fake_file_bytes,
    mock_Attachment_save_to_storage,
    spy__save,
):
    """Tests :func:`core.models.Attachment.Attachment.save`
    in case of the data fails to be saved.
    """
    mock_Attachment_save_to_storage.side_effect = AssertionError
    fake_attachment.email.mailbox.save_attachment_models = True

    with pytest.raises(AssertionError):
        fake_attachment.save(attachment_payload=fake_file_bytes)

    spy__save.assert_called()
    mock_Attachment_save_to_storage.assert_called()


@pytest.mark.django_db
def test_Attachment_queryset_as_file(
    fake_file, fake_attachment, fake_attachment_with_file
):
    assert Attachment.objects.count() == 2

    result = Attachment.queryset_as_file(Attachment.objects.all())

    assert Attachment.objects.count() == 2
    assert hasattr(result, "read")
    with ZipFile(result) as zipfile:
        assert zipfile.namelist() == [
            os.path.basename(fake_attachment_with_file.file_path)
        ]
        with zipfile.open(
            os.path.basename(fake_attachment_with_file.file_path)
        ) as zipped_file:
            assert zipped_file.read().strip() == fake_file.getvalue().strip()
    assert hasattr(result, "close")
    result.close()
    assert os.listdir("/tmp") == []


@pytest.mark.django_db
def test_Attachment_queryset_as_file_mailbox_empty_queryset():
    assert Attachment.objects.count() == 0

    with pytest.raises(Attachment.DoesNotExist):
        Attachment.queryset_as_file(Attachment.objects.none())

    assert Attachment.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    "test_email_path, expected_email_features, expected_correspondents_features,expected_attachments_features",
    TEST_EMAIL_PARAMETERS,
)
def test_Attachment_from_data(
    fake_email,
    mock_Attachment_save_to_storage,
    test_email_path,
    expected_email_features,
    expected_correspondents_features,
    expected_attachments_features,
):
    """Tests :func:`core.models.Attachment.Attachment.from_data`
    in case of success.
    """
    with open(test_email_path, "br") as f:
        test_email_bytes = f.read()
    test_email_message = email.message_from_bytes(test_email_bytes)

    result = Attachment.create_from_email_message(test_email_message, fake_email)

    assert isinstance(result, list)
    assert all(isinstance(item, Attachment) for item in result)
    assert len(result) == len(expected_attachments_features)
    for item in result:
        assert item.pk is not None
        assert item.file_name in expected_attachments_features
        assert (
            item.content_disposition
            == expected_attachments_features[item.file_name]["content_disposition"]
        )
        assert (
            item.content_maintype
            == expected_attachments_features[item.file_name]["content_maintype"]
        )
        assert (
            item.content_subtype
            == expected_attachments_features[item.file_name]["content_subtype"]
        )
        assert (
            item.content_id
            == expected_attachments_features[item.file_name]["content_id"]
        )
    assert mock_Attachment_save_to_storage.call_count == len(
        expected_attachments_features
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "file_path, expected_has_download",
    [
        (None, False),
        ("some/file/path", True),
    ],
)
def test_Attachment_has_download(fake_attachment, file_path, expected_has_download):
    """Tests :func:`core.models.Attachment.Attachment.has_download` in the two relevant cases."""
    fake_attachment.file_path = file_path

    result = fake_attachment.has_download

    assert result == expected_has_download


@pytest.mark.django_db
@pytest.mark.parametrize(
    "content_maintype, expected_has_thumbnail",
    [
        ("", False),
        ("oo4vuy0s9yn", False),
        ("image", True),
        ("video", False),
        ("application", False),
    ],
)
def test_Attachment_has_thumbnail(
    fake_attachment, content_maintype, expected_has_thumbnail
):
    """Tests :func:`core.models.Attachment.Attachment.has_thumbnail` in the two relevant cases."""
    fake_attachment.content_maintype = content_maintype

    result = fake_attachment.has_thumbnail

    assert result == expected_has_thumbnail


@pytest.mark.django_db
def test_Attachment_get_absolute_thumbnail_url(fake_attachment):
    """Tests :func:`core.models.Attachment.Attachment.get_absolute_thumbnail_url`."""
    result = fake_attachment.get_absolute_thumbnail_url()

    assert result == reverse(
        f"api:v1:{fake_attachment.BASENAME}-download",
        kwargs={"pk": fake_attachment.pk},
    )


@pytest.mark.django_db
def test_Attachment_get_absolute_url(fake_attachment):
    """Tests :func:`core.models.Attachment.Attachment.get_absolute_url`."""
    result = fake_attachment.get_absolute_url()

    assert result == reverse(
        f"web:{fake_attachment.BASENAME}-detail",
        kwargs={"pk": fake_attachment.pk},
    )


@pytest.mark.django_db
def test_Attachment_get_absolute_list_url(fake_attachment):
    """Tests :func:`core.models.Attachment.Attachment.get_absolute_list_url`."""
    result = fake_attachment.get_absolute_list_url()

    assert result == reverse(f"web:{fake_attachment.BASENAME}-filter-list")
