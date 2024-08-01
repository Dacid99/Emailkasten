import poplib
import os

from MailParser import MailParser

class POP3Fetcher(poplib.POP3): 

    def __init__(self, username, password, host: str = "", port: int = 110, timeout= None):
        super().__init__(host, port, timeout)
        self.__username = username
        self.__password = password

    
    def withLogin(method):
        def methodWithLogin(self, *args, **kwargs):
            #maybe with apop or rpop?
            self.user(self.__username)
            self.pass_( self.__password)
            method(self, *args, **kwargs)
            self.quit()
        return methodWithLogin
    
    @withLogin
    def fetchAndPrintAll(self, mailbox = 'INBOX'):
        self.select(mailbox)
        typ, data = self.search(None, 'ALL')
        messageNumber = len(self.list()[1])
        for number in range(messageNumber):
            typ, messageData = self.retr(number + 1)
            fullMessage = bytes()
            for messageLine in messageData:
                fullMessage += messageLine
            print('Message %s\n%s\n' % (number, MailParser.parseTo(fullMessage))) 


