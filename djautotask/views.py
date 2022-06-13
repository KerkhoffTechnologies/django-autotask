import json
import logging

from braces import views
from django import forms
from django.views.generic import View
from django.http import HttpResponse, HttpResponseBadRequest

from djautotask import sync, models
from djautotask.api import AutotaskAPIError

logger = logging.getLogger(__name__)


class CallBackView(views.CsrfExemptMixin,
                   views.JsonRequestResponseMixin, View):

    CALLBACK_TYPES = {
        'ticket': (
            sync.TicketSynchronizer, models.Ticket
        ),
    }

    def post(self, request, *args, **kwargs):
        """
        Add, OR update entity by fetching it from AT. The only real useful
        information we get from the callback is the id of the ticket. Right
        now Autotask only supports callbacks for Tickets, but it looks like
        support could be added for any other entity at some point. We don't
        receive the ticket object, just its ID, current status, the datetime
        it was originally created, and the user domain it came from, which
        is a lot of useless info. Use the ID to sync the ticket.

        Note that we don't get a callback when a ticket is deleted, so it will
        only get scooped up next sync.
        """

        form = CallBackForm(request.POST)

        if not form.is_valid():
            fields = ', '.join(form.errors.keys())
            msg = 'Received callback with missing parameters: {}.'.format(
                fields)
            logger.warning(msg)
            return HttpResponseBadRequest(json.dumps(form.errors))

        entity_id = form.cleaned_data['id']
        synchronizer = sync.TicketSynchronizer

        try:
            self.handle(entity_id, synchronizer)
        except AutotaskAPIError as e:
            logger.error(
                'API call failed in Ticket ID {} callback: '
                '{}'.format(entity_id, e)
            )

        return HttpResponse(status=204)

    def handle(self, entity_id, synchronizer):
        """
        Do the interesting stuff here, so that it can be overridden in
        a child class if needed.
        """
        synchronizer().fetch_sync_by_id(entity_id)


class CallBackForm(forms.Form):
    id = forms.IntegerField()
