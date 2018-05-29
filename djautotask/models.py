import re
import logging
import urllib

#from easy_thumbnails.fields import ThumbnailerImageField
from model_utils import Choices

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
#from django_extensions.db.models import TimeStampedModel

#from . import api

logger = logging.getLogger(__name__)


PRIORITY_RE = re.compile('^Priority ([\d]+)')

class Account(models.Model):

    account_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)

    def __str__(self):
        return self.account_name + self.account_number


class Project(models.Model):
    pass


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
