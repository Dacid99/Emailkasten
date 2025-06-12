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

"""Module with the :class:`web.views.DaemonUpdateView` view."""

from typing import Any, override

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views.generic import CreateView
from django_celery_beat.models import IntervalSchedule

from core.models import Daemon
from web.forms import IntervalScheduleForm

from ...forms import CreateDaemonForm


class DaemonCreateView(LoginRequiredMixin, CreateView):
    """View for creating a single :class:`core.models.Daemon` instance."""

    model = Daemon
    form_class = CreateDaemonForm
    template_name = "web/daemon/daemon_create.html"
    URL_NAME = Daemon.BASENAME + "-create"

    @override
    def get_form_kwargs(self) -> dict[str, Any]:
        """Extended to add the user to the form kwargs."""
        form_kwargs = super().get_form_kwargs()
        form_kwargs["user"] = self.request.user
        return form_kwargs

    @override
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Extended to add the form for interval to the context."""
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["interval_form"] = IntervalScheduleForm(self.request.POST)
        else:
            context["interval_form"] = IntervalScheduleForm()
        return context

    @override
    def form_valid(self, form: CreateDaemonForm) -> HttpResponse:
        """Extended to save the intervaldata.

        Important:
            There should not be duplicate IntervalSchedules.
            https://django-celery-beat.readthedocs.io/en/latest/index.html#example-creating-interval-based-periodic-task
        """
        context = self.get_context_data()
        interval_form = context["interval_form"]
        if interval_form.is_valid():
            interval, _ = IntervalSchedule.objects.get_or_create(
                every=interval_form.cleaned_data["every"],
                period=interval_form.cleaned_data["period"],
            )
            self.object = form.save(commit=False)
            self.object.interval = interval
            self.object.save()
            return super().form_valid(form)
        return self.form_invalid(form)
