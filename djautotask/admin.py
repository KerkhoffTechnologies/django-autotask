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
    actions = None
    change_form_template = 'change_form.html'
    list_display = (
        'id', 'start_time', 'end_time', 'duration_or_zero', 'entity_name',
        'success', 'added', 'updated', 'skipped', 'deleted', 'sync_type',
    )
    list_filter = ('sync_type', 'success', 'entity_name', )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

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
    list_display = ('id', 'label', 'is_active', 'is_system')


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


@admin.register(models.TaskCategory)
class TaskCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'label', 'is_active')


@admin.register(models.TaskType)
class TaskTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'label', 'is_active')


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


@admin.register(models.AccountType)
class AccountTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'label')


@admin.register(models.Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name')
    search_fields = ('id', 'first_name', 'last_name')
    list_filter = ('account__name', )

    def full_name(self, obj):
        return str(obj)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('account')


@admin.register(models.DisplayColor)
class DisplayColorAdmin(admin.ModelAdmin):
    list_display = ('id', 'label', 'is_active')


@admin.register(models.LicenseType)
class LicenseTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'label')


@admin.register(models.ServiceCallStatus)
class ServiceCallStatusAdmin(admin.ModelAdmin):
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
    list_display = ('id', 'name', 'type', 'number', 'active', 'parent_account')
    search_fields = ('id', 'name', 'number', 'parent_account__name')
    list_filter = ('active', 'type')


@admin.register(models.AccountPhysicalLocation)
class AccountPhysicalLocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'account', 'active')
    search_fields = ('id', 'name', 'account')
    list_filter = ('active',)


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
    list_filter = ('status',)
    search_fields = ('id', 'title', 'number', 'status__label', 'phase__title')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('phase', 'status')


@admin.register(models.TaskSecondaryResource)
class TaskSecondaryResourceAdmin(admin.ModelAdmin):
    list_display = ('id', 'resource', 'task')


@admin.register(models.Phase)
class PhaseTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'parent_phase')
    search_fields = ('id', 'title')


@admin.register(models.NoteType)
class NoteTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'label')


@admin.register(models.Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'hourly_rate')
    search_fields = ('id', 'name', 'description')


@admin.register(models.Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('id', 'name', 'description')


@admin.register(models.TicketNote)
class TicketNoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'ticket')
    search_fields = ('id', 'title')


@admin.register(models.TaskNote)
class TaskNoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'task')
    search_fields = ('id', 'title')


@admin.register(models.TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ('id', 'resource', 'ticket', 'task',
                    'date_worked', 'start_date_time', 'end_date_time')
    list_filter = ('resource', )
    search_fields = [
        'id', 'resource__user_name', 'ticket__title', 'task__title']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('resource', 'ticket', 'task')


@admin.register(models.TaskTypeLink)
class TaskTypeLinkAdmin(admin.ModelAdmin):
    list_display = ('id', 'label', 'is_active')
    search_fields = ('id', 'label')


@admin.register(models.UseType)
class UseTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'label', 'is_active')
    search_fields = ('id', 'label')


@admin.register(models.BillingCodeType)
class BillingCodeTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'label', 'is_active')
    search_fields = ('id', 'label')


@admin.register(models.BillingCode)
class BillingCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'active', 'use_type')
    list_filter = ('use_type', )
    search_fields = ('id', 'name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('use_type')


@admin.register(models.ResourceRoleDepartment)
class ResourceRoleDepartmentAdmin(admin.ModelAdmin):
    list_display = \
        ('id', 'resource', 'role', 'department', 'active', 'default')
    search_fields = (
        'id',
        'resource__first_name',
        'role__name',
        'department__name'
    )


@admin.register(models.ResourceServiceDeskRole)
class ResourceServiceDeskRoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'resource', 'role', 'active', 'default')
    search_fields = ('id', 'resource__first_name')


@admin.register(models.Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'number', 'account', 'status_name')
    search_fields = ('id', 'name', 'number')
    list_filter = ('status',)

    def status_name(self, obj):
        return obj.STATUS_CHOICES[int(obj.status)][1]


@admin.register(models.ServiceCall)
class ServiceCallAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'description',
        'creator_resource',
        'status',
        'duration',
        'start_date_time',
        'end_date_time',
    )
    search_fields = ('id', 'description')
    list_filter = ('status', 'creator_resource')


@admin.register(models.ServiceCallTicket)
class ServiceCallTicketAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'service_call',
        'ticket',
    )
    search_fields = ('id', 'service_call__description')


@admin.register(models.ServiceCallTask)
class ServiceCallTaskAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'service_call',
        'task',
    )
    search_fields = ('id', 'service_call__description')


@admin.register(models.ServiceCallTicketResource)
class ServiceCallTicketResourceAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'service_call_ticket',
        'resource',
    )
    search_fields = ('id', 'resource__first_name', 'resource__last_name')


@admin.register(models.ServiceCallTaskResource)
class ServiceCallTaskResourceAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'service_call_task',
        'resource',
    )
    search_fields = ('id', 'resource__first_name', 'resource__last_name')


@admin.register(models.TaskPredecessor)
class TaskPredecessorAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'predecessor_task', 'successor_task', 'lag_days'
    )
    search_fields = ('id', 'predecessor_task__title', 'successor_task__title')


@admin.register(models.TicketUDF)
class TicketUDFAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'is_picklist')
    search_fields = ['name', 'type']


@admin.register(models.TaskUDF)
class TaskUDFAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'is_picklist')
    search_fields = ['name', 'type']


@admin.register(models.ProjectUDF)
class ProjectUDFAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'type', 'is_picklist')
    search_fields = ['name', 'type']


@admin.register(models.ProjectNoteType)
class ProjectNoteTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'label')
