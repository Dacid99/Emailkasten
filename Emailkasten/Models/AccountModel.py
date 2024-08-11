from django.db import models
from .IMAPFetcher import IMAPFetcher
from .IMAP_SSL_Fetcher import IMAP_SSL_Fetcher
from .POP3Fetcher import POP3Fetcher
from .POP3_SSL_Fetcher import POP3_SSL_Fetcher


class AccountModel(models.Model):
    mail_address = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    mail_host = models.CharField(max_length=255)
    mail_host_port = models.IntegerField(null=True)
    protocol = models.TextChoices(IMAPFetcher.PROTOCOL, IMAP_SSL_Fetcher.PROTOCOL, POP3Fetcher.PROTOCOL, POP3_SSL_Fetcher.PROTOCOL, ExchangeFetcher.PROTOCOL)
    cycle_interval = models.IntegerField(default=EMailArchiverDaemon.cyclePeriod)
    save_attachments = models.BooleanField(default=True)
    save_toEML = models.BooleanField(default=True)
    is_fetched = models.BooleanField(default=False)

    def __str__(self):
        return f"Account {self.mail_address} with protocol {self.protocol}"

    class Meta:
        db_table = "accounts"

