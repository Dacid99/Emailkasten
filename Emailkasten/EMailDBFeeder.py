import logging
import traceback
import django.db
from .LoggerFactory import LoggerFactory
from .Models.EMailModel import EMailModel
from .Models.AttachmentModel import AttachmentModel
from .Models.CorrespondentModel import CorrespondentModel
from .Models.EMailCorrespondentsModel import EMailCorrespondentsModel


class EMailDBFeeder:

    MENTION_FROM = "FROM"
    MENTION_TO = "TO"
    MENTION_CC = "CC"
    MENTION_BCC = "BCC"

    @staticmethod
    def insert(parsedEMail):
        logger = LoggerFactory.getChildLogger(EMailDBFeeder.__name__)

        try:
            with django.db.transaction.atomic():
                emailEntry = EMailModel.objects.get_or_create(
                    message_id = parsedEMail.messageID,
                    defaults = {
                        'date_received' : parsedEMail.dateReceived,
                        'email_subject' : parsedEMail.subject,
                        'bodytext' : parsedEMail.bodyText,
                        'datasize' :  parsedEMail.dataSize,
                        'eml_filepath' : parsedEMail.emlFilePath
                    }
                )

                for attachmentFile in parsedEMail.attachmentsFiles:
                    attachmentEntry = AttachmentModel.objects.get_or_create(
                        file_name = attachmentsFiles[0],
                        file_path = attachmentsFiles[1],
                        datasize = attachmentFile[2],
                        email = emailEntry
                    )

                for correspondent in parsedEMail.emailFrom:
                    correspondentEntry = CorrespondentModel.objects.get_or_create(
                        email_address = correspondent[1], 
                        defaults = {'email_name': correspondent[0]}
                    )
                   

                    EMailCorrespondentsModel.objects.get_or_create(
                        email = emailEntry, 
                        correspondent = correspondentEntry,
                        mention = EMailDBFeeder.MENTION_FROM
                    )

                for correspondent in parsedEMail.emailTo:
                    correspondentEntry = CorrespondentModel.objects.get_or_create(
                        email_address = correspondent[1], 
                        defaults = {'email_name': correspondent[0]}
                    )

                    EMailCorrespondentsModel.objects.get_or_create(
                        email = emailEntry, 
                        correspondent = correspondentEntry,
                        mention = EMailDBFeeder.MENTION_TO
                    )
                
                for correspondent in parsedEMail.emailCc:
                    correspondentEntry = CorrespondentModel.objects.get_or_create(
                        email_address = correspondent[1], 
                        defaults = {'email_name': correspondent[0]}
                    )

                    EMailCorrespondentsModel.objects.get_or_create(
                        email = emailEntry, 
                        correspondent = correspondentEntry,
                        mention = EMailDBFeeder.MENTION_CC
                    )

                for correspondent in parsedEMail.emailBcc:
                    correspondentEntry = CorrespondentModel.objects.get_or_create(
                        email_address = correspondent[1], 
                        defaults = {'email_name': correspondent[0]}
                    )

                    EMailCorrespondentsModel.objects.get_or_create(
                        email = emailEntry, 
                        correspondent = correspondentEntry,
                        mention = EMailDBFeeder.MENTION_BCC
                    )

        except django.db.IntegrityError as e:
            logger.error("Error while writing to database, rollback to last state", exc_info=True)


