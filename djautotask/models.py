import re
import logging
import urllib

from easy_thumbnails.fields import ThumbnailerImageField
from model_utils import Choices

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.models import TimeStampedModel


logger = logging.getLogger(__name__)


PRIORITY_RE = re.compile('^Priority ([\d]+)')

class Account(models.Model):

    name = models.CharField(blank=True, null=True, max_length=100)
    number = models.CharField(blank=True, null=True, max_length=50)
    account_id = models.IntegerField(blank=True, null=True)
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
        return self.name


class Project(models.Model):
    
    name = models.CharField(blank=True, null=True, max_length=200)
    last_activity_date = models.DateField(blank=True, null=True)
    actual_hours = models.DecimalField(
	blank=True, null=True, decimal_places=2, max_digits=6) 
    budget_hours = models.DecimalField(
	blank=True, null=True, decimal_places=2, max_digits=6)
    scheduled_hours = models.DecimalField(
	blank=True, null=True, decimal_places=2, max_digits=6)
    
    account_id = models.ForeignKey(
        'Account', 
        blank=True, 
        null=True, 
        on_delete=models.SET_NULL
    )

   #status

    def __str__(self):
        return self.name


class Ticket(models.Model):
    

    RECORD_TYPES = (
        ('ServiceTicket', "Service Ticket"),
        ('ProjectTicket', "Project Ticket"),
        ('ProjectIssue', "Project Issue"),
    )
    actual_hours = models.DecimalField
	blank=True, null=True, decimal_places=2, max_digits=6)
    agreement_id = models.IntegerField(blank=True, null=True)
    approved = models.NullBooleanField(blank=True, null=True)
    budget_hours = models.DecimalField(
        blank=True, null=True, decimal_places=2, max_digits=6)
    closed_by = models.CharField(blank=True, null=True, max_length=250)
    closed_date_utc = models.DateTimeField(blank=True, null=True)
    closed_flag = models.NullBooleanField(blank=True, null=True)
    customer_updated = models.BooleanField(default=False)
    date_resolved_utc = models.DateTimeField(blank=True, null=True)
    date_resplan_utc = models.DateTimeField(blank=True, null=True)
    date_responded_utc = models.DateTimeField(blank=True, null=True)
    entered_date_utc = models.DateTimeField(blank=True, null=True)
    has_child_ticket = models.NullBooleanField()
    impact = models.CharField(blank=True, null=True, max_length=250)
    is_in_sla = models.NullBooleanField(blank=True, null=True)
    last_updated_utc = models.DateTimeField(blank=True, null=True)
    parent_ticket_id = models.IntegerField(blank=True, null=True)
    record_type = models.CharField(blank=True, null=True,
                                   max_length=250, choices=RECORD_TYPES,
                                   db_index=True)
    required_date_utc = models.DateTimeField(blank=True, null=True)
    respond_mins = models.IntegerField(blank=True, null=True)
    resolve_mins = models.IntegerField(blank=True, null=True)
    resources = models.CharField(blank=True, null=True, max_length=250)
    res_plan_mins = models.IntegerField(blank=True, null=True)
    severity = models.CharField(blank=True, null=True, max_length=250)
    site_name = models.CharField(blank=True, null=True, max_length=250)
    source = models.CharField(blank=True, null=True, max_length=250)
    sub_type = models.CharField(blank=True, null=True, max_length=250)
    sub_type_item = models.CharField(blank=True, null=True, max_length=250)
    summary = models.CharField(blank=True, null=True, max_length=250)
    updated_by = models.CharField(blank=True, null=True, max_length=250)

class TicketCategory(models.Model):
    pass


class TicketNote(models.Model):
    pass


class TicketSecondaryResource(models.Model):
    pass


class Resource(models.Model):
    pass


class Opportunity(models.Model):
    # May implement at a later time
    pass
