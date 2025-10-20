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

"""Module with the :class:`UserProfileViewSet` viewset."""

from __future__ import annotations

from typing import TYPE_CHECKING

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated

from api.v1.serializers import UserProfileSerializer
from Emailkasten.models import UserProfile


if TYPE_CHECKING:
    from django.db.models import QuerySet


@extend_schema_view(
    retrieve=extend_schema(description="Retrieves the user profile data."),
    update=extend_schema(description="Updates the user profile data."),
)
class UserProfileView(RetrieveUpdateAPIView):
    """View for retrieving and updating the users :class:`Emailkasten.models.UserProfile`."""

    NAME = "profile"
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self) -> QuerySet[UserProfile]:
        """Fetches the profile connected to the request user.

        Returns:
            The UserProfile model of the request user.
        """
        if getattr(self, "swagger_fake_view", False):
            return UserProfile.objects.none()
        return self.request.user.profile
