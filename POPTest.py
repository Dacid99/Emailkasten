from POP3_SSL_Fetcher import POP3_SSL_Fetcher


mail = POP3_SSL_Fetcher(username="archiv@aderbauer.org", password="nxF154j9879ZZsW", host="pop.ionos.de", port=995)

mail.fetchAndPrintAll() 