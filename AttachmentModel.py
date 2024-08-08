from django.db import models
from FileManager import FileManager

class AttachmentModel(models.Model):
    fileName = models.CharField(max_length=255)
    filePath = models.FilePathField(
        path=FileManager.attachmentDirectoryPath,
        recursive=True, 
        not_null=True,
        blank=True,  
        unique=True)
    emailID = models.ForeignKey(on_delete=models.CASCADE)

    def __str__(self):
        return f"Attachment {self.fileName}"