import email 
import email.header
import email.utils
import email.generator
import logging
import os.path
import datetime
import pytz

from LoggerFactory import LoggerFactory
from ParsedEMail import ParsedEMail

class MailParser:
    __messageIDString = "Message-ID"
    __fromString = "From"
    __toString = "To"
    __bccString = "Bcc"
    __ccString = "Cc"
    __dateString = "Date"
    __subjectString = "Subject"
    __charsetDefault = "utf-8"
    __dateFormat = '%Y-%m-%d %H:%M:%S'
    __dateDefault = "1971-01-01 00:00:00"  #must fit dateFormat
    timezone = "Europe/Berlin"
    emlDirectoryPath = "/mnt/eml/"
    attachmentDirectoryPath = "/mnt/attachments/"

    @staticmethod
    def parseMailbox(mailboxBytes):
        mailbox = mailboxBytes.decode(MailParser.__charsetDefault)
        mailboxName = mailbox.split("\"/\"")[1].strip()
        if mailboxName == "":
            mailboxName = mailbox.split("\" \"")[1].strip()
        return mailboxName

    @staticmethod
    def parseMail(mailToParse):
        logger = LoggerFactory.getChildLogger(MailParser.__name__)

        mailMessage = email.message_from_bytes(mailToParse)
        logger.debug(f"Parsing email with content {mailMessage}...")

        def decodeHeader(header):

            decodedFragments = email.header.decode_header(header)
            decodedString = ""
            for fragment, charset in decodedFragments:
                if charset is None:
                    decodedString += fragment.decode(MailParser.__charsetDefault, errors='replace') if isinstance(fragment, bytes) else fragment
                else:
                    decodedString += fragment.decode(charset, errors='replace')

            return decodedString


        def decodeText(text):

            charset = text.get_content_charset()
            if charset is None:
                charset = MailParser.__charsetDefault
            decodedText = text.get_payload(decode=True).decode(charset, errors='replace')

            return decodedText
        

        def separateMailNameAndAdress(mailer):
            mailName, mailAddress = email.utils.parseaddr(mailer)
            if mailAddress.find("@") == -1:
                logger.warn(f"Separation of mailname and address failed for {mailer}!")
                mailAddress = mailer
            
            return (mailName, mailAddress)
        

        def parseMessageID():
            messageID = mailMessage.get(MailParser.__messageIDString)
            if messageID is None:
                logger.warn(f"No messageID found in mail, resorting to hash!")
                return str(hash(mailMessage))  #fallback for unique identifier if no messageID found
            return messageID

        def parseFrom():
            sender = mailMessage.get(MailParser.__fromString)
            if sender is None:
                logger.warn(f"No FROM correspondent found in mail!")
                return None
            return separateMailNameAndAdress(decodeHeader(sender))

        def parseTo():
            recipients = mailMessage.get_all(MailParser.__toString)
            if recipients is None:
                logger.warn(f"No TO correspondents found in mail!")
                return []
            decodedAndSeparatedRecipients = [separateMailNameAndAdress(decodeHeader(recipient)) for recipient in recipients]
            return decodedAndSeparatedRecipients
        
        def parseBcc():
            recipients = mailMessage.get_all(MailParser.__bccString)
            if recipients is None:
                logger.debug("No BCC correspondents found in mail")
                return []
            decodedAndSeparatedRecipients = [separateMailNameAndAdress(decodeHeader(recipient)) for recipient in recipients]
            return decodedAndSeparatedRecipients
        
        def parseCc():
            recipients = mailMessage.get_all(MailParser.__ccString)
            if recipients is None:
                logger.debug("No CC correspondents found in mail")
                return []
            decodedAndSeparatedRecipients = [separateMailNameAndAdress(decodeHeader(recipient)) for recipient in recipients]
            return decodedAndSeparatedRecipients

        def parseDate():
            date = mailMessage.get(MailParser.__dateString)
            if date is None:
                logger.warn(f"No DATE found in mail, resorting to default!")
                return MailParser.__dateDefault
            decodedDate = decodeHeader(date)
            if MailParser.timezone in pytz.all_timezones:
                timezoneObject = pytz.timezone(MailParser.timezone)
            else:
                logger.warn(f"Invalid timezone {MailParser.timezone}, defaulting to UTC!")
                timezoneObject = datetime.timezone.utc
            decodedConvertedDate = email.utils.parsedate_to_datetime(decodedDate).astimezone(timezoneObject).strftime(MailParser.__dateFormat)
            return decodedConvertedDate
        
        def parseSubject():
            if (subject := mailMessage.get(MailParser.__subjectString)):
                return decodeHeader(subject)
            else: 
                logger.warn(f"No SUBJECT found in mail!")
                return ""
        
        def parseBody():
            mailBodyText = ""
            if mailMessage.is_multipart():
                for part in mailMessage.walk():
                    if part.get_content_type() in ['text/plain', 'text/html']:
                        mailBodyText += decodeText(part)
            else:
                mailBodyText = decodeText(mailMessage)
            if mailBodyText == "":
                logger.warn(f"No BODYTEXT found in mail!")
            return mailBodyText

        def generateEML():
            logger.debug("Storing mail in .eml file ...")
            emlFilePath = os.path.join(MailParser.emlDirectoryPath, parseSubject() + ".eml")
            try:
                if os.path.exists(emlFilePath):
                    if os.path.getsize(emlFilePath) > 0:
                        logger.debug(f"Not writing to {emlFilePath}, it already exists and is not empty")
                        return emlFilePath
                    else:
                        logger.debug(f"Writing to empty .eml file {emlFilePath} ...")
                        with open(emlFilePath, "wb") as emlFile:
                            emlGenerator = email.generator.BytesGenerator(emlFile)
                            emlGenerator.flatten(mailMessage)
                        logger.debug("Success")
                else:
                    if not os.path.exists(MailParser.emlDirectoryPath):
                            logger.debug(f"Creating directory {MailParser.emlDirectoryPath} ...")
                            os.makedirs(MailParser.emlDirectoryPath)
                            logger.debug("Success")
                    logger.debug(f"Creating new .eml file {emlFilePath}...")
                    with open(emlFilePath, "wb") as emlFile:
                        emlGenerator = email.generator.BytesGenerator(emlFile)
                        emlGenerator.flatten(mailMessage)
                    logger.debug("Success")

            except OSError as e:
                logger.error(f"Failed to write .eml file for message!", exc_info=True)
                if os.path.exists(emlFilePath):
                    logger.debug("Clearing incomplete file ...")
                    try: 
                        with open(emlFilePath, "wb") as file:
                            file.truncate(0)
                        logger.debug("Success")
                    except OSError as e:
                        logger.error("Failed to clear the incomplete file!")
                else:
                    logger.debug("File was not created")

            return emlFilePath


        def parseAttachments():
            attachmentFiles = []
            if mailMessage.is_multipart():
                for part in mailMessage.walk():
                    if part.get_content_disposition() == "attachment":
                        fileName = part.get_filename()
                        dirPath = os.path.join(MailParser.attachmentDirectoryPath, parseSubject())
                        filePath = os.path.join(dirPath, fileName)
                        attachmentFiles.append( (fileName,filePath) )
                        try:
                            if os.path.exists(filePath):
                                if os.path.getsize(filePath) > 0:
                                    logger.debug(f"Not writing to {filePath}, it already exists and is not empty")
                                    continue
                                else:
                                    logger.debug(f"Writing to empty file {filePath} ...")
                                    with open(filePath, "wb") as file:
                                        file.write(part.get_payload(decode=True))
                                    logger.debug("Success")
                            else:
                                if not os.path.exists(dirPath):
                                    logger.debug(f"Creating directory {dirPath} ...")
                                    os.makedirs(dirPath)
                                    logger.debug("Success")
                                logger.debug(f"Creating new file {filePath} ...")
                                with open(filePath, "wb") as file:
                                    file.write(part.get_payload(decode=True))
                                logger.debug("Success")

                        except OSError as e:
                            logger.error(f"Failed to write attachment file {fileName} to {filePath}!", exc_info=True)
                            if os.path.exists(filePath):
                                logger.debug("Clearing incomplete file ...")
                                try: 
                                    with open(filePath, "wb") as file:
                                        file.truncate(0)
                                    logger.debug("Success")
                                except OSError as e:
                                    logger.error("Failed to clear the incomplete file!")
                            else:
                                logger.debug("File was not created")
                            
            
            if not attachmentFiles:
                logger.debug(f"No attachments found in mail")

            return attachmentFiles


        
        parsedEMail = ParsedEMail()
        parsedEMail.messageID = parseMessageID()
        parsedEMail.subject = parseSubject()
        parsedEMail.emailFrom = parseFrom()
        parsedEMail.emailTo = parseTo()
        parsedEMail.emailCc = parseCc()
        parsedEMail.emailBcc = parseBcc()
        parsedEMail.dateReceived = parseDate()
        parsedEMail.bodyText = parseBody()
        parsedEMail.emlFilePath = generateEML()
        parsedEMail.attachments = parseAttachments()

        logger.debug("Success")
        return parsedEMail