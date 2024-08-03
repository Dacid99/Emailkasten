import mysql.connector
import logging
import traceback

class EMailDBFeeder:
    __INSERT_EMAIL_SQL = '''
        INSERT IGNORE INTO emails (message_id, sender, date_received, bodytext)
        VALUES (%s, %s, %s, %s)
    '''

    __INSERT_CORRESPONDENT_SQL = '''
        INSERT INTO correspondents (email_name, email_address)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE
            email_name = IF(email_name = '' OR email_name IS NULL, VALUES(email_name), email_name);
    '''

    __SELECT_CORRESPONDENTS_ID_SQL = '''
        SELECT id FROM correspondents WHERE email_address IN (%s)
    '''

    __INSERT_EMAIL_CORRESPONDENT_CONNECTION_SQL = '''
        INSERT IGNORE INTO email_correspondents (email_id, correspondent_id, mention)
        VALUES (%s, %s, %s)
    '''

    MENTION_TO = "TO"
    MENTION_CC = "CC"
    MENTION_BCC = "BCC"


    def __init__(self, dbManager):
        self.__dbManager = dbManager

    def insertEmail(self, parsedEMail):
        emailData = []
        emailData.append(parsedEMail.parseMessageID())
        emailData.append(parsedEMail.parseFrom()[1])
        emailData.append(parsedEMail.parseDate())
        emailData.append(parsedEMail.parseBody())
        return self.__dbManager.execute(EMailDBFeeder.__INSERT_EMAIL_SQL, emailData)

    def insertCorrespondents(self, parsedEMail):

        toCorrespondents = parsedEMail.parseTo()
        ccCorrespondents = parsedEMail.parseCc()
        bccCorrespondents = parsedEMail.parseBcc()

        for toCorrespondent in toCorrespondents:
            self.__dbManager.execute(EMailDBFeeder.__INSERT_CORRESPONDENT_SQL, toCorrespondent)
        for ccCorrespondent in ccCorrespondents:
            self.__dbManager.execute(EMailDBFeeder.__INSERT_CORRESPONDENT_SQL, ccCorrespondent)
        for bccCorrespondent in bccCorrespondents:
            self.__dbManager.execute(EMailDBFeeder.__INSERT_CORRESPONDENT_SQL, bccCorrespondent)


    def insertEmailCorrespondentsConnection(self, parsedEMail, emailID):

        toCorrespondentsAddresses = []
        for toCorrespondent in parsedEMail.parseTo():
            toCorrespondentsAddresses.append(toCorrespondent[1])

        ccCorrespondentsAddresses = []
        for ccCorrespondent in parsedEMail.parseCc():
            ccCorrespondentsAddresses.append(ccCorrespondent[1])

        bccCorrespondentsAddresses = []
        for bccCorrespondent in parsedEMail.parseBcc():
            bccCorrespondentsAddresses.append(bccCorrespondent[1])


        self.__dbManager.execute(EMailDBFeeder.__SELECT_CORRESPONDENTS_ID_SQL % ', '.join(['%s']*len(toCorrespondentsAddresses)), toCorrespondentsAddresses)
        toCorrespondentsIDs = self.__dbManager.fetchall()
        
        self.__dbManager.execute(EMailDBFeeder.__SELECT_CORRESPONDENTS_ID_SQL % ', '.join(['%s']*len(ccCorrespondentsAddresses)), ccCorrespondentsAddresses)
        ccCorrespondentsIDs = self.__dbManager.fetchall()
        
        self.__dbManager.execute(EMailDBFeeder.__SELECT_CORRESPONDENTS_ID_SQL % ', '.join(['%s']*len(bccCorrespondentsAddresses)), bccCorrespondentsAddresses)
        bccCorrespondentsIDs = self.__dbManager.fetchall()

        
        for toCorrespondentId in toCorrespondentsIDs:
            self.__dbManager.execute(EMailDBFeeder.__INSERT_EMAIL_CORRESPONDENT_CONNECTION_SQL, [emailID, toCorrespondentId[0], EMailDBFeeder.MENTION_TO])

        for ccCorrespondentId in ccCorrespondentsIDs:
            self.__dbManager.execute(EMailDBFeeder.__INSERT_EMAIL_CORRESPONDENT_CONNECTION_SQL, (emailID, ccCorrespondentId[0], EMailDBFeeder.MENTION_CC))

        for bccCorrespondentId in bccCorrespondentsIDs:
            self.__dbManager.execute(EMailDBFeeder.__INSERT_EMAIL_CORRESPONDENT_CONNECTION_SQL, (emailID, bccCorrespondentId[0], EMailDBFeeder.MENTION_BCC))


    def insert(self, parsedEMail):
        emailID = self.insertEmail(parsedEMail)
        self.insertCorrespondents(parsedEMail)
        self.insertEmailCorrespondentsConnection(parsedEMail, emailID)
        self.__dbManager.commit()

        