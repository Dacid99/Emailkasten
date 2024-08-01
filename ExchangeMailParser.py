import exchangelib

class ExchangeMailParser:
    def parseFrom(mail):
        if isinstance(mail, exchangelib.Message):
            return mail.sender.email_address
    
    def parseTo(mail):
        if isinstance(mail, exchangelib.Message):
            recipients = [recipient.email_address for recipient in mail.to_recipients]
            return recipients
        
    def parseBcc(mail):
        if isinstance(mail, exchangelib.Message):
            recipients = [recipient.email_address for recipient in mail.bcc_recipients]
            return recipients
    
    def parseCc(mail):
        if isinstance(mail, exchangelib.Message):
            recipients = [recipient.email_address for recipient in mail.cc_recipients]
            return recipients
    
    def parseDate(mail):
        if isinstance(mail, exchangelib.Message):
            return mail.datetime_received
        
    def parseBody(mail):
        if isinstance(mail, exchangelib.Message):
            return mail.text_body
        
    def parseSubject(mail):
        if isinstance(mail, exchangelib.Message):
            return mail.subject
