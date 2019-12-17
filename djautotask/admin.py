from django.contrib import admin
import datetime

from . import models


class TicketSecondaryResourceInline(admin.StackedInline):
    model = models.TicketSecondaryResource


@admin.register(models.Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'ticket_number', 'status')
    list_filter = ('status',)
    search_fields = ('id', 'title', 'ticket_number', 'status__label')

    inlines = [
        TicketSecondaryResourceInline
    ]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('status')


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


@admin.register(models.Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'label')


@admin.register(models.Priority)
class PriorityAdmin(admin.ModelAdmin):
    list_display = ('id', 'label')


@admin.register(models.Queue)
class QueueAdmin(admin.ModelAdmin):
    list_display = ('id', 'label')


@admin.register(models.ProjectStatus)
class ProjectStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'label', 'is_active')


@admin.register(models.ProjectType)
class ProjectTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'label')


@admin.register(models.TicketCategory)
class TicketCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'active')


@admin.register(models.Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ('id', 'label')


@admin.register(models.IssueType)
class IssueTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'label')


@admin.register(models.SubIssueType)
class SubIssueType(admin.ModelAdmin):
    list_display = ('id', 'label')


@admin.register(models.TicketType)
class TicketTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'label')


@admin.register(models.DisplayColor)
class DisplayColorAdmin(admin.ModelAdmin):
    list_display = ('id', 'label', 'is_active')


@admin.register(models.LicenseType)
class LicenseTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'label')


@admin.register(models.Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = (
        'user_name', 'full_name', 'email', 'active', 'license_type'
    )
    list_filter = ('active', 'license_type')
    search_fields = ('user_name', 'first_name', 'last_name', 'email')

    def full_name(self, obj):
        return str(obj)


@admin.register(models.TicketSecondaryResource)
class TicketSecondaryResourceAdmin(admin.ModelAdmin):
    list_display = ('id', 'resource', 'ticket')


@admin.register(models.Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'number', 'active')
    search_fields = ('id', 'name', 'number')


@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'number', 'type', 'status')
    list_filter = ('type', 'status')
    search_fields = ('id', 'name', 'number')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('type', 'status')


@admin.register(models.Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'number', 'status', 'phase')
    list_filter = ('status', 'phase')
    search_fields = ('id', 'title', 'number', 'status', 'phase')


@admin.register(models.TaskSecondaryResource)
class TaskSecondaryResourceAdmin(admin.ModelAdmin):
    list_display = ('id', 'resource', 'task')


@admin.register(models.Phase)
class PhaseTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'parent_phase')
    search_fields = ('id', 'title')
