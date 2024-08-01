import imaplib
import os

from MailParser import MailParser

class IMAPFetcher(imaplib.IMAP4): 

    def __init__(self, username, password, host: str = "", port: int = 143, timeout= None):
        super().__init__(host, port, timeout)
        self.__username = username
        self.__password = password

    
    def withLogin(method):
        def methodWithLogin(self, *args, **kwargs):
            self.login(self.__username, self.__password)
            method(self, *args, **kwargs)
            self.logout()
        return methodWithLogin
    
    @withLogin
    def fetchAndPrintAll(self, mailbox = 'INBOX'):
        self.select(mailbox)
        typ, messageNumbers = self.search(None, 'ALL')
        for number in messageNumbers[0].split()[-2:]:
            typ, messageData = self.fetch(number, '(RFC822)')
            print('Message %s\n%s\n' % (number, MailParser.parseTo(messageData[0][1]))) 


