import poplib
import os

from MailParser import MailParser

class POP3_SSL_Fetcher: 

    def __init__(self, username, password, host: str = "", port: int = 995, keyfile= None, certfile = None, ssl_context = None, timeout= None):
        self.__mailhost = poplib.POP3_SSL(host, port, keyfile, certfile, timeout, ssl_context)
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
        

