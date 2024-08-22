import logging
import logging.handlers
import os

class LoggerFactory:

    @staticmethod
    def getMainLogger():
        logger = logging.getLogger(LoggerFactory.loggerName)
        
        return logger

    
    @staticmethod
    def getChildLogger(instanceName):
        logger = logging.getLogger(LoggerFactory.loggerName + "." + str(instanceName))

        return logger
