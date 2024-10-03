'''
    Emailkasten - a open-source self-hostable email archiving server
    Copyright (C) 2024  David & Philipp Aderbauer

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

import exchangelib
from .. import constants
from ..ExchangeMailParser import ExchangeMailParser

class ExchangeFetcher:
    PROTOCOL = constants.MailFetchingProtocols.EXCHANGE
    
    def __init__(self, username, password, primary_smtp_address=None, server='outlook.office365.com', fullname=None, access_type=exchangelib.DELEGATE, autodiscover=True, locale=None, default_timezone=None):
        self.__credentials = exchangelib.Credentials(username, password)
        self.__config = exchangelib.Configuration(server=server, credentials=self.__credentials)
        
        self.__mailhost = exchangelib.Account(
            primary_smtp_address=primary_smtp_address,fullname=fullname,access_type=access_type,autodiscover=autodiscover,locale=locale,default_timezone=default_timezone
            )
        
    def fetchAllAndPrint(self):
        for message in self.__mailhost.inbox.all().order_by('-datetime_received')[:10]:
            mailParser = ExchangeMailParser(message)
            print(mailParser.parseFrom())


    def __enter__(self):
        self.logger.debug(str(self.__class__.__name__) + "._enter_")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.logger.debug(str(self.__class__.__name__) + "._exit_")