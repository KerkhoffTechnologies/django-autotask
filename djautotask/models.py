import pytz

from django.db import models
from django.db.models import Q
from django_extensions.db.models import TimeStampedModel
from django.utils import timezone
from model_utils import FieldTracker

from djautotask.api import ProjectsAPIClient, TaskNotesAPIClient, \
    TicketsAPIClient, ServiceCallsAPIClient, TimeEntriesAPIClient, \
    TicketNotesAPIClient

OFFSET_TIMEZONE = 'America/New_York'


class SyncJob(models.Model):
    start_time = models.DateTimeField(null=False)
    end_time = models.DateTimeField(blank=True, null=True)
    entity_name = models.CharField(max_length=100)
    added = models.PositiveIntegerField(null=True)
    updated = models.PositiveIntegerField(null=True)
    skipped = models.PositiveIntegerField(null=True)
    deleted = models.PositiveIntegerField(null=True)
    success = models.BooleanField(null=True)
    message = models.TextField(blank=True, null=True)
    sync_type = models.CharField(max_length=32, default='full')

    def duration(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time


class Ticket(TimeStampedModel):
    ticket_number = models.CharField(blank=True, null=True, max_length=50)
    completed_date = models.DateTimeField(blank=True, null=True)
    create_date = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True, max_length=8000)
    due_date_time = models.DateTimeField(null=False)
    estimated_hours = models.DecimalField(
        blank=True, null=True, decimal_places=2, max_digits=9)
    last_activity_date = models.DateTimeField(blank=True, null=True)
    title = models.CharField(blank=True, null=True, max_length=255)
    first_response_date_time = models.DateTimeField(blank=True, null=True)
    first_response_due_date_time = models.DateTimeField(blank=True, null=True)
    resolution_plan_date_time = models.DateTimeField(blank=True, null=True)
    resolution_plan_due_date_time = models.DateTimeField(blank=True, null=True)
    resolved_date_time = models.DateTimeField(blank=True, null=True)
    resolved_due_date_time = models.DateTimeField(blank=True, null=True)
    service_level_agreement = models.IntegerField(blank=True, null=True)
    service_level_agreement_has_been_met = models.BooleanField(default=False)
    service_level_agreement_paused_next_event_hours = models.DecimalField(
        blank=True, null=True, decimal_places=2, max_digits=9)
    checklist_completed = models.PositiveSmallIntegerField(
        blank=True, null=True)
    checklist_total = models.PositiveSmallIntegerField(blank=True, null=True)

    status = models.ForeignKey(
        'Status', blank=True, null=True, on_delete=models.SET_NULL
    )
    priority = models.ForeignKey(
        'Priority', blank=True, null=True, on_delete=models.SET_NULL
    )
    assigned_resource = models.ForeignKey(
        'Resource', blank=True, null=True, on_delete=models.SET_NULL
    )
    secondary_resources = models.ManyToManyField(
        'Resource', through='TicketSecondaryResource',
        related_name='secondary_resource_tickets'
    )
    queue = models.ForeignKey(
        'Queue', blank=True, null=True, on_delete=models.SET_NULL
    )
    contact = models.ForeignKey(
        'Contact', blank=True, null=True, on_delete=models.SET_NULL
    )
    account = models.ForeignKey(
        'Account', blank=True, null=True, on_delete=models.SET_NULL
    )
    account_physical_location = models.ForeignKey(
        'AccountPhysicalLocation', blank=True, null=True,
        on_delete=models.SET_NULL
    )
    project = models.ForeignKey(
        'Project', blank=True, null=True, on_delete=models.SET_NULL
    )
    category = models.ForeignKey(
        'TicketCategory', blank=True, null=True, on_delete=models.SET_NULL
    )
    source = models.ForeignKey(
        'Source', blank=True, null=True, on_delete=models.SET_NULL
    )
    issue_type = models.ForeignKey(
        'IssueType', blank=True, null=True, on_delete=models.SET_NULL
    )
    sub_issue_type = models.ForeignKey(
        'SubIssueType', blank=True, null=True, on_delete=models.SET_NULL
    )
    type = models.ForeignKey(
        'TicketType', blank=True, null=True, on_delete=models.SET_NULL
    )
    assigned_resource_role = models.ForeignKey(
        'Role', blank=True, null=True, on_delete=models.SET_NULL
    )
    billing_code = models.ForeignKey(
        'BillingCode', null=True, blank=True, on_delete=models.SET_NULL
    )
    contract = models.ForeignKey(
        'Contract', null=True, blank=True, on_delete=models.SET_NULL
    )
    udf = models.JSONField(blank=True, null=True, default=dict)

    AUTOTASK_FIELDS = {
        'title': 'title',
        'description': 'description',
        'queue': 'queueID',
        'estimated_hours': 'estimatedHours',
        'due_date_time': 'dueDateTime',
        'status': 'status',
        'priority': 'priority',
        'category': 'ticketCategory',
        'billing_code': 'billingCodeID',
        'issue_type': 'issueType',
        'sub_issue_type': 'subIssueType',
        'project': 'projectID',
        'assigned_resource': 'assignedResourceID',
        'assigned_resource_role': 'assignedResourceRoleID',
        'account': 'companyID',
        'account_physical_location': 'companyLocationID',
        'contact': 'contactID',
        'contract': 'contractID',
    }

    class Meta:
        verbose_name = 'Ticket'

    def __str__(self):
        return '{}-{}'.format(self.id, self.title)

    def get_account(self):
        return self.account


