from django.db import models

class CorrespondentModel(models.Model):
    emailName = models.CharField(max_length=255)
    emailAddress = models.MailField(not_null=True, unique=True)

    def __str__(self):
        return f"Correspondent with address {self.emailAddress}"