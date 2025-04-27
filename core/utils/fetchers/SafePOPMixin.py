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

"""Module with the SafePOPMixin mixin."""

import logging
import poplib
from collections.abc import Callable
from typing import Any, Protocol, Self, TypeVar, overload

from django.utils.translation import gettext as _

from core.utils.fetchers.exceptions import FetcherError, MailAccountError


type POP3Response = bytes | tuple[bytes, list[bytes], int]

POP3ActionResponse = TypeVar("POP3ActionResponse", bound=POP3Response)


class POP3FetcherClass(Protocol):
    """Protocol defining the required attributes of a class implementing this mixin."""

    _mailClient: poplib.POP3
    logger: logging.Logger


class SafePOPMixin:
    """Mixin with safe POP operations.

    The implementing class must have
    an :attr:`_mailClient` that is an :class:`poplib.POP3` or :class:`poplib.POP3_SSL`
    and an instance logger.

    Only errors leading up to and during the fetching process should raise outside of the class.
    Otherwise issues with logout etc would destroy the work done with fetching, which makes no sense.
    """

    def checkResponse(
        self,
        response: POP3Response,
        commandName: str,
        exception: type[FetcherError] | None,
        expectedStatus: bytes = b"+OK",
    ) -> None:
        """Checks the status response of a POP action.

        If it doesnt match the expectation raises an exception.

        Todo:
            Safely! extract error message from response for logging and exception.

        Args:
            response: The complete response to the POP action.
            commandName: The name of the action.
            expectedStatus: The expected status response. Defaults to `"+OK"`.
            exception: The expection to raise if the status doesnt match the expectation. Defaults to :class:`core.utils.fetchers.exceptions.FetcherError`.

        Raises:
            exception: If the response status doesnt match the expectation.
        """
        status = response if isinstance(response, bytes) else response[0]
        if not status.startswith(expectedStatus):
            self.logger.error("Bad server response for %s:\n%s", commandName, response)
            if exception is not None:
                raise exception(
                    _("Bad server response for %(commandName)s:\n%(response)s")
                    % {"commandName": commandName, "response": response}
                )
        self.logger.debug("Server responded %s as expected.", status)

    @overload
    @staticmethod
    def safe(
        exception: type[FetcherError],
        expectedStatus: bytes = b"+OK",
    ) -> Callable[
        [Callable[..., POP3ActionResponse]], Callable[..., POP3ActionResponse]
    ]: ...

    @overload
    @staticmethod
    def safe(
        exception: None,
        expectedStatus: bytes = b"+OK",
    ) -> Callable[
        [Callable[..., POP3ActionResponse]], Callable[..., POP3ActionResponse | None]
    ]: ...

    @staticmethod
    def safe(
        exception: type[FetcherError] | None,
        expectedStatus: bytes = b"+OK",
    ) -> Callable[
        [Callable[..., POP3ActionResponse]], Callable[..., POP3ActionResponse | None]
    ]:
        """Wrapper for POP actions.

        Catches expected errors and checks for correct responses and raises an FetcherError.

        Todo:
            Find a better way to disable the exception and getting rid of the typing mess.

        Args:
            expectedStatus: The expected status response. Defaults to `"+OK"`.
            exception: The exception to raise if an error occurs or the status doesnt match the expectation.
                Defaults to :class:`core.utils.fetchers.exceptions.FetcherError`.
                If `None` is passed, no exception is raised, all errors are logged nonetheless.

        Returns:
            The return value of the wrapped action.
            None if an error occurs and `exception` is `None`.

        Raises:
            exception: If an error occurs or the status doesnt match the expectation.
        """

        def safeWrapper(
            popAction: Callable[..., POP3ActionResponse],
        ) -> Callable[..., POP3ActionResponse | None]:
            def safeAction(
                self: Self, *args: Any, **kwargs: Any
            ) -> POP3ActionResponse | None:
                try:
                    response = popAction(self, *args, **kwargs)
                except Exception as error:
                    self.logger.exception(
                        "An %s occured during %s!",
                        error.__class__.__name__,
                        popAction.__name__,
                    )
                    if exception is not None:
                        raise exception(
                            _("An %(error_class_name)s occured during %(action_name)s!")
                            % {
                                "error_class_name": error.__class__.__name__,
                                "action_name": popAction.__name__,
                            },
                        ) from error
                    return None
                else:
                    self.checkResponse(
                        response, popAction.__name__, exception, expectedStatus
                    )
                return response

            return safeAction

        return safeWrapper

    @safe(exception=MailAccountError)
    def safe_user(self: POP3FetcherClass, *args: Any, **kwargs: Any) -> bytes:
        """The :func:`safe` wrapped version of :func:`poplib.POP3.user`."""
        return self._mailClient.user(*args, **kwargs)

    @safe(exception=MailAccountError)
    def safe_pass_(self: POP3FetcherClass, *args: Any, **kwargs: Any) -> bytes:
        """The :func:`safe` wrapped version of :func:`poplib.POP3.pass_`."""
        return self._mailClient.pass_(*args, **kwargs)

    @safe(exception=MailAccountError)
    def safe_noop(self: POP3FetcherClass, *args: Any, **kwargs: Any) -> bytes:
        """The :func:`safe` wrapped version of :func:`poplib.POP3.noop`."""
        return self._mailClient.noop(*args, **kwargs)

    @safe(exception=MailAccountError)
    def safe_list(
        self: POP3FetcherClass, *args: Any, **kwargs: Any
    ) -> tuple[bytes, list[bytes], int]:
        """The :func:`safe` wrapped version of :func:`poplib.POP3.list`."""
        return self._mailClient.list(*args, **kwargs)

    @safe(exception=MailAccountError)
    def safe_retr(
        self: POP3FetcherClass, *args: Any, **kwargs: Any
    ) -> tuple[bytes, list[bytes], int]:
        """The :func:`safe` wrapped version of :func:`poplib.POP3.retr`."""
        return self._mailClient.retr(*args, **kwargs)

    @safe(exception=None)
    def safe_quit(self: POP3FetcherClass, *args: Any, **kwargs: Any) -> bytes:
        """The :func:`safe` wrapped version of :func:`poplib.POP3.quit`."""
        return self._mailClient.quit(*args, **kwargs)