class AvailablePicklistManager(models.Manager):
    """ Return only active Picklist objects. """

    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class Picklist(TimeStampedModel):
    label = models.CharField(blank=True, null=True, max_length=50)
    is_default_value = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
    is_system = models.BooleanField(default=False)

    objects = models.Manager()
    available_objects = AvailablePicklistManager()

    class Meta:
        ordering = ('label',)
        abstract = True

    def __str__(self):
        return self.label if self.label else self.pk


class Status(Picklist):
    # Ticket/task statuses New, Waiting Customer, and Complete are
    # system statuses in Autotask that cannot be edited or deactivated.
    COMPLETE_ID = 5

    class Meta:
        ordering = ('label',)
        verbose_name_plural = 'Statuses'

    def is_complete(self):
        return self.id == Status.COMPLETE_ID


class Priority(Picklist):

    class Meta:
        ordering = ('sort_order',)
        verbose_name_plural = 'Priorities'


class Queue(Picklist):
    label = models.CharField(blank=True, null=True, max_length=100)

    class Meta:
        ordering = ('label',)
        verbose_name_plural = 'Queues'


class ProjectStatus(Picklist):
    COMPLETE_ID = 5

    class Meta:
        ordering = ('label',)
        verbose_name_plural = 'Project statuses'

    def is_complete(self):
        return self.id == ProjectStatus.COMPLETE_ID


class DisplayColor(Picklist):

    class Meta:
        ordering = ('label',)
        verbose_name_plural = 'Display colors'


class ProjectType(Picklist):
    TEMPLATE = 'Template'
    BASELINE = 'Baseline'


class Source(Picklist):
    pass


class IssueType(Picklist):
    pass


class TicketType(Picklist):
    pass


class TaskCategory(Picklist):
    class Meta:
        verbose_name_plural = 'Task categories'


class SubIssueType(Picklist):
    parent_value = models.ForeignKey(
        'IssueType', blank=True, null=True, on_delete=models.CASCADE
    )

    def __str__(self):
        return "{}/{}".format(self.parent_value, self.label) \
            if self.parent_value else self.label


