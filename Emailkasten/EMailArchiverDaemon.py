import time
import threading

from . import constants
from .LoggerFactory import LoggerFactory
from .MailProcessor import MailProcessor
from .EMailDBFeeder import EMailDBFeeder


class EMailArchiverDaemon:

    def __init__(self, daemon):
        self.logger = LoggerFactory.getChildLogger(self.__class__.__name__)
        self.thread = None
        self.isRunning = False
        
        self.daemon = daemon
        self.mailbox = daemon.mailbox
        self.account = daemon.mailbox.account


    def start(self):
        self.logger.info("Starting EMailArchiverDaemon")
        self.isRunning = True
        self.thread = threading.Thread(target = self.run)
        self.thread.start()

    def stop(self):
        self.logger.info("Stopping EMailArchiverDaemon")
        self.isRunning = False

    def run(self):
        try:
            while self.isRunning:
                self.cycle()
                time.sleep(self.daemon.cycle_interval)
            self.logger.info("EMailArchiverDaemon finished")
        except Exception as e:
            self.logger.critical("EMailArchiverDaemon crashed! Attempting to restart ...", exc_info=True)
            time.sleep(constants.EMailArchiverDaemonConfiguration.restartTime)
            self.run()

    def cycle(self):
        self.logger.debug("---------------------------------------\nNew cycle")
        startTime = time.time()
        try:
            MailProcessor.fetch(self.mailbox, self.account, self.mailbox.fetching_criterion)

            endtime = time.time()
            self.logger.debug(f"Cycle complete after {endtime - startTime} seconds\n-------------------------------------------")
                            
        except Exception as e:
            self.logger.error("Error during daemon cycle execution!", exc_info=True)
            raise

