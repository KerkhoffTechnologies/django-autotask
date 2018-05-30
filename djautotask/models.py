import re
import logging

from django.db import models


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
