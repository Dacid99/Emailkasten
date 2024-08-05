import logging
import time
import signal

from DBManager import DBManager
from EMailDBFeeder import EMailDBFeeder
from IMAP_SSL_Fetcher import IMAP_SSL_Fetcher

class EMailArchiverDaemon:
    cyclePeriod = 60  #seconds
    __restartTime = 10
    dbHost = "192.168.178.109"
    dbUser = "root"
    dbPassword = "example"

    def __init__(self):
        signal.signal(signal.SIGTERM, self.signalHandler)
        signal.signal(signal.SIGINT, self.signalHandler)
        signal.signal(signal.SIGKILL, self.signalHandler)
        self.isRunning = True

    def start(self):
        logging.info("Starting EMailArchiverDaemon")
        try:
            while self.isRunning:
                self.cycle()
                time.sleep(EMailArchiverDaemon.cyclePeriod)
            logging.info("Stopped EMailArchiverDaemon")
        except Exception as e:
            logging.error("EMailArchiverDaemon crashed! Attempting to restart ...", exc_info=True)
            time.sleep(EMailArchiverDaemon.__restartTime)
            self.start()

    def cycle(self):
        try:
            with DBManager(EMailArchiverDaemon.dbHost, EMailArchiverDaemon.dbUser, EMailArchiverDaemon.dbPassword, "email_archive", "utf8mb4", "utf8mb4_bin") as db:
                
                dbfeeder = EMailDBFeeder(db)
                
                with IMAP_SSL_Fetcher(username="archiv@aderbauer.org", password="nxF154j9879ZZsW", host="pop.ionos.de") as imapMail:

                    parsedNewMails = imapMail.fetchBySearch(searchCriterion="RECENT")

                    for mail in parsedNewMails:
                        dbfeeder.insert(mail)
                        
        except Exception as e:
            logging.error("Error during daemon cycle execution!", exc_info=True)
            raise

    def signalHandler(self, signal, frame):
        self.isRunning = False
        logging.info(f"EMailArchiverDaemon stopped by system signal {signum}.")