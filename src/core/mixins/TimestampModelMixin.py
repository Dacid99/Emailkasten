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

"""Module with the :class:`TimestampModelMixin`."""

from django.db.models import DateTimeField, Model
from django.utils.translation import gettext_lazy as _


class TimestampModelMixin(Model):
    """Mixin adding `created` and `updated` timestamps to a model class."""

    created = DateTimeField(
        auto_now_add=True,
        verbose_name=_("created"),
    )
    """The datetime the model instance was created. Is set automatically."""

    updated = DateTimeField(
        auto_now=True,
        verbose_name=_("last updated"),
    )
    """The datetime the model instance entry was last updated. Is set automatically."""

    class Meta:
        """Metadata class for the mixin, abstract to avoid makemigrations picking it up."""

        abstract = True
