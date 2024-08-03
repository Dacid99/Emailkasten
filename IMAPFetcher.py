import imaplib
import logging

from MailParser import MailParser

class IMAPFetcher: 
    
    def __init__(self, username, password, host: str = "", port: int = 993, timeout= None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.__mailhost = imaplib.IMAP4(host, port, timeout)
        self.username = username
        self.password = password
        self.login()

    def login(self):
        logging.debug(f"Logging in to {self.host} on port {self.port} with username {self.username} and password {self.password} via IMAP ...")
        try:
            self.__mailhost.login(self.username, self.password)
            logging.debug(f"Successfully logged in to {self.host} on port {self.port} with username {self.username} via IMAP.")
        except imaplib.IMAP4.error as e:
            logging.error(f"Failed connecting via IMAP to {self.host} on port {self.port} with username {self.username} and password {self.password}!")

    def close(self):
        logging.debug(f"Closing connection to {self.host} on port {self.port} with username {self.username} via IMAP ...")
        if self.__mailhost:
            try:
                self.__mailhost.close()
                self.__mailhost.logout()
                logging.debug(f"Gracefully closed connection to {self.host} on port {self.port} with username {self.username} via IMAP.")
            except imaplib.IMAP4.error:
                logging.error("Failed to close connection to {self.host} on port {self.port} with username {self.username} via IMAP!")

    def fetchLatest(self, mailbox = 'INBOX'):
        logging.debug(f"Fetching from {mailbox} at {self.host} on port {self.port} with username {self.username} via IMAP ...")
        try:
            self.__mailhost.select(mailbox)
            typ, messageNumbers = self.__mailhost.search(None, 'ALL')
            number = messageNumbers[0].split()[-2]
            typ, messageData = self.__mailhost.fetch(number, '(RFC822)')
            mailParser = MailParser(messageData[0][1]) 
            logging.debug(f"Successfully fetched from {mailbox} at {self.host} on port {self.port} with username {self.username} via IMAP.")
            return mailParser
        except imaplib.IMAP4.error as e:
            logging.error(f"Failed to fetch data via IMAP from {self.host} on port {self.port} with username {self.username}!")
            return None

    def __enter__(self):
        logging.debug("IMAP_SSL_Fetcher.__enter__")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        logging.debug("IMAP_SSL_Fetcher.__exit__")
        self.close()

