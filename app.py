from IMAP_SSL_Fetcher import IMAP_SSL_Fetcher


mail = IMAP_SSL_Fetcher(username="inbox@aderbauer.org", password="28CFSrs2!1f7Yh&95,-", host="imap.ionos.de", port=993)

mail.fetchAndPrintAll() 