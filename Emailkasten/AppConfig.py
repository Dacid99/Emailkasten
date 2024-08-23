from django.apps import AppConfig
from .Models.MailboxModel import MailboxModel
from .ViewSets.MailboxViewSet import MailboxViewSet
import logging

class Appconfig(AppConfig):
    name = 'Emailkasten'

    def ready(self):
        mailboxViewSet = MailboxViewSet()
        mailboxesWithDaemons = MailboxModel.objects.filter(is_fetching=True)

        for mailbox in mailboxesWithDaemons:
            try:
                mailboxViewSet.startDaemon(mailbox)
            except Exception:
                logging.error("Failed to start daemon on restart!")
