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
    account_id = models.IntegerField(blank=True, null=True)
    last_activity_date = models.DateField(blank=True, null=True)
    actual_hours = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=6) 
    budget_hours = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=6)
    scheduled_hours = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=6)

    def __str__(self):
        return self.name


class Ticket(models.Model):
    pass


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
