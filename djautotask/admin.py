from django.contrib import admin
import datetime

from . import models


class TicketSecondaryResourceInline(admin.StackedInline):
    model = models.TicketSecondaryResource


@admin.register(models.Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'ticket_number', 'status')
    search_fields = ('id', 'title', 'ticket_number', 'status')

    inlines = [
        TicketSecondaryResourceInline
    ]


@admin.register(models.SyncJob)
class SyncJobAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'start_time', 'end_time', 'duration_or_zero', 'entity_name',
        'success', 'added', 'updated', 'deleted', 'sync_type',
    )
    list_filter = ('sync_type', 'success', 'entity_name', )

    def duration_or_zero(self, obj):
        """
        Return the duration, or just the string 0 (otherwise we get 0:00:00)
        """
        duration = obj.duration()
        if duration:
            # Get rid of the microseconds part
            duration_seconds = duration - datetime.timedelta(
                microseconds=duration.microseconds
            )
            return duration_seconds if duration_seconds else '0'
    duration_or_zero.short_description = 'Duration'


@admin.register(models.TicketStatus)
class TicketStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'label', 'value')


@admin.register(models.Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'full_name', 'email', 'active')
    search_fields = ('user_name', 'first_name', 'last_name', 'email')

    def full_name(self, obj):
        return str(obj)


@admin.register(models.TicketSecondaryResource)
class TicketSecondaryResourceAdmin(admin.ModelAdmin):
    list_display = ('id', 'resource', 'ticket')