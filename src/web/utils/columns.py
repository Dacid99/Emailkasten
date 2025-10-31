from typing import override

from django.utils.html import format_html
from django_tables2 import Column


class CheckboxColumn(Column):
    @override
    def __init__(
        self,
        verbose_name="",
        accessor=None,
        default=None,
        visible=True,
        orderable=False,
        attrs=None,
        order_by=None,
        empty_values=(),
        localize=None,
        footer=None,
        exclude_from_export=True,
        linkify=False,
        initial_sort_descending=False,
    ):
        super().__init__(
            verbose_name,
            accessor,
            default,
            visible,
            orderable,
            attrs,
            order_by,
            empty_values,
            localize,
            footer,
            exclude_from_export,
            linkify,
            initial_sort_descending,
        )

    @override
    def render(self, record):
        return format_html(
            '<label for="select-{id}" class="form-check-label visually-hidden">Select</label><input class="form-check-input" type="checkbox" id="select-{id}" data-id="{id}"/>',
            id=record.id,
        )
