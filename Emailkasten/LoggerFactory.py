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
