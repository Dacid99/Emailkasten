import imaplib
import os

from MailParser import MailParser

class IMAP_SSL_Fetcher(imaplib.IMAP4_SSL): 

    def __init__(self, username, password, host: str = "", port: int = 993, keyfile= None, certfile = None, ssl_context = None, timeout= None):
        super().__init__(host, port, keyfile, certfile, ssl_context, timeout)
        self.__username = username
        self.__password = password

    
    def fetchAndPrintAll(self, mailbox = 'INBOX'):
        self.login(self.__username, self.__password)
        self.select(mailbox)
        typ, data = self.search(None, 'ALL')
        for number in data[0].split()[-2:]:
            typ, data = self.fetch(number, '(RFC822)')
            print('Message %s\n%s\n' % (number, MailParser.parseTo(data[0][1]))) 
        self.logout()


