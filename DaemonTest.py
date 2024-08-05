import logging

from EMailArchiverDaemon import EMailArchiverDaemon


if __name__ == "__main__":
    daemon = EMailArchiverDaemon()
    daemon.start()