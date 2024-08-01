import exchangelib
from ExchangeMailParser import ExchangeMailParser

class ExchangeFetcher(exchangelib.Account):
    def __init__(self, username, password, primary_smtp_address=None, fullname=None, access_type=None, autodiscover=False, config=None, locale=None, default_timezone=None):
        self.credentials = exchangelib.Credentials(username, password)
        super.__init__(primary_smtp_address,
                        fullname,
                        access_type,
                        autodiscover,
                        self.credentials,
                        config,
                        locale,
                        default_timezone)
        
    def fetchAllAndPrint(self):
        for message in self.inbox.all().order_by('-datetime_received')[:10]:
            print(ExchangeMailParser.parseFrom(message))