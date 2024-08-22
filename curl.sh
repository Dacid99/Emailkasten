#!/bin/bash

#curl -X POST http://192.168.178.138:1122/accounts/ -H "Content-Type: application/json" -d '{"mail_address": "archiv@aderbauer.org", "password": "nxF154j9879ZZsW", "mail_host": "imap.ionos.de", "mail_host_port": "993", "protocol": "IMAP_SSL"}' 
#curl -X POST http://192.168.178.138:1122/accounts/1/scan_mailboxes/
#curl -X GET http://192.168.178.138:1122/emails/
curl -X GET http://192.168.178.138:1122/accounts/
#curl -X POST http://192.168.178.138:1122/mailboxes/1/fetch_all/
#curl -X POST http://192.168.178.138:1122/mailboxes/1/stop/
#curl -X PATCH http://192.168.178.138:1122/mailboxes/1/ -H "Content-Type: application/json" -d '{"fetching_criterion": "ALL", "cycle_interval": "3600"}'
