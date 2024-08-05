

class ParsedEMail:
    def __init__(self):
        self.messageID = None
        self.subject = None
        self.emailFrom = None
        self.emailTo = []
        self.emailCc = []
        self.emailBcc = []
        self.dateReceived = None
        self.bodyText = None

    def hasMessageID(self):
        return bool(self.messageID)

    def hasSubject(self):
        return bool(self.subject)

    def hasFrom(self):
        return bool(self.emailFrom) and True

    def hasTo(self):
        return bool(self.emailTo) and True

    def hasCc(self):
        return bool(self.emailCc) and True
    
    def hasBcc(self):
        return bool(self.emailBcc) and True
    
    def hasDateReceived(self):
        return bool(self.dateReceived) and True
        
    def hasBodyText(self):
        return bool(self.bodyText) and True