class LicenseType(Picklist):
    # We expect this id's is fixed and immutable.
    impersonation_limited_type = {
        'TEAM_MEMBER': 4,
        'CONTRACTOR': 8,
        'CO_HELP_DESK': 9,
    }
    impersonation_disabled_type = {
        'TIME_ATTENDANCE': 5,
        'DASHBOARD': 6,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_limited_impersonation_targets()

    def has_impersonation(self, target):
        if self.id in self.impersonation_disabled_type.values():
            return False

        if self.id in self.impersonation_limited_type.values():
            return self.check_impersonation(target)

        return True

    def init_limited_impersonation_targets(self):

        if self.id == self.impersonation_limited_type['TEAM_MEMBER']:
            self.limited_impersonation_targets = [
                ProjectsAPIClient,
                TaskNotesAPIClient,
            ]
        elif self.id == \
                self.impersonation_limited_type['CONTRACTOR']:
            self.limited_impersonation_targets = [
                TicketsAPIClient,
                ProjectsAPIClient,
                ServiceCallsAPIClient,
                TimeEntriesAPIClient,
                TicketNotesAPIClient,
                TaskNotesAPIClient,
            ]
        elif self.id == \
                self.impersonation_limited_type['CO_HELP_DESK']:
            self.limited_impersonation_targets = [
                TicketsAPIClient,
                ProjectsAPIClient,
                TaskNotesAPIClient,
            ]
        else:
            self.limited_impersonation_targets = []

    def check_impersonation(self, target):
        for limited_target in self.limited_impersonation_targets:
            if isinstance(target, limited_target):
                return False

        return True


class AccountType(Picklist):
    pass


class NoteType(Picklist):
    SUMMARY = 1
    DETAIL = 2
    NOTES = 3
    # Workflow Rule Note - Task is an Autotask system note type that cannot
    # be edited or deactivated.
    WORKFLOW_RULE_NOTE_ID = 13
    RMM_NOTE = 99


class ProjectNoteType(Picklist):
    NOTES = 5
    EMAIL = 8
    STATUS = 12


class TaskTypeLink(Picklist):
    pass


class UseType(Picklist):
    pass


class BillingCodeType(Picklist):
    NORMAL = 0
    SYSTEM = 1
    NON_BILLABLE = 2


class ServiceCallStatus(Picklist):

    class Meta:
        ordering = ('label',)
        verbose_name_plural = 'Service call statuses'


class TaskType(Picklist):
    pass


class RegularResourceManager(models.Manager):
    API_USER_LICENSE_ID = 7

    def get_queryset(self):
        return super().get_queryset().exclude(
            license_type=self.API_USER_LICENSE_ID)


class Resource(TimeStampedModel):
    user_name = models.CharField(max_length=32)
    email = models.CharField(max_length=250)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    active = models.BooleanField(default=False)
    license_type = models.ForeignKey(
        'LicenseType', null=True, on_delete=models.SET_NULL
    )
    default_service_desk_role = models.ForeignKey(
        'Role', null=True, blank=True, on_delete=models.SET_NULL
    )

    objects = models.Manager()
    regular_objects = RegularResourceManager()

    class Meta:
        ordering = ('first_name', 'last_name')

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)


class TicketCategory(TimeStampedModel):
    # default system id to be used for creating tickets
    STANDARD_ID = 3

    name = models.CharField(max_length=30)
    active = models.BooleanField(default=False)
    display_color = models.ForeignKey(
        'DisplayColor', null=True, on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ('name',)
        verbose_name_plural = 'Ticket categories'

    def __str__(self):
        return self.name


class TicketSecondaryResource(TimeStampedModel):
    resource = models.ForeignKey(
        'Resource', blank=True, null=True, on_delete=models.SET_NULL
    )
    ticket = models.ForeignKey(
        'Ticket', blank=True, null=True, on_delete=models.SET_NULL
    )
    role = models.ForeignKey(
        'Role', null=True, blank=True, on_delete=models.SET_NULL
    )

    AUTOTASK_FIELDS = {
        'resource': 'resourceID',
        'ticket': 'ticketID',
        'role': 'roleID',
    }

    def __str__(self):
        return '{} {}'.format(self.resource, self.ticket)


class Note:
    ALL_USERS = 1
    INTERNAL_USERS = 2
    PUBLISH_CHOICES = (
        (ALL_USERS, 'All Autotask Users'),
        (INTERNAL_USERS, 'Internal Users')
    )
    AUTOTASK_FIELDS = {
        'title': 'title',
        'description': 'description',
        'note_type': 'noteType',
        'publish': 'publish',
        'created_by_contact_id': 'createdByContactID',
    }

    def is_internal(self):
        return self.publish == str(Note.INTERNAL_USERS)


class NonInternalTicketNoteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(publish=Note.INTERNAL_USERS)


class TicketNote(TimeStampedModel, Note):
    title = models.CharField(max_length=250)
    description = models.CharField(max_length=3200)
    create_date_time = models.DateTimeField(blank=True, null=True)
    last_activity_date = models.DateTimeField(blank=True, null=True)

    note_type = models.ForeignKey(
        'NoteType', blank=True, null=True, on_delete=models.SET_NULL)
    creator_resource = models.ForeignKey(
        'Resource', blank=True, null=True, on_delete=models.SET_NULL)
    publish = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=Note.PUBLISH_CHOICES
    )
    ticket = models.ForeignKey(
        'Ticket', blank=True, null=True, on_delete=models.SET_NULL,
        related_name='notes'
    )
    created_by_contact = models.ForeignKey(
        'Contact', blank=True, null=True, on_delete=models.SET_NULL
    )

    objects = models.Manager()
    non_internal_objects = NonInternalTicketNoteManager()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        super().AUTOTASK_FIELDS.update({
            'ticket': 'ticketID',
        })


class NonInternalTaskNoteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(publish=Note.INTERNAL_USERS)


