import logging

from EMailDBFeeder import EMailDBFeeder
from IMAP_SSL_Fetcher import IMAP_SSL_Fetcher
from POP3_SSL_Fetcher import POP3_SSL_Fetcher
from MailParser import MailParser
from DBManager import DBManager
from LoggerFactory import LoggerFactory
from EMailArchiverDaemon import EMailArchiverDaemon


MailParser.emlDirectoryPath = "C:\\Users\\phili\\Desktop\\emltest\\"
MailParser.attachmentDirectoryPath = "C:\\Users\\phili\\Desktop\\attachmenttest\\"
LoggerFactory.logfilePath = "C:\\Users\\phili\\Desktop\\log.log\\"
LoggerFactory.logLevel = logging.DEBUG
LoggerFactory.consoleLogging = True


if __name__ == "__main__":
    daemon = EMailArchiverDaemon()
    daemon.start()