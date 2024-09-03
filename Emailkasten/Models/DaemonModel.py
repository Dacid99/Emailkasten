from django.db import models
from .. import constants
from .MailboxModel import MailboxModel

class DaemonModel(models.Model):
    mailbox = models.OneToOneField(MailboxModel, related_name='daemon', on_delete=models.CASCADE)
    cycle_interval = models.IntegerField(default=constants.EMailArchiverDaemonConfiguration.CYCLE_PERIOD_DEFAULT)
    is_running = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'daemons'
        
    def __str__(self):
        return f"Mailfetcher daemon configuration for mailbox {self.mailbox}"
    
