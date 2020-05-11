from collections import OrderedDict
from atws.wrapper import AutotaskProcessException, AutotaskAPIException
from xml.sax._exceptions import SAXParseException

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext_lazy as _
from djautotask import sync, api

OPTION_NAME = 'autotask_object'
ERROR_MESSAGE_TEMPLATE = 'Failed to sync {}. Autotask API returned an ' \
                             'error(s): {}.'


class Command(BaseCommand):
    help = str(_('Synchronize the specified object with the Autotask API'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # This can be replaced with a single instantiation of an OrderedDict
        # using kwargs in Python 3.6. But we need Python 3.5 compatibility for
        # now.
        # See https://www.python.org/dev/peps/pep-0468/.
        synchronizers = (
            ('status', sync.StatusSynchronizer, _('Status')),
            ('license_type', sync.LicenseTypeSynchronizer, _('License Type')),
            ('resource', sync.ResourceSynchronizer, _('Resource')),
            ('ticket_secondary_resource',
             sync.TicketSecondaryResourceSynchronizer,
             _('Ticket Secondary Resource')),
            ('priority', sync.PrioritySynchronizer, _('Priority')),
            ('queue', sync.QueueSynchronizer, _('Queue')),
            ('account_type', sync.AccountTypeSynchronizer, _('Account Type')),
            ('account', sync.AccountSynchronizer, _('Account')),
            (
                'account_physical_location',
                sync.AccountPhysicalLocationSynchronizer,
                _('Account Physical Location')
            ),
            ('contract', sync.ContractSynchronizer, _('Contract')),
            ('project_status',
             sync.ProjectStatusSynchronizer, _('Project Status')),
            ('project_type', sync.ProjectTypeSynchronizer, _('Project Type')),
            ('project', sync.ProjectSynchronizer, _('Project')),
            ('phase', sync.PhaseSynchronizer, _('Phase')),
            ('task_secondary_resource',
             sync.TaskSecondaryResourceSynchronizer,
             _('Task Secondary Resource')),
            ('task', sync.TaskSynchronizer, _('Task')),
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
            ('note_type', sync.NoteTypeSynchronizer, _('Note Type')),
            ('ticket_note', sync.TicketNoteSynchronizer, _('Ticket Note')),
            ('task_note', sync.TaskNoteSynchronizer, _('Task Note')),
            ('task_type_link', sync.TaskTypeLinkSynchronizer,
             _('Task Type Link')),
            ('use_type', sync.UseTypeSynchronizer, _('Use Type')),
            ('allocation_code', sync.AllocationCodeSynchronizer,
             _('Allocation Code')),
            ('role', sync.RoleSynchronizer, _('Role')),
            ('department', sync.DepartmentSynchronizer, _('Department')),
            ('time_entry', sync.TimeEntrySynchronizer, _('Time Entry')),
            (
                'resource_role_department',
                sync.ResourceRoleDepartmentSynchronizer,
                _('Resource Role Department')
            ),
            (
                'resource_service_desk_role',
                sync.ResourceServiceDeskRoleSynchronizer,
                _('Resource Service Desk Role')
            ),
            (
                'service_call_status',
                sync.ServiceCallStatusSynchronizer,
                _('Service Call Status')
            ),
            (
                'service_call',
                sync.ServiceCallSynchronizer,
                _('Service Call')
            ),
            (
                'service_call_ticket',
                sync.ServiceCallTicketSynchronizer,
                _('Service Call Ticket')
            ),
            (
                'service_call_task',
                sync.ServiceCallTaskSynchronizer,
                _('Service Call Task')
            ),
            (
                'service_call_ticket_resource',
                sync.ServiceCallTicketResourceSynchronizer,
                _('Service Call Ticket Resource')
            ),
            (
                'service_call_task_resource',
                sync.ServiceCallTaskResourceSynchronizer,
                _('Service Call Task Resource')
            ),
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

        for sync_class, obj_name in sync_classes:
            error_msg = None
            try:
                self.sync_by_class(sync_class, obj_name,
                                   full_option=full_option)

            except AutotaskProcessException as e:
                error_msg = ERROR_MESSAGE_TEMPLATE.format(
                    obj_name, api.parse_autotaskprocessexception(e))

            except AutotaskAPIException as e:
                error_msg = ERROR_MESSAGE_TEMPLATE.format(
                    obj_name, api.parse_autotaskapiexception(e))

            except SAXParseException as e:
                error_msg = 'Failed to connect to Autotask API. ' \
                      'The error was: {}'.format(e)

            finally:
                if error_msg:
                    self.stderr.write(error_msg)
                    error_messages += '{}\n'.format(error_msg)
                    failed_classes += 1

        if failed_classes > 0:
            msg = '{} class{} failed to sync.\n'.format(
                failed_classes,
                '' if failed_classes == 1 else 'es',
            )
            msg += 'Errors:\n'
            msg += error_messages
            raise CommandError(msg)
