|variable | default | 
|---------|---------|
EmailArchiverDaemon.cyclePeriod | 60 | 
EmailArchiverDaemon.saveAttachments | True |
EmailArchiverDaemon.saveToEML | True |
LoggerFactory.loggerName | "EMailArchiverDaemon" |
LoggerFactory.logfilePath | f"/var/log/{loggerName}.log" |
LoggerFactory.logLevel | logging.INFO = 20 | 
LoggerFactory.logfileMaxSize | 10 MB | 
LoggerFactory.logfileBackupCount | 3 |
LoggerFactory.consoleLogging | False |
LoggerFactory.logFormat | '%(name)s - %(levelname)s: %(message)s' |
DBManager.reconnectWaitTime | 15 |
FileManager.emlDirectoryPath | /mnt/eml/ |
FileManager.attachmentDirectoryPath | /mnt/attachments/ |

