from django.db import models
from django_extensions.db.models import TimeStampedModel


class Account(TimeStampedModel):
    account_name = models.CharField(null=False, max_length=100)
    account_number = models.CharField(blank=True, null=True, max_length=50)
    active = models.BooleanField(default=False)
    last_activity_date = models.DateField(blank=True, null=True)
    web_address = models.CharField(blank=True, null=True, max_length=250)

    def __str__(self):
        return self.account_name


class Project(TimeStampedModel):
    actual_billed_hours = models.DecimalField(
        blank=True, null=True, decimal_places=2, max_digits=6)
    actual_hours = models.DecimalField(
        blank=True, null=True, decimal_places=2, max_digits=6)
    completed_date_time = models.DateField(blank=True, null=True)
    create_date_time = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True, max_length=2000)
    duration = models.IntegerField(blank=True, null=True)
    end_date_time = models.DateField(null=False)
    estimated_time = models.DecimalField(
        blank=True, null=True, decimal_places=2, max_digits=6)
    project_name = models.CharField(null=False, max_length=100)
    project_number = models.CharField(blank=True, null=True, max_length=50)
    start_date_time = models.DateField(null=False)
    # Uses picklist, how to implement?
    status = models.IntegerField(blank=True, null=True)

    account = models.ForeignKey(
        'Account', null=False, on_delete=models.CASCADE)
    creator_resource = models.ForeignKey(
        'Resource', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.project_name


class Ticket(TimeStampedModel):
    completed_date = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True, max_length=8000)
    due_date_time = models.DateTimeField(null=False)
    estimated_hours = models.DecimalField(
        blank=True, null=True, decimal_places=2, max_digits=6)
    hours_to_be_scheduled = models.DecimalField(
        blank=True, null=True, decimal_places=2, max_digits=6)
    # picklist    issue_type = models.IntegerField(null=True)
    last_activity_date = models.DateTimeField(blank=True, null=True)
    opportunity_id = models.IntegerField(blank=True, null=True)
    # picklist    priority = models.IntegerField(blank=True, null=True)
    resolution_plan_due_date = models.DateTimeField(blank=True, null=True)
    resolution_plan_due_date_time = models.DateTimeField(blank=True, null=True)
    resolved_date_time = models.DateTimeField(blank=True, null=True)
    resolved_due_date_time = models.DateTimeField(blank=True, null=True)
    sla_been_met = models.NullBooleanField(blank=True, null=True)
    sla_id = models.IntegerField(blank=True, null=True)
    source = models.IntegerField(blank=True, null=True)
    # picklist    status = models.IntegerField(blank=True, null=True)
    # TicketCategory that is a field of Ticket, not the entity.
    # They are seemingly unrelated
    ticket_category = models.IntegerField(blank=True, null=True)
    ticket_number = models.CharField(blank=True, null=True, max_length=50)
    ticket_type = models.IntegerField(blank=True, null=True)
    title = models.CharField(blank=True, null=True, max_length=255)

    account = models.ForeignKey(
        'Account', null=True, related_name='account_tickets',
        on_delete=models.SET_NULL)
    assigned_resource = models.ForeignKey(
        'Resource', blank=True, null=True,
        related_name='assigned_resource_tickets',
        on_delete=models.SET_NULL)
    last_activity_resource = models.ForeignKey(
        'Resource', blank=True, null=True, on_delete=models.SET_NULL)
    creator_resource = models.ForeignKey(
        'Resource', blank=True, null=True,
        related_name='creator_resource_tickets',
        on_delete=models.SET_NULL)
    project = models.ForeignKey(
        'Project', blank=True, null=True,
        related_name='project_tickets',
        on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ('title', )

    def __str__(self):
        return '{}-{}'.format(self.id, self.title)


class TicketCategory(TimeStampedModel):
    active = models.BooleanField(default=False)
    display_color_rgb = models.IntegerField()
    global_default = models.BooleanField(default=False)
    ticket_category_name = models.CharField(max_length=30)
    nickname = models.CharField(max_length=3)

    def __str__(self):
        return self.ticket_category_name


class TicketNote(TimeStampedModel):
    description = models.TextField(null=False, max_length=3200)
    last_activity_date = models.DateTimeField(blank=True, null=True)
    # picklist    note_type = models.IntegerField(null=False)
    # picklist    publish = models.IntegerField(null=False)
    title = models.CharField(null=False, max_length=250)

    creator_resource = models.ForeignKey(
        'Resource', blank=True, null=True, on_delete=models.SET_NULL)
    ticket = models.ForeignKey(
        'Ticket', null=False, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Notes'

    def __str__(self):
        return '{} {}'.format(self.title,
                              str(self.last_activity_date))


class TimeEntry(TimeStampedModel):
    create_date_time = models.DateTimeField(blank=True, null=True)
    date_worked = models.DateTimeField(null=False)
    end_date_time = models.DateTimeField(blank=True, null=True)
    hours_to_bill = models.DecimalField(
        blank=True, null=True, decimal_places=2, max_digits=6)
    hours_worked = models.DecimalField(
        blank=True, null=True, decimal_places=2, max_digits=6)
    last_modified_date_time = models.DateTimeField(blank=True, null=True)
    last_modified_user_id = models.IntegerField(blank=True, null=True)
    non_billable = models.BooleanField(default=False)
    start_date_time = models.DateTimeField(blank=True, null=True)
    summary_notes = models.TextField(blank=True, null=True, max_length=8000)
    # picklist time_entry_type = models.IntegerField(blank=True, null=False)

    ticket = models.ForeignKey(
        'Ticket', null=False, on_delete=models.CASCADE)
    resource = models.ForeignKey(
        'Resource', null=False, on_delete=models.CASCADE)

    def __str__(self):
        return self.summary_notes


# Field on ticket should be through secondary resource. many to many
class TicketSecondaryResource(TimeStampedModel):
    resource = models.ForeignKey(
       'Resource', null=True, on_delete=models.CASCADE)
    ticket = models.ForeignKey(
        'Ticket', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.resource


class Resource(TimeStampedModel):
    active = models.BooleanField(null=False, default=False)
    email = models.CharField(null=False, max_length=50)
    first_name = models.CharField(null=False, max_length=50)
    last_name = models.CharField(null=False, max_length=50)
    title = models.CharField(blank=True, null=True, max_length=50)
    user_name = models.CharField(null=False, max_length=32)

    def __str__(self):
        return '{} {} {}'.format(self.user_name)


class Department(TimeStampedModel):
    description = models.TextField(blank=True, null=True, max_length=1000)
    name = models.TextField(null=False, max_length=100)
    number = models.CharField(blank=True, null=True, max_length=50)

    def __str__(self):
        return '{} {}'.format(self.name, self.number)


class Opportunity(models.Model):
    # May implement at a later time
    pass
