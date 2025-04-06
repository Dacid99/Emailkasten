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

"""Module with the :class:`core.backends.DaemonHealthCheckBackend.DaemonHealthCheckBackend` class."""

from health_check.backends import BaseHealthCheckBackend, HealthCheckException

from core.EMailArchiverDaemonRegistry import EMailArchiverDaemonRegistry


class DaemonHealthCheckBackend(BaseHealthCheckBackend):
    """Health check backend for :func:`core.EMailArchiverDaemonRegistry.EMailArchiverDaemonRegistry.healthcheck`."""

    critical_service = False

    def check_status(self) -> None:
        """Implements the healthcheck.

        Raises:
            HealthCheckException: If :func:`core.EMailArchiverDaemonRegistry.EMailArchiverDaemonRegistry.healthcheck` fails.
        """
        if not EMailArchiverDaemonRegistry.healthcheck():
            raise HealthCheckException("Daemons are unhealthy!")
