from django.db import models
from django_extensions.db.models import TimeStampedModel


class SyncJob(models.Model):
    start_time = models.DateTimeField(null=False)
    end_time = models.DateTimeField(blank=True, null=True)
    entity_name = models.CharField(max_length=100)
    added = models.PositiveIntegerField(null=True)
    updated = models.PositiveIntegerField(null=True)
    deleted = models.PositiveIntegerField(null=True)
    success = models.NullBooleanField()
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
        blank=True, null=True, decimal_places=2, max_digits=6)
    last_activity_date = models.DateTimeField(blank=True, null=True)
    title = models.CharField(blank=True, null=True, max_length=255)

    status = models.ForeignKey(
        'TicketStatus', blank=True, null=True, on_delete=models.SET_NULL
    )
    priority = models.ForeignKey(
        'TicketPriority', blank=True, null=True, on_delete=models.SET_NULL
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
    account = models.ForeignKey(
        'Account', blank=True, null=True, on_delete=models.SET_NULL
    )
    project = models.ForeignKey(
        'Project', null=True, on_delete=models.SET_NULL
    )
    category = models.ForeignKey(
        'TicketCategory', null=True, on_delete=models.SET_NULL
    )
    source = models.ForeignKey(
        'Source', null=True, on_delete=models.SET_NULL
    )
    issue_type = models.ForeignKey(
        'IssueType', null=True, on_delete=models.SET_NULL
    )
    sub_issue_type = models.ForeignKey(
        'SubIssueType', null=True, on_delete=models.SET_NULL
    )
    type = models.ForeignKey(
        'TicketType', null=True, on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = 'Ticket'

    def __str__(self):
        return '{}-{}'.format(self.id, self.title)


class Picklist(TimeStampedModel):
    label = models.CharField(blank=True, null=True, max_length=50)
    is_default_value = models.BooleanField(default=False)
    sort_order = models.PositiveSmallIntegerField(blank=True, null=True)
    parent_value = models.CharField(blank=True, null=True, max_length=20)
    is_active = models.BooleanField(default=False)
    is_system = models.BooleanField(default=False)

    class Meta:
        abstract = True

    def __str__(self):
        return '{}-{}'.format(self.id, self.label)


class TicketStatus(Picklist):
    pass

    class Meta:
        verbose_name_plural = 'Ticket statuses'


class TicketPriority(Picklist):
    pass

    class Meta:
        verbose_name_plural = 'Ticket priorities'


class Queue(Picklist):
    pass

    class Meta:
        verbose_name_plural = 'Queues'


class ProjectStatus(Picklist):
    pass

    class Meta:
        verbose_name_plural = 'Project statuses'


class DisplayColor(Picklist):
    pass

    class Meta:
        verbose_name_plural = 'Display colors'


class ProjectType(Picklist):
    pass


class Source(Picklist):
    pass


class IssueType(Picklist):
    pass


class TicketType(Picklist):
    pass


class SubIssueType(Picklist):
    pass


class Resource(TimeStampedModel):
    user_name = models.CharField(max_length=32)
    email = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ('first_name', 'last_name')

    def __str__(self):
        return '{} {}'.format(self.first_name, self.last_name)


class TicketCategory(TimeStampedModel):
    name = models.CharField(max_length=30)
    active = models.BooleanField(default=False)
    display_color = models.ForeignKey(
        'DisplayColor', null=True, on_delete=models.SET_NULL
    )

    class Meta:
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

    def __str__(self):
        return '{} {}'.format(self.resource, self.ticket)


class Account(TimeStampedModel):
    name = models.CharField(max_length=100)
    number = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    last_activity_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name


class Project(TimeStampedModel):
    name = models.CharField(max_length=100)
    number = models.CharField(null=True, max_length=50)
    description = models.CharField(max_length=2000)
    actual_hours = models.DecimalField(
        null=True, decimal_places=2, max_digits=9)
    completed_date = models.DateField(null=True)
    completed_percentage = models.PositiveSmallIntegerField(default=0)
    duration = models.PositiveSmallIntegerField(default=0)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    estimated_time = models.DecimalField(
        null=True, decimal_places=2, max_digits=9
    )
    last_activity_date_time = models.DateTimeField(null=True)

    project_lead_resource = models.ForeignKey(
        'Resource', null=True, on_delete=models.SET_NULL
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

    def __str__(self):
        return self.name
