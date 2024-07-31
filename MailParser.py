import email 

class MailParser:
    __fromString = "From"
    __toString = "To"
    __bccString = "Bcc"
    __dateString = "Date"
    __subjectString = "Subject"


    def parseToText(mail):
        mailText = email.message_from_bytes(mail)
        return mailText
    
    def parseFrom(mail):
        mailText = MailParser.parseToText(mail)
        return mailText.get(MailParser.__fromString)
    
    def parseTo(mail):
        mailText = MailParser.parseToText(mail)
        return mailText.get(MailParser.__toString)
    
    def parseBCC(mail):
        mailText = MailParser.parseToText(mail)
        return mailText.get(MailParser.__bccString)

    def parseDate(mail):
        mailText = MailParser.parseToText(mail)
        return mailText.get(MailParser.__dateString)
    
    def parseSubject(mail):
        mailText = MailParser.parseToText(mail)
        return mailText.get(MailParser.__subjectString)
    
    def parseBody(mail):
        mailText = MailParser.parseToText(mail)
        mailBodyText = ""
        for text in mailText.walk():
            if text.get_content_type() == 'text/plain':
                mailBodyText += text.as_string()