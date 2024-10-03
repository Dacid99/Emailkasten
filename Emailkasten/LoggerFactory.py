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

import logging
import logging.handlers
from . import constants

class LoggerFactory:

    @staticmethod
    def getMainLogger():
        logger = logging.getLogger(constants.LoggerConfiguration.LOGGER_NAME)
        
        return logger

    
    @staticmethod
    def getChildLogger(instanceName):
        logger = logging.getLogger(constants.LoggerConfiguration.LOGGER_NAME + "." + str(instanceName))

        return logger
