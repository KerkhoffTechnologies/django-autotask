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
    assigned_resource = models.ForeignKey(
        'Resource', blank=True, null=True, on_delete=models.SET_NULL
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


class TicketStatus(Picklist):
    pass

    class Meta:
        verbose_name = 'Ticket status'
        verbose_name_plural = 'Ticket statuses'

    def __str__(self):
        return '{}-{}'.format(self.id, self.label)


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
