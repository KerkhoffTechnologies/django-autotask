from django.db import models
from django_extensions.db.models import TimeStampedModel


class Account(TimeStampedModel):
    account_name = models.CharField(blank=True, null=True, max_length=100)
    account_number = models.CharField(blank=True, null=True, max_length=50)
    account_type = models.IntegerField(blank=True, null=True)
    active = models.NullBooleanField(blank=True)
    account_id = models.BigIntegerField(blank=True, null=True)
    last_activity_date = models.DateField(blank=True, null=True)
    phone_number = models.CharField(blank=True, null=True, max_length=250)
    fax_number = models.CharField(blank=True, null=True, max_length=250)
    address_line1 = models.CharField(blank=True, null=True, max_length=250)
    address_line2 = models.CharField(blank=True, null=True, max_length=250)
    city = models.CharField(blank=True, null=True, max_length=250)
    state_identifier = models.CharField(blank=True, null=True, max_length=250)
    zip = models.CharField(blank=True, null=True, max_length=250)
    country = models.CharField(blank=True, null=True, max_length=250)
    territory = models.CharField(blank=True, null=True, max_length=250)
    website = models.CharField(blank=True, null=True, max_length=250)
    market = models.CharField(blank=True, null=True, max_length=250)

    def __str__(self):
        return self.account_name


class Project(TimeStampedModel):
    project_id = models.BigIntegerField(blank=True, null=True)
    actual_billed_hours = models.DecimalField(
        blank=True, null=True, decimal_places=2, max_digits=6)
    actual_hours = models.DecimalField(
        blank=True, null=True, decimal_places=2, max_digits=6)
    completed_date_time = models.DateField(blank=True, null=True)
    create_date_time = models.DateField(blank=True, null=True)
    department = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True, max_length=2000)
    duration = models.IntegerField(blank=True, null=True)
    end_date_time = models.DateField(blank=True, null=True)
    estimated_time = models.DecimalField(
        blank=True, null=True, decimal_places=2, max_digits=6)
    project_name = models.CharField(blank=True, null=True, max_length=100)
    project_number = models.CharField(blank=True, null=True, max_length=50)
    start_date_time = models.DateField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    status_date_time = models.DateField(blank=True, null=True)
    status_detail = models.TextField(blank=True, null=True, max_length=2000)
    project_type = models.IntegerField(blank=True, null=True)

    account_id = models.ForeignKey(
        'Account', blank=True, null=True, on_delete=models.SET_NULL)
    creator_resource_id = models.ForeignKey(
        'Resource', blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class Ticket(TimeStampedModel):
    ticket_id = models.BigIntegerField(blank=True, null=True)
    creator_resource_id = models.IntegerField(blank=True, null=True)
    completed_date = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True, max_length=8000)
    due_date_time = models.DateTimeField(blank=True, null=True)
    estimated_hours = models.DecimalField(
        blank=True, null=True, decimal_places=2, max_digits=6)
    hours_to_be_scheduled = models.DecimalField(
        blank=True, null=True, decimal_places=2, max_digits=6)
    last_activity_date = models.DateTimeField(blank=True, null=True)
    opportunity_id = models.IntegerField(blank=True, null=True)
    priority = models.IntegerField(blank=True, null=True)
    resolution = models.TextField(blank=True, null=True, max_length=32000)
    resolution_plan_due_date = models.DateTimeField(blank=True, null=True)
    resolution_plan_due_date_time = models.DateTimeField(blank=True, null=True)
    resolved_date_time = models.DateTimeField(blank=True, null=True)
    resolved_due_date_time = models.DateTimeField(blank=True, null=True)
    sla_been_met = models.NullBooleanField(blank=True, null=True)
    sla_id = models.IntegerField(blank=True, null=True)
    source = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    ticket_category = models.IntegerField(blank=True, null=True)
    ticket_number = models.CharField(blank=True, null=True, max_length=50)
    ticket_type = models.IntegerField(blank=True, null=True)
    title = models.CharField(blank=True, null=True, max_length=255)

    account_id = models.ForeignKey(
        'Account', blank=True, null=True, related_name='account_tickets',
        on_delete=models.SET_NULL)
    assigned_resource_id = models.ForeignKey(
        'Resource', blank=True, null=True,
        related_name='assigned_resource_tickets',
        on_delete=models.SET_NULL)
    last_activity_resource_id = models.ForeignKey(
        'Resource', blank=True, null=True, on_delete=models.SET_NULL)
    assigned_resource_role_id = models.ForeignKey(
        'ResourceRole', blank=True, null=True, related_name='role_tickets',
        on_delete=models.SET_NULL)
    creator_resource_id = models.ForeignKey(
        'Resource', blank=True, null=True,
        related_name='creator_resource_tickets',
        on_delete=models.SET_NULL)
    project_id = models.ForeignKey(
        'Project', blank=True, null=True,
        related_name='project_tickets',
        on_delete=models.CASCADE)
    # Might need to include, board, priority, status and
    # team as in django-connectwise

    class Meta:
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ('title', )

    def __str__(self):
        return '{}-{}'.format(self.id, self.summary)


