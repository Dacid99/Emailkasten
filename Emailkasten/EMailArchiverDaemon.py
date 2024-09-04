import time
import threading
from rest_framework.response import Response
from . import constants
from .LoggerFactory import LoggerFactory
from .MailProcessor import MailProcessor


class EMailArchiverDaemon:
    runningDaemons = {}
    
    @staticmethod
    def startDaemon(daemonModel):
        if not daemonModel.id in EMailArchiverDaemon.runningDaemons:
            try:
                newDaemon = EMailArchiverDaemon(daemonModel)
                newDaemon.start()
                EMailArchiverDaemon.runningDaemons[daemonModel.id] = newDaemon
                daemonModel.is_running = True
                daemonModel.save() 
                return Response({'status': 'Daemon started', 'account': daemonModel.mailbox.account.mail_address, 'mailbox': daemonModel.mailbox.name})
            except Exception as e:
                return Response({'status': 'Daemon failed to start!', 'account': daemonModel.mailbox.account.mail_address, 'mailbox': daemonModel.mailbox.name})
        else:
            return Response({'status': 'Daemon already running', 'account': daemonModel.mailbox.account.mail_address, 'mailbox': daemonModel.mailbox.name})
        
    @staticmethod
    def stopDaemon(daemonModel):
        if daemonModel.id in EMailArchiverDaemon.runningDaemons:
            oldDaemon = EMailArchiverDaemon.runningDaemons.pop(daemonModel.id)
            oldDaemon.stop()
            daemonModel.is_running = False
            daemonModel.save()
            return Response({'status': 'Daemon stopped', 'account': daemonModel.mailbox.account.mail_address, 'mailbox': daemonModel.mailbox.name})
        else:
            return Response({'status': 'Daemon not running', 'account': daemonModel.mailbox.account.mail_address, 'mailbox': daemonModel.mailbox.name})
        

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
            time.sleep(constants.EMailArchiverDaemonConfiguration.RESTART_TIME)
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

