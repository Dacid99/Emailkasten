# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

# from __future__ import annotations

# import exchangelib


# class ExchangeMailParser:

#     def __init__(self, mail_to_parse) -> None:
#         if isinstance(mail_to_parse, exchangelib.Message):
#             self.mail_message = mail_to_parse
#         else:
#             raise TypeError("Mail is no in Message format!")

#     def parse_from(self):
#         decoded_sender = self.mail_message.sender
#         return (decoded_sender.name, decoded_sender.email_address)

#     def parse_to(self):
#         return [
#             (recipient.name, recipient.email_address)
#             for recipient in self.mail_message.to_recipients
#         ]

#     def parse_bcc(self):
#         recipients = [
#             (recipient.name, recipient.email_address)
#             for recipient in self.mail_message.bcc_recipients
#         ]
#         return recipients

#     def parse_cc(self):
#         recipients = [
#             (recipient.name, recipient.email_address)
#             for recipient in self.mail_message.cc_recipients
#         ]
#         return recipients

#     def parse_date(self):
#         return str(self.mail_message.datetime_received)

#     def parse_body(self):
#         return str(self.mail_message.text_body)

#     def parse_subject(self):
#         return self.decode_header(self.mail_message.subject)