class TicketCategory(models.Model):
    pass


class TicketNote(TimeStampedModel):
    ticket_note_id = models.BigIntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True, max_length=3200)
    last_activity_date = models.DateTimeField(blank=True, null=True)
    note_type = models.IntegerField(blank=True, null=True)
    publish = models.IntegerField(blank=True, null=True)
    title = models.CharField(blank=True, null=True, max_length=250)

    creator_resource_id = models.ForeignKey(
        'Resource', blank=True, null=True, on_delete=models.SET_NULL)
    ticket_id = models.ForeignKey(
        'Ticket', on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Notes'

    def __str__(self):
        return 'Ticket {} note: {}'.format(self.ticket,
                                           str(self.last_activity_date))


class TimeEntry(TimeStampedModel):
    time_entry_id = models.BigIntegerField(blank=True, null=True)
    create_date_time = models.DateTimeField(blank=True, null=True)
    date_worked = models.DateTimeField(blank=True, null=True)
    end_date_time = models.DateTimeField(blank=True, null=True)
    hours_to_bill = models.DateTimeField(blank=True, null=True)
    hours_worked = models.DecimalField(
        blank=True, null=True, decimal_places=2, max_digits=6)
    last_modified_date_time = models.DateTimeField(blank=True, null=True)
    last_modified_user_id = models.IntegerField(blank=True, null=True)
    non_billable = models.NullBooleanField(blank=True, null=True)
    show_on_invoice = models.BooleanField(blank=True)
    start_date_time = models.DateTimeField(blank=True, null=True)
    summary_notes = models.TextField(blank=True, null=True, max_length=8000)
    time_entry_type = models.IntegerField(blank=True, null=True)

    ticket_id = models.ForeignKey(
        'Ticket', on_delete=models.CASCADE)
    resource_id = models.ForeignKey(
        'Resource', on_delete=models.CASCADE)
    role_id = models.ForeignKey(
        'Role', on_delete=models.CASCADE)

    def __str__(self):
        return self.summary_notes


class TicketSecondaryResource(TimeStampedModel):
    ticket_secondary_resource_id = models.BigIntegerField(
        blank=True, null=True)
    resource_id = models.ForeignKey(
       'Resource', null=True, on_delete=models.CASCADE)
    role_id = models.ForeignKey(
        'ResourceRole', null=True, on_delete=models.CASCADE)
    ticket_id = models.ForeignKey(
        'Ticket', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.resource_id


class Resource(TimeStampedModel):
    resource_id = models.BigIntegerField(blank=True, null=True)
    active = models.BooleanField(default=False)
    date_format = models.CharField(blank=True, null=True, max_length=20)
    email = models.CharField(blank=True, null=True, max_length=20)
    first_name = models.CharField(blank=True, null=True, max_length=50)
    last_name = models.CharField(blank=True, null=True, max_length=50)
    gender = models.CharField(blank=True, null=True, max_length=1)
    greeting = models.IntegerField(blank=True, null=True)
    hire_date = models.DateTimeField(blank=True, null=True)
    number_format = models.CharField(blank=True, null=True, max_length=20)
    office_phone = models.CharField(blank=True, null=True, max_length=20)
    resource_type = models.CharField(blank=True, null=True, max_length=15)
    time_format = models.CharField(blank=True, null=True, max_length=20)
    title = models.CharField(blank=True, null=True, max_length=50)
    user_name = models.CharField(blank=True, null=True, max_length=32)
    user_type = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return '{} {} {}'.format(self.first_name,
                                 self.last_name, self.user_name)


class ResourceRole(TimeStampedModel):
    resource_role_id = models.BigIntegerField(blank=True, null=True)
    active = models.BooleanField(default=False)
    department_id = models.ForeignKey(
            'Department', null=True, on_delete=models.CASCADE)
    resource_id = models.ForeignKey(
        'Resource', null=True, on_delete=models.CASCADE)
    role_id = models.ForeignKey(
        'Role', null=True, on_delete=models.CASCADE)


class Department(TimeStampedModel):
    department_id = models.BigIntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True, max_length=1000)
    name = models.TextField(blank=True, null=True, max_length=100)
    number = models.TextField(blank=True, null=True, max_length=50)
    primary_location_id = models.DecimalField(
        blank=True, null=True, decimal_places=2, max_digits=6)

    def __str__(self):
        return '{} {}'.format(self.name, self.number)


class Role(TimeStampedModel):
    role_id = models.BigIntegerField(blank=True, null=True)
    active = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True, max_length=200)
    hourly_factor = models.DecimalField(
        blank=True, null=True, decimal_places=2, max_digits=6)
    hourly_rate = models.DecimalField(
        blank=True, null=True, decimal_places=2, max_digits=6)
    is_excluded_from_new_contracts = models.BooleanField(default=False)
    name = models.TextField(blank=True, null=True, max_length=200)
    role_type = models.IntegerField(blank=True, null=True)
    system_role = models.BooleanField(default=False)

    def __str__(self):
        return '{} {}'.format(self.name, self.role_type)


class Opportunity(models.Model):
    # May implement at a later time
    pass
