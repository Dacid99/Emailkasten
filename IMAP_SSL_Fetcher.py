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
            self.__mailhost.login(self.__username, self.__password)
            method(self, *args, **kwargs)
            self.__mailhost.logout()
        return methodWithLogin
    
    @withLogin
    def fetchAndPrintAll(self, mailbox = 'INBOX'):
        self.__mailhost.select(mailbox)
        typ, messageNumbers = self.__mailhost.search(None, 'ALL')
        for number in messageNumbers[0].split()[-10:]:
            typ, messageData = self.__mailhost.fetch(number, '(RFC822)')
            mailParser = MailParser(messageData[0][1]) 
            print(mailParser.parseFrom())
            print(mailParser.parseTo())
            print(mailParser.parseSubject())
            print(mailParser.parseBody())
            print(mailParser.parseDate())
            print(mailParser.parseCc())
            print(mailParser.parseBcc())
