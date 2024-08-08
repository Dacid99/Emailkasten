from django.db import models
from FileManager import FileManager

class EMailModel(models.Model):
    messageID = models.CharField(max_length=255, unique=True, not_null=True)
    dateReceived = models.DateTimeField(not_null=True)
    subject = models.CharField(max_length=255, not_null=True)
    bodyText = models.TextField(not_null=True)
    emlFile = models.FilePathField(
        path=FileManager.emlDirectoryPath, 
        recursive=True, 
        match='.*\.eml$', 
        blank=True, 
        not_null=True
    )

    def __str__(self):
        return f"Email with ID {self.messageID}, received on {self.dateReceived} with subject {self.subject}"