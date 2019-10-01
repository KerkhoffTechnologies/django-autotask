from collections import OrderedDict
from atws.wrapper import AutotaskAPIException
from xml.sax._exceptions import SAXParseException

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext_lazy as _
from djautotask import sync

OPTION_NAME = 'autotask_object'


class Command(BaseCommand):
    help = str(_('Synchronize the specified object with the Autotask API'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # This can be replaced with a single instantiation of an OrderedDict
        # using kwargs in Python 3.6. But we need Python 3.5 compatibility for
        # now.
        # See https://www.python.org/dev/peps/pep-0468/.
        synchronizers = (
            ('ticket_status',
             sync.TicketStatusSynchronizer, _('Ticket Status')),
            ('resource', sync.ResourceSynchronizer, _('Resource')),
            ('ticket_secondary_resource',
             sync.TicketSecondaryResourceSynchronizer,
             _('Ticket Secondary Resource')),
            ('ticket_priority',
             sync.TicketPrioritySynchronizer, _('Ticket Priority')),
            ('queue', sync.QueueSynchronizer, _('Queue')),
            ('account', sync.AccountSynchronizer, _('Account')),
            ('project_status',
             sync.ProjectStatusSynchronizer, _('Project Status')),
            ('project_type', sync.ProjectTypeSynchronizer, _('Project Type')),
            ('project', sync.ProjectSynchronizer, _('Project')),
            ('display_color', sync.DisplayColorSynchronizer,
             _('Display Color')),
            ('ticket_category', sync.TicketCategorySynchronizer,
             _('Ticket Category')),
            ('source', sync.SourceSynchronizer, _('Source')),
            ('issue_type', sync.IssueTypeSynchronizer, _('Issue Type')),
            ('ticket_type', sync.TicketTypeSynchronizer, _('Ticket Type')),
            ('sub_issue_type', sync.SubIssueTypeSynchronizer,
             _('Sub Issue Type')),
            ('ticket', sync.TicketSynchronizer, _('Ticket')),
        )
        self.synchronizer_map = OrderedDict()
        for name, synchronizer, obj_name in synchronizers:
            self.synchronizer_map[name] = (synchronizer, obj_name)

    def add_arguments(self, parser):
        parser.add_argument(OPTION_NAME, nargs='?', type=str)
        parser.add_argument('--full',
                            action='store_true',
                            dest='full',
                            default=False)

    def sync_by_class(self, sync_class, obj_name, full_option=False):
        synchronizer = sync_class(full=full_option)

        created_count, updated_count, deleted_count = synchronizer.sync()

        msg = _('{} Sync Summary - Created: {}, Updated: {}')
        fmt_msg = msg.format(obj_name, created_count, updated_count)

        if full_option:
            msg = _('{} Sync Summary - Created: {}, Updated: {}, Deleted: {}')
            fmt_msg = msg.format(obj_name, created_count, updated_count,
                                 deleted_count)

        self.stdout.write(fmt_msg)

    def handle(self, *args, **options):
        sync_classes = []
        autotask_object_arg = options[OPTION_NAME]
        full_option = options.get('full', False)

        if autotask_object_arg:
            object_arg = autotask_object_arg
            sync_tuple = self.synchronizer_map.get(object_arg)

            if sync_tuple:
                sync_classes.append(sync_tuple)
            else:
                msg = _('Invalid AT object {}, '
                        'choose one of the following: \n{}')
                options_txt = ', '.join(self.synchronizer_map.keys())
                msg = msg.format(sync_tuple, options_txt)
                raise CommandError(msg)
        else:
            sync_classes = self.synchronizer_map.values()

        failed_classes = 0
        error_messages = ''

        num_synchronizers = len(self.synchronizer_map)
        has_ticket_sync = 'ticket' in self.synchronizer_map
        if full_option and num_synchronizers and has_ticket_sync:
            sync_classes = list(sync_classes)
            sync_classes.reverse()
            # need to move ticket synchronizer to the tail of the list
            sync_classes.append(sync_classes.pop(0))

        for sync_class, obj_name in sync_classes:
            try:
                self.sync_by_class(sync_class, obj_name,
                                   full_option=full_option)

            except AutotaskAPIException as e:
                msg = 'Failed to sync {}. Autotask API returned an error: ' \
                      '{}.'.format(obj_name, ' '.join(e.response.errors))

                error_messages += '{}\n'.format(msg)
                failed_classes += 1

            except SAXParseException as e:
                msg = 'Failed to connect to Autotask API. ' \
                      'The error was: {}'.format(e)

                error_messages += '{}\n'.format(msg)
                failed_classes += 1

        if failed_classes > 0:
            msg = '{} class{} failed to sync.\n'.format(
                failed_classes,
                '' if failed_classes == 1 else 'es',
            )
            msg += 'Errors:\n'
            msg += error_messages
            raise CommandError(msg)
