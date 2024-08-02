import imaplib
import os

from MailParser import MailParser

class IMAP_SSL_Fetcher: 
    
    def __init__(self, username, password, host: str = "", port: int = 993, keyfile= None, certfile = None, ssl_context = None, timeout= None):
        self.__mailhost=imaplib.IMAP4_SSL(host, port, keyfile, certfile, ssl_context, timeout)
        self.__username = username
        self.__password = password

    def withLogin(method):
        def methodWithLogin(self, *args, **kwargs):
            
            method(self, *args, **kwargs)

        return methodWithLogin
    

    def fetchLatest(self, mailbox = 'INBOX'):
        self.__mailhost.login(self.__username, self.__password)
        self.__mailhost.select(mailbox)
        typ, messageNumbers = self.__mailhost.search(None, 'ALL')
        number = messageNumbers[0].split()[-2]
        typ, messageData = self.__mailhost.fetch(number, '(RFC822)')
        mailParser = MailParser(messageData[0][1]) 
        self.__mailhost.logout()
        return mailParser

