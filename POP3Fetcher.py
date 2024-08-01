import poplib
import os

from MailParser import MailParser

class POP3Fetcher: 

    def __init__(self, username, password, host: str = "", port: int = 110, timeout= None):
        self.__mailhost = poplib.POP3(host, port, timeout)
        self.__username = username
        self.__password = password

    
    def withLogin(method):
        def methodWithLogin(self, *args, **kwargs):
            #maybe with apop or rpop?
            self.__mailhost.user(self.__username)
            self.__mailhost.pass_( self.__password)
            method(self, *args, **kwargs)
            self.__mailhost.quit()
        return methodWithLogin
    
    @withLogin
    def fetchAndPrintAll(self):
        messageNumber = len(self.__mailhost.list()[1])
        for number in range(messageNumber):
            messageData = self.__mailhost.retr(number + 1)[1]
            
            fullMessage = b'\n'.join(messageData)
            mailParser = MailParser(fullMessage)
            print(mailParser.parseFrom())
            print(mailParser.parseTo())
            print(mailParser.parseSubject())
            print(mailParser.parseBody())
            print(mailParser.parseDate())
            print(mailParser.parseCc())
            print(mailParser.parseBcc())


