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

"""Module with the :class:`DaemonUpdateView` view."""

from typing import Any, override

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.views.generic.edit import DeletionMixin, UpdateView

from core.models.DaemonModel import DaemonModel
from web.views.daemon_views.DaemonFilterView import DaemonFilterView

from ...forms.daemon_forms.BaseDaemonForm import BaseDaemonForm


class DaemonUpdateOrDeleteView(LoginRequiredMixin, UpdateView, DeletionMixin):
    """View for updating or deleting a single :class:`core.models.DaemonModel.DaemonModel` instance."""

    model = DaemonModel
    form_class = BaseDaemonForm
    template_name = "daemon/daemon_edit.html"
    context_object_name = "daemon"
    URL_NAME = DaemonModel.get_edit_web_url_name()

    @override
    def get_success_url(self) -> str:
        """Overridden method to redirect to filter-list after `delete` else to detail."""
        if "delete" in self.request.POST:
            return reverse("web:" + DaemonFilterView.URL_NAME)
        return UpdateView.get_success_url(self)

    @override
    def get_queryset(self) -> QuerySet:
        """Restricts the queryset to objects owned by the requesting user."""
        return DaemonModel.objects.filter(mailbox__account__user=self.request.user)

    @override
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        """Overridden method to distinguish the `delete` button."""
        if "delete" in request.POST:
            return DeletionMixin.post(self, request, *args, **kwargs)
        return UpdateView.post(self, request, *args, **kwargs)
