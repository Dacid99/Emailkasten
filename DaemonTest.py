import logging

from EMailArchiverDaemon import EMailArchiverDaemon


logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    daemon = EMailArchiverDaemon()
    daemon.start()