class TaskNote(TimeStampedModel, Note):
    title = models.CharField(max_length=250)
    description = models.CharField(max_length=3200)
    create_date_time = models.DateTimeField(blank=True, null=True)
    last_activity_date = models.DateTimeField(blank=True, null=True)

    note_type = models.ForeignKey(
        'NoteType', blank=True, null=True, on_delete=models.SET_NULL)
    creator_resource = models.ForeignKey(
        'Resource', blank=True, null=True, on_delete=models.SET_NULL)
    publish = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=Note.PUBLISH_CHOICES)
    task = models.ForeignKey(
        'Task',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='notes'
    )
    created_by_contact = models.ForeignKey(
        'Contact', blank=True, null=True, on_delete=models.SET_NULL
    )

    objects = models.Manager()
    non_internal_objects = NonInternalTaskNoteManager()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        super().AUTOTASK_FIELDS.update({
            'task': 'taskID',
        })


class Contact(TimeStampedModel):

    first_name = models.CharField(blank=True, null=True, max_length=200,
                                  db_index=True)
    last_name = models.CharField(blank=True, null=True, max_length=200,
                                 db_index=True)
    email_address = models.CharField(blank=True, null=True, max_length=200)
    email_address2 = models.CharField(blank=True, null=True, max_length=200)
    email_address3 = models.CharField(blank=True, null=True, max_length=200)
    phone = models.CharField(blank=True, null=True, max_length=200)
    alternate_phone = models.CharField(blank=True, null=True, max_length=200)
    mobile_phone = models.CharField(blank=True, null=True, max_length=200)
    extension = models.CharField(blank=True, null=True, max_length=10)
    account = models.ForeignKey(
        'Account', blank=True, null=True, on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ('first_name', 'last_name')

    def __str__(self):
        return '{} {}'.format(self.first_name,
                              self.last_name if self.last_name else '')


class Account(TimeStampedModel):
    MY_ACCOUNT = 0
    name = models.CharField(max_length=100,
                            db_index=True)
    number = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    last_activity_date = models.DateTimeField(blank=True, null=True)
    phone = models.CharField(blank=True, null=True, max_length=200)
    type = models.ForeignKey(
        'AccountType', blank=True, null=True, on_delete=models.SET_NULL
    )
    parent_account = models.ForeignKey(
        'Account', blank=True, null=True, on_delete=models.SET_NULL
    )
    owner_resource = models.ForeignKey(
        'Resource', blank=True, null=True, on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class AccountPhysicalLocation(models.Model):
    name = models.CharField(max_length=100)
    active = models.BooleanField(default=True)
    primary = models.BooleanField(default=True)
    account = models.ForeignKey(
        'Account', blank=True, null=True, on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class AvailableProjectManager(models.Manager):
    """
    Exclude projects whose type is 'Template' or 'Baseline'. Neither of these
    types provide any use for us, so just exclude them.
    """
    def get_queryset(self):
        return super().get_queryset().exclude(
            Q(type__label=ProjectType.TEMPLATE) |
            Q(type__label=ProjectType.BASELINE)
        )


class Project(TimeStampedModel):
    name = models.CharField(max_length=100)
    number = models.CharField(null=True, max_length=50)
    description = models.CharField(max_length=2000)
    actual_hours = models.DecimalField(
        null=True, decimal_places=2, max_digits=9)
    completed_date = models.DateField(null=True)
    completed_percentage = models.PositiveSmallIntegerField(default=0)
    duration = models.PositiveIntegerField(default=0)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    estimated_time = models.DecimalField(
        null=True, decimal_places=2, max_digits=9
    )
    last_activity_date_time = models.DateTimeField(null=True)
    status_detail = models.CharField(max_length=2000, blank=True, null=True)

    project_lead_resource = models.ForeignKey(
        'Resource', null=True, on_delete=models.SET_NULL
    )
    contact = models.ForeignKey(
        'Contact', blank=True, null=True, on_delete=models.SET_NULL
    )
    account = models.ForeignKey(
        'Account', null=True, on_delete=models.SET_NULL
    )
    status = models.ForeignKey(
        'ProjectStatus', null=True, on_delete=models.SET_NULL
    )
    type = models.ForeignKey(
        'ProjectType', null=True, on_delete=models.SET_NULL
    )
    contract = models.ForeignKey(
        'Contract', null=True, blank=True, on_delete=models.SET_NULL
    )
    department = models.ForeignKey(
        'Department', null=True, blank=True, on_delete=models.SET_NULL
    )
    udf = models.JSONField(blank=True, null=True, default=dict)

    AUTOTASK_FIELDS = {
        'name': 'projectName',
        'status': 'status',
        'description': 'description',
        'start_date': 'startDateTime',
        'end_date': 'endDateTime',
        'type': 'projectType',
        'project_lead_resource': 'projectLeadResourceID',
        'department': 'department',
        'status_detail': 'statusDetail',
    }

    objects = models.Manager()
    available_objects = AvailableProjectManager()

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Phase(TimeStampedModel):
    title = models.CharField(blank=True, null=True, max_length=255)
    description = models.CharField(blank=True, null=True, max_length=8000)
    start_date = models.DateTimeField(blank=True, null=True)
    # due_date is end date in autotask UI
    due_date = models.DateTimeField(blank=True, null=True)
    estimated_hours = models.DecimalField(default=0.0, decimal_places=2,
                                          max_digits=9)
    number = models.CharField(blank=True, null=True, max_length=50)
    scheduled = models.BooleanField(default=False)
    last_activity_date = models.DateTimeField(blank=True, null=True)

    parent_phase = models.ForeignKey(
        'self', null=True, on_delete=models.SET_NULL
    )

    project = models.ForeignKey(
        'Project', null=True, on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return self.title


class Task(TimeStampedModel):
    MAX_DESCRIPTION = 8000
    title = models.CharField(blank=True, null=True, max_length=255)
    number = models.CharField(blank=True, null=True, max_length=50)
    description = models.TextField(blank=True, null=True,
                                   max_length=MAX_DESCRIPTION)
    completed_date = models.DateTimeField(blank=True, null=True)
    create_date = models.DateTimeField(blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)
    estimated_hours = models.DecimalField(
        blank=True, null=True, decimal_places=2, max_digits=9)
    remaining_hours = models.DecimalField(
        blank=True, null=True, decimal_places=2, max_digits=9)
    last_activity_date = models.DateTimeField(blank=True, null=True)

    assigned_resource = models.ForeignKey(
        'Resource', null=True, on_delete=models.SET_NULL
    )
    secondary_resources = models.ManyToManyField(
        'Resource', through='TaskSecondaryResource',
        related_name='secondary_resource_tasks'
    )
    project = models.ForeignKey(
        'Project', on_delete=models.CASCADE
    )
    priority = models.ForeignKey(
        'Priority', null=True, blank=True, on_delete=models.SET_NULL
    )
    status = models.ForeignKey(
        'Status', null=True, on_delete=models.SET_NULL
    )
    phase = models.ForeignKey(
        'Phase', null=True,
        on_delete=models.SET_NULL
    )
    billing_code = models.ForeignKey(
        'BillingCode', null=True, blank=True, on_delete=models.SET_NULL
    )
    assigned_resource_role = models.ForeignKey(
        'Role', blank=True, null=True, on_delete=models.SET_NULL
    )
    department = models.ForeignKey(
        'Department', blank=True, null=True, on_delete=models.SET_NULL
    )
    category = models.ForeignKey(
        'TaskCategory', null=True, blank=True, on_delete=models.SET_NULL
    )
    task_type = models.ForeignKey(
        'TaskType', null=True, blank=True, on_delete=models.SET_NULL
    )
    udf = models.JSONField(blank=True, null=True, default=dict)

    AUTOTASK_FIELDS = {
        'title': 'title',
        'description': 'description',
        'start_date': 'startDateTime',
        'end_date': 'endDateTime',
        'estimated_hours': 'estimatedHours',
        'remaining_hours': 'remainingHours',
        'status': 'status',
        'department': 'departmentID',
        'billing_code': 'billingCodeID',
        'priority': 'priorityLabel',
        'phase': 'phaseID',
        'assigned_resource': 'assignedResourceID',
        'assigned_resource_role': 'assignedResourceRoleID',
        'category': 'taskCategoryID',
    }

    def __str__(self):
        return self.title

    def get_account(self):
        return getattr(self.project, 'account', None)


class TaskSecondaryResource(TimeStampedModel):
    resource = models.ForeignKey(
        'Resource', blank=True, null=True, on_delete=models.SET_NULL
    )
    task = models.ForeignKey(
        'Task', blank=True, null=True, on_delete=models.SET_NULL
    )
    role = models.ForeignKey(
        'Role', null=True, blank=True, on_delete=models.SET_NULL
    )

    AUTOTASK_FIELDS = {
        'resource': 'resourceID',
        'task': 'taskID',
        'role': 'roleID',
    }

    def __str__(self):
        return '{} {}'.format(self.resource, self.task)


class TimeEntry(TimeStampedModel):
    date_worked = models.DateTimeField(blank=True, null=True)
    start_date_time = models.DateTimeField(blank=True, null=True)
    end_date_time = models.DateTimeField(blank=True, null=True)
    summary_notes = models.TextField(blank=True, null=True, max_length=8000)
    internal_notes = models.TextField(blank=True, null=True, max_length=8000)
    non_billable = models.BooleanField(default=False)
    hours_worked = models.DecimalField(
        blank=True, null=True, decimal_places=4, max_digits=9)
    hours_to_bill = models.DecimalField(
        blank=True, null=True, decimal_places=4, max_digits=9)
    offset_hours = models.DecimalField(
        blank=True, null=True, decimal_places=4, max_digits=9)

    resource = models.ForeignKey(
        'Resource', blank=True, null=True, on_delete=models.CASCADE)
    ticket = models.ForeignKey(
        'Ticket', blank=True, null=True, on_delete=models.CASCADE)
    task = models.ForeignKey(
        'Task', blank=True, null=True, on_delete=models.CASCADE)
    type = models.ForeignKey(
        'TaskTypeLink', blank=True, null=True, on_delete=models.SET_NULL)
    billing_code = models.ForeignKey(
        'BillingCode', blank=True, null=True, on_delete=models.SET_NULL)
    role = models.ForeignKey(
        'Role', blank=True, null=True, on_delete=models.SET_NULL
    )
    contract = models.ForeignKey(
        'Contract', blank=True, null=True, on_delete=models.SET_NULL
    )

    AUTOTASK_FIELDS = {
        'ticket': 'ticketID',
        'task': 'taskID',
        'date_worked': 'dateWorked',
        'start_date_time': 'startDateTime',
        'end_date_time': 'endDateTime',
        'summary_notes': 'summaryNotes',
        'internal_notes': 'internalNotes',
        'hours_worked': 'hoursWorked',
        'offset_hours': 'offsetHours',
        'role': 'roleID',
        'resource': 'resourceID',
        'billing_code': 'billingCodeID',
        'contract': 'contractID',
        'show_on_invoice': 'showOnInvoice',
    }

    class Meta:
        verbose_name_plural = 'Time entries'
        ordering = ('-start_date_time', '-date_worked', '-id')

    def __str__(self):
        return str(self.id) or ''

    def get_entered_time(self):
        """
        In Autotask, tickets are required to have start and end times.
        Start and end times for project tasks can be optional.
        In the case that a task has no start or end time, use the
        date_worked field.
        """
        if self.end_date_time:
            entered_time = self.end_date_time
        else:
            # Autotask gives us date_worked as a datetime, even though the
            # time is always set to EST midnight (00:00:00).
            # TODO timezone.pytz does not exist anymore
            est_offset = timezone.localtime(
                timezone=pytz.timezone(OFFSET_TIMEZONE)).utcoffset()
            local_offset = timezone.localtime().utcoffset()

            # We want to end up with a UTC datetime that is midnight in the
            # local timezone.
            date_worked = self.date_worked + est_offset
            entered_time = date_worked - local_offset

        return entered_time


class BillingCode(TimeStampedModel):
    # BillingCodes with use type General Allocation Code (with ID = 1)
    # are for setting a ticket's work type in the UI. See API docs for details.
    # https://ww2.autotask.net/help/DeveloperHelp/Content/APIs/REST/Entities/BillingCodesEntity.htm # noqa
    GENERAL_BILLING_CODE_ID = 1
    name = models.CharField(blank=True, null=True, max_length=200)
    description = models.CharField(blank=True, null=True, max_length=500)
    active = models.BooleanField(default=False)

    use_type = models.ForeignKey(
        'UseType', blank=True, null=True, on_delete=models.SET_NULL
    )
    billing_code_type = models.ForeignKey(
        'BillingCodeType', blank=True, null=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.name if self.name else self.pk


class Role(models.Model):
    name = models.CharField(max_length=200)
    active = models.BooleanField(default=True)
    description = models.CharField(blank=True, null=True, max_length=200)
    hourly_factor = models.DecimalField(
        blank=True, null=True, decimal_places=2, max_digits=9)
    hourly_rate = models.DecimalField(
        blank=True, null=True, decimal_places=2, max_digits=9)
    role_type = models.PositiveIntegerField(blank=True, null=True)
    system_role = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True, max_length=1000)
    number = models.CharField(blank=True, null=True, max_length=50)

    def __str__(self):
        return self.name


class ResourceRoleDepartment(models.Model):
    id = models.BigAutoField(primary_key=True, verbose_name='ID')
    active = models.BooleanField(default=True)
    default = models.BooleanField(default=False)
    department_lead = models.BooleanField(default=False)

    def __str__(self):
        return "{} - {} - {}".format(
            self.resource, self.role, self.department)

    department = models.ForeignKey(
        'Department', on_delete=models.CASCADE)
    role = models.ForeignKey(
        'Role', on_delete=models.CASCADE)
    resource = models.ForeignKey(
        'Resource', on_delete=models.CASCADE)


class ResourceServiceDeskRole(models.Model):
    active = models.BooleanField(default=True)
    default = models.BooleanField(default=False)

    def __str__(self):
        return "{} - {}".format(
            self.resource, self.role)

    role = models.ForeignKey(
        'Role', on_delete=models.CASCADE)
    resource = models.ForeignKey(
        'Resource', on_delete=models.CASCADE)


class Contract(models.Model):
    INACTIVE = 0
    ACTIVE = 1
    STATUS_CHOICES = (
        (INACTIVE, 'Inactive'),
        (ACTIVE, 'Active')
    )
    name = models.CharField(max_length=250, db_index=True)
    number = models.CharField(blank=True, null=True, max_length=50)
    status = models.CharField(
        max_length=20, blank=True, null=True, choices=STATUS_CHOICES)

    account = models.ForeignKey(
        'Account', blank=True, null=True, on_delete=models.SET_NULL
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class ServiceCall(TimeStampedModel):
    description = models.TextField(blank=True, null=True, max_length=2000)
    duration = models.DecimalField(
        blank=True, null=True, decimal_places=4, max_digits=9)
    complete = models.BooleanField(default=False)
    create_date_time = models.DateTimeField(blank=True, null=True)
    start_date_time = models.DateTimeField()
    end_date_time = models.DateTimeField()
    canceled_date_time = models.DateTimeField(blank=True, null=True)
    last_modified_date_time = models.DateTimeField(blank=True, null=True)

    account = models.ForeignKey(
        'Account', blank=True, null=True, on_delete=models.SET_NULL)
    location = models.ForeignKey(
        'AccountPhysicalLocation',
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    status = models.ForeignKey(
        'ServiceCallStatus', on_delete=models.CASCADE)
    creator_resource = models.ForeignKey(
        'Resource',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='created_service_calls'
    )
    canceled_by_resource = models.ForeignKey(
        'Resource',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='cancelled_service_calls'
    )

    tickets = models.ManyToManyField(
        'Ticket', through='ServiceCallTicket',
    )
    tasks = models.ManyToManyField(
        'Task', through='ServiceCallTask',
    )

    AUTOTASK_FIELDS = {
        'description': 'description',
        'duration': 'duration',
        'complete': 'isComplete',
        'create_date_time': 'createDateTime',
        'start_date_time': 'startDateTime',
        'end_date_time': 'endDateTime',
        'canceled_date_time': 'canceledDateTime',
        'last_modified_date_time': 'lastModifiedDateTime',
        'account': 'companyID',
        'location': 'companyLocationID',
        'status': 'status',
        'creator_resource': 'creatorResourceID',
        'canceled_by_resource': 'canceledByResourceID',
    }

    def __str__(self):
        return str(self.id)


class ServiceCallTicket(TimeStampedModel):
    service_call = models.ForeignKey(
        'ServiceCall',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    ticket = models.ForeignKey('Ticket', on_delete=models.CASCADE)
    resources = models.ManyToManyField(
        'Resource', through='ServiceCallTicketResource',
        related_name='resource_service_call_ticket'
    )

    AUTOTASK_FIELDS = {
        'service_call': 'serviceCallID',
        'ticket': 'ticketID',
    }

    def __str__(self):
        return str(self.id)


class ServiceCallTask(TimeStampedModel):
    service_call = models.ForeignKey(
        'ServiceCall',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    resources = models.ManyToManyField(
        'Resource', through='ServiceCallTaskResource',
        related_name='resource_service_call_task'
    )

    AUTOTASK_FIELDS = {
        'service_call': 'serviceCallID',
        'task': 'taskID',
    }

    def __str__(self):
        return str(self.id)


class ServiceCallTicketResource(TimeStampedModel):
    service_call_ticket = models.ForeignKey(
        'ServiceCallTicket', on_delete=models.CASCADE)
    resource = models.ForeignKey('Resource', on_delete=models.CASCADE)

    AUTOTASK_FIELDS = {
        'resource': 'resourceID',
        'service_call_ticket': 'serviceCallTicketID',
    }

    def __str__(self):
        return str(self.id)


class ServiceCallTaskResource(TimeStampedModel):
    service_call_task = models.ForeignKey(
        'ServiceCallTask', on_delete=models.CASCADE)
    resource = models.ForeignKey('Resource', on_delete=models.CASCADE)

    AUTOTASK_FIELDS = {
        'resource': 'resourceID',
        'service_call_task': 'serviceCallTaskID',
    }

    def __str__(self):
        return str(self.id)


class TaskPredecessor(TimeStampedModel):
    lag_days = models.IntegerField(blank=True, null=True)
    predecessor_task = models.ForeignKey('Task', blank=True, null=True,
                                         related_name='predecessor_task_set',
                                         on_delete=models.CASCADE)
    successor_task = models.ForeignKey('Task', blank=True, null=True,
                                       related_name='successor_task_set',
                                       on_delete=models.CASCADE)

    class Meta:
        ordering = ('predecessor_task__title', )

    def __str__(self):
        return str(self.id)


class BaseUDF(TimeStampedModel):
    name = models.CharField(max_length=50, unique=True)
    label = models.CharField(max_length=50, blank=True, null=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    is_picklist = models.BooleanField(default=False)
    picklist = models.JSONField(default=dict)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class TicketUDF(BaseUDF):
    pass


class TaskUDF(BaseUDF):
    pass


class ProjectUDF(BaseUDF):
    pass


class TicketTracker(Ticket):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_ticket'


class StatusTracker(Status):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_status'


class PriorityTracker(Priority):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_priority'


class QueueTracker(Queue):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_queue'


class ProjectStatusTracker(ProjectStatus):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_projectstatus'


class DisplayColorTracker(DisplayColor):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_displaycolor'


class ProjectTypeTracker(ProjectType):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_projecttype'


class ProjectNoteTypeTracker(ProjectNoteType):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_projectnotetype'


class SourceTracker(Source):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_source'


class IssueTypeTracker(IssueType):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_issuetype'


class TicketTypeTracker(TicketType):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_tickettype'


class TaskCategoryTracker(TaskCategory):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_taskcategory'


class SubIssueTypeTracker(SubIssueType):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_subissuetype'


class LicenseTypeTracker(LicenseType):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_licensetype'


class AccountTypeTracker(AccountType):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_accounttype'


class NoteTypeTracker(NoteType):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_notetype'


class TaskTypeLinkTracker(TaskTypeLink):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_tasktypelink'


class UseTypeTracker(UseType):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_usetype'


class BillingCodeTypeTracker(BillingCodeType):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_billingcodetype'


class ServiceCallStatusTracker(ServiceCallStatus):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_servicecallstatus'


class ResourceTracker(Resource):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_resource'


class TicketCategoryTracker(TicketCategory):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_ticketcategory'


class TicketSecondaryResourceTracker(TicketSecondaryResource):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_ticketsecondaryresource'


class TicketNoteTracker(TicketNote):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_ticketnote'


class TaskNoteTracker(TaskNote):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_tasknote'


class ContactTracker(Contact):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_contact'


class AccountTracker(Account):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_account'


class AccountPhysicalLocationTracker(AccountPhysicalLocation):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_accountphysicallocation'


class ProjectTracker(Project):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_project'


class PhaseTracker(Phase):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_phase'


class TaskTracker(Task):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_task'


class TaskSecondaryResourceTracker(TaskSecondaryResource):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_tasksecondaryresource'


class TimeEntryTracker(TimeEntry):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_timeentry'


class BillingCodeTracker(BillingCode):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_billingcode'


class RoleTracker(Role):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_role'


class DepartmentTracker(Department):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_department'


class ResourceRoleDepartmentTracker(ResourceRoleDepartment):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_resourceroledepartment'


class ResourceServiceDeskRoleTracker(ResourceServiceDeskRole):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_resourceservicedeskrole'


class ContractTracker(Contract):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_contract'


class ServiceCallTracker(ServiceCall):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_servicecall'


class ServiceCallTicketTracker(ServiceCallTicket):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_servicecallticket'


class ServiceCallTaskTracker(ServiceCallTask):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_servicecalltask'


class ServiceCallTicketResourceTracker(ServiceCallTicketResource):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_servicecallticketresource'


class ServiceCallTaskResourceTracker(ServiceCallTaskResource):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_servicecalltaskresource'


class TaskPredecessorTracker(TaskPredecessor):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_taskpredecessor'


class TicketUDFTracker(TicketUDF):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_ticketudf'


class TaskUDFTracker(TaskUDF):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_taskudf'


class ProjectUDFTracker(ProjectUDF):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_projectudf'


class TaskTypeTracker(TaskType):
    tracker = FieldTracker()

    class Meta:
        proxy = True
        db_table = 'djautotask_tasktype'
