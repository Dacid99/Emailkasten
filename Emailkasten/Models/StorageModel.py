'''
    Emailkasten - a open-source self-hostable email archiving server
    Copyright (C) 2024  David & Philipp Aderbauer

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

from django.db import models
import logging
import os
from .. import constants

logger = logging.getLogger(__name__)


class StorageModel(models.Model):
    directory_number = models.PositiveIntegerField(unique=True)
    path = models.FilePathField(unique=True, path=constants.StorageConfiguration.STORAGE_PATH)
    subdirectory_count = models.SmallIntegerField(default=0)
    current = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    def __str__(self):
        state = "Current" if self.current else "Archived"
        return f"{state} storage directory {self.path}"
    

    def save(self):
        if self.current and StorageModel.objects.filter(current=True):
            logger.critical("More than one current storage directories!!")
        if not self.path:
            self.path = os.path.join(constants.StorageConfiguration.STORAGE_PATH, self.directory_number)
        super().save()


    def incrementSubdirectoryCount(self):
        self.subdirectory_count += 1
        if (self.subdirectory_count >= constants.StorageConfiguration.MAX_SUBDIRS_PER_DIR):
            self.__addNewDirectory()
        else:
            self.save()


    def __addNewDirectory(self):
        self.current = False
        self.save()
        
        newStorageEntry = StorageModel.objects.create(directory_number=self.directory_number+1, current=True, subdirectory_count=0)


    class Meta:
        db_table = "storage"


    @staticmethod
    def getStoragePath(increment=False):
        storageEntry = StorageModel.objects.filter(current=True).first()
        if not storageEntry:
            storageEntry = StorageModel.objects.create(directory_number=0, current=True, subdirectory_count=0)

        if increment:
            storageEntry.incrementSubdirectoryCount()
        return storageEntry.path 


