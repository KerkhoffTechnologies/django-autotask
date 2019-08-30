from suds.client import Client
from atws.wrapper import QueryCursor
import urllib
import os


def generate_ticket_object():

    path = os.path.abspath("djautotask/tests/atws.wsdl")
    url = urllib.parse.urljoin('file:', urllib.request.pathname2url(path))
    client = Client(url)

    # Create suds test ticket object
    ticket_object = client.factory.create('Ticket')
    ticket_object.id = 7703
    ticket_object.Title = 'Customer defect with provisioning'
    ticket_object.CompletedDate = '2019-08-29 19:01:41.573000+01:00'
    ticket_object.CreateDate = '2012-06-18 13:38:30.940000+01:00'
    ticket_object.Description = \
        'Review with customer how they can utilize new features.'
    ticket_object.DueDateTime = '2012-06-18 13:38:30.940000+01:00'
    ticket_object.EstimatedHours = 3.0
    ticket_object.LastActivityDate = '2019-08-29 00:16:31.970000+01:00'
    ticket_object.TicketNumber = 'T20120529.0001'

    return QueryCursor(mock_query_generator([ticket_object]))


def mock_query_generator(suds_objects):
    for obj in suds_objects:
        yield obj
