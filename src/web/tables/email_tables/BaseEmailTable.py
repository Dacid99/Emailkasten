# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024 David Aderbauer & The Emailkasten Contributors
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

"""test.web.tables.email_tables package containing email tables of the Emailkasten webapp."""

from django_tables2 import Column, Table

from core.models import Email
from web.utils.columns import CheckboxColumn


class BaseEmailTable(Table):
    checkbox = CheckboxColumn()
    subject = Column(linkify=True)

    class Meta:
        model = Email
        fields = (
            "subject",
            "datetime",
            "datasize",
        )
        sequence = ("checkbox", *fields)
