# SPDX-License-Identifier: AGPL-3.0-or-later
#
# Emailkasten - a open-source self-hostable email archiving server
# Copyright (C) 2024  David & Philipp Aderbauer

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from rest_framework import serializers

from ...Models.MailboxModel import MailboxModel
from ..DaemonSerializers.DaemonSerializer import DaemonSerializer


class MailboxWithDaemonSerializer(serializers.ModelSerializer):
    """The standard serializer for a :class:`Emailkasten.Models.DaemonModel`.
    Uses all fields including the daemon."""

    daemons = DaemonSerializer(many=True, read_only=False)
    """The emails are serialized by :class:`Emailkasten.Serializers.DaemonSerializers.DaemonSerializer`."""


    class Meta:
        model = MailboxModel

        fields = '__all__'
        """Includes all fields."""

        read_only_fields = ['name', 'account', 'created', 'updated']
        """The :attr:`Emailkasten.Models.MailboxModel.name`, :attr:`Emailkasten.Models.MailboxModel.account`, :attr:`Emailkasten.Models.MailboxModel.created`, and :attr:`Emailkasten.Models.MailboxModel.updated` fields are read-only."""


    def update(self, instance, validated_data):
        """Extends :restframework::func:`serializers.ModelSerializer.update` to allow changing the daemon data."""
        daemonsData = validated_data.pop('daemons', [])
        for daemonData in daemonsData:
            daemon_id = daemonData.get('id', None)
            if daemon_id:
                daemonInstance = instance.daemons.get(id=daemon_id)
                for key, value in daemonData.items():
                    setattr(daemonInstance, key,value)
                daemonInstance.save()

        return super().update(instance, validated_data)


    def validate_fetching_criterion(self, value: str) -> str:
        """Checks whether the fetching criterion is available for the serialized mailbox.

        Args:
            value: The given fetching criterion.

        Returns:
            The validated fetching criterion.

        Raises:
            :restframework::class:`serializers.ValidationError`: If the given fetching criterion is not available for the mailbox.
        """
        if self.instance and value not in self.instance.getAvailableFetchingCriteria():
            raise serializers.ValidationError("Fetching criterion not available for this mailbox!")
        return value
