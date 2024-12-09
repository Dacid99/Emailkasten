# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import os
import pytest
import email.message
import Emailkasten.fileManagment
from Emailkasten.constants import ParsedMailKeys
from unittest.mock import patch, call
from pyfakefs.fake_filesystem_unittest import Patcher

@pytest.fixture
def mock_logger(mocker):
    return mocker.patch('Emailkasten.fileManagment.logger')

@pytest.fixture
def mock_parsedMailDict():
    message = email.message.Message()
    message.add_header('test', "Test message")
    message.set_payload('This is a test mail message.')

    mock_dict = {
        ParsedMailKeys.Header.MESSAGE_ID: 'abc123',
        ParsedMailKeys.FULL_MESSAGE: message
    }
    return mock_dict

@pytest.fixture
def mock_filesystem():
    with Patcher() as patcher:
        patcher.fs.create_dir("/dir")
        patcher.fs.chmod("/dir", 0o777)
        patcher.fs.create_file("/dir/full_file", contents="Im not empty!")
        patcher.fs.create_file("/dir/empty_file", contents="")
        patcher.fs.create_file("/dir/broken_file", contents="", side_effect=OSError)

        patcher.fs.create_file("/dir/no_write_file", contents="")
        patcher.fs.chmod("/dir/no_write_file", 0o555)

        patcher.fs.create_file("/dir/no_read_file", contents="")
        patcher.fs.chmod("/dir/no_read_file", 0o333)

        patcher.fs.create_file("/dir/no_readwrite_file", contents="")
        patcher.fs.chmod("/dir/no_readwrite_file", 0o111)

        patcher.fs.create_file("/dir/no_access_file", contents="")
        patcher.fs.chmod("/dir/no_access_file", 0o000)

        patcher.fs.create_dir("/no_access_dir")
        patcher.fs.create_file("/no_access_dir/file", contents="")
        patcher.fs.chmod("/no_access_dir", 0o000)
        yield patcher.fs


@pytest.mark.parametrize(
        'fakeFile, expectedFileExists, expectedFileSize, expectedEMLFilePath, expectedCallsToOpen, expectedErrors',
        [
            ("/dir/new_file", True, 48, "/dir/new_file", 1, 0),
            ("/dir/full_file", True, 13, "/dir/full_file", 0, 0),
            ("/dir/empty_file", True, 48, "/dir/empty_file", 1, 0),
            ("/dir/broken_file", True, 0, None, 1, 2),
            ("/dir/no_write_file", True, 0, None, 1, 1),
            ("/dir/no_read_file", True, 48, "/dir/no_read_file", 1, 0),
            ("/dir/no_readwrite_file", True, 0, None, 1, 1),
            ("/dir/no_access_file", True, 0, None, 1, 1),
            ("/no_access_dir/new_file", False, 0, None, 1, 1),
            ("/no_access_dir/file", True, 0, None, 1, 1)
        ]
)
@patch('Emailkasten.fileManagment.StorageModel.getSubdirectory', return_value = 'unnecessary')
def test_storeMessageAsEML(mock_storageModel, mock_logger, mock_filesystem, mock_parsedMailDict, fakeFile, expectedFileExists, expectedFileSize, expectedEMLFilePath, expectedCallsToOpen, expectedErrors, mocker):
    mock_ospathjoin = mocker.patch('os.path.join', return_value = fakeFile)
    spy_open = mocker.spy(Emailkasten.fileManagment, 'open')

    Emailkasten.fileManagment.storeMessageAsEML(mock_parsedMailDict)

    mock_storageModel.assert_called_once()
    mock_ospathjoin.assert_called_once_with('unnecessary', 'abc123.eml')

    mock_filesystem.chmod(os.path.dirname(fakeFile), 0o777)
    assert mock_filesystem.exists(fakeFile) is expectedFileExists
    if mock_filesystem.exists(fakeFile):
        mock_filesystem.chmod(fakeFile, 0o666)
        assert mock_filesystem.get_object(fakeFile).size == expectedFileSize

    assert mock_parsedMailDict.get(ParsedMailKeys.EML_FILE_PATH) == expectedEMLFilePath
    assert spy_open.call_count == expectedCallsToOpen
    spy_open.assert_has_calls( [call(fakeFile, "wb")] * expectedCallsToOpen )
    assert mock_logger.error.call_count == expectedErrors

    mock_logger.debug.assert_called()
