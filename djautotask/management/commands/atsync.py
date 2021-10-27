from collections import OrderedDict

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext_lazy as _
from djautotask import sync_rest as syncrest
from djautotask import api_rest as apirest

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
            ('status', syncrest.StatusSynchronizer, _('Status')),
            (
                'license_type',
                syncrest.LicenseTypeSynchronizer,
                _('License Type')
            ),
            ('resource', syncrest.ResourceSynchronizer, _('Resource')),
            ('ticket_secondary_resource',
             syncrest.TicketSecondaryResourceSynchronizer,
             _('Ticket Secondary Resource')),
            ('priority', syncrest.PrioritySynchronizer, _('Priority')),
            ('queue', syncrest.QueueSynchronizer, _('Queue')),
            (
                'account_type',
                syncrest.AccountTypeSynchronizer,
                _('Account Type')
            ),
            ('account', syncrest.AccountSynchronizer, _('Account')),
            (
                'account_physical_location',
                syncrest.AccountPhysicalLocationSynchronizer,
                _('Account Physical Location')
            ),
            ('contract', syncrest.ContractSynchronizer, _('Contract')),
            ('project_status',
             syncrest.ProjectStatusSynchronizer, _('Project Status')),
            ('project_type',
             syncrest.ProjectTypeSynchronizer, _('Project Type')),
            ('project', syncrest.ProjectSynchronizer, _('Project')),
            ('phase', syncrest.PhaseSynchronizer, _('Phase')),
            ('display_color', syncrest.DisplayColorSynchronizer,
             _('Display Color')),
            ('ticket_category', syncrest.TicketCategorySynchronizer,
             _('Ticket Category')),
            ('source', syncrest.SourceSynchronizer, _('Source')),
            ('issue_type', syncrest.IssueTypeSynchronizer, _('Issue Type')),
            ('ticket_type', syncrest.TicketTypeSynchronizer, _('Ticket Type')),
            ('sub_issue_type', syncrest.SubIssueTypeSynchronizer,
             _('Sub Issue Type')),
            ('ticket', syncrest.TicketSynchronizer, _('Ticket')),
            ('note_type', syncrest.NoteTypeSynchronizer, _('Note Type')),
            ('ticket_note', syncrest.TicketNoteSynchronizer, _('Ticket Note')),
            ('use_type', syncrest.UseTypeSynchronizer, _('Use Type')),
            ('allocation_code', syncrest.AllocationCodeSynchronizer,
             _('Allocation Code')),
            ('role', syncrest.RoleSynchronizer, _('Role')),
            ('department', syncrest.DepartmentSynchronizer, _('Department')),
            ('time_entry', syncrest.TimeEntrySynchronizer, _('Time Entry')),
            ('task', syncrest.TaskSynchronizer, _('Task')),
            ('task_note', syncrest.TaskNoteSynchronizer, _('Task Note')),
            ('task_type_link', syncrest.TaskTypeLinkSynchronizer,
             _('Task Type Link')),
            ('task_secondary_resource',
             syncrest.TaskSecondaryResourceSynchronizer,
             _('Task Secondary Resource')),
            (
                'resource_role_department',
                syncrest.ResourceRoleDepartmentSynchronizer,
                _('Resource Role Department')
            ),
            (
                'resource_service_desk_role',
                syncrest.ResourceServiceDeskRoleSynchronizer,
                _('Resource Service Desk Role')
            ),
            (
                'service_call_status',
                syncrest.ServiceCallStatusSynchronizer,
                _('Service Call Status')
            ),
            (
                'service_call',
                syncrest.ServiceCallSynchronizer,
                _('Service Call')
            ),
            (
                'service_call_ticket',
                syncrest.ServiceCallTicketSynchronizer,
                _('Service Call Ticket')
            ),
            (
                'service_call_task',
                syncrest.ServiceCallTaskSynchronizer,
                _('Service Call Task')
            ),
            (
                'service_call_ticket_resource',
                syncrest.ServiceCallTicketResourceSynchronizer,
                _('Service Call Ticket Resource')
            ),
            (
                'service_call_task_resource',
                syncrest.ServiceCallTaskResourceSynchronizer,
                _('Service Call Task Resource')
            ),
            ('task_predecessor', syncrest.TaskPredecessorSynchronizer,
             _('Task Predecessor')),
            ('contact', syncrest.ContactSynchronizer, _('Contact')),
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

        created_count, updated_count, skipped_count, deleted_count = \
            synchronizer.sync()

        msg = _('{} Sync Summary - Created: {}, Updated: {}, Skipped: {}')
        fmt_msg = msg.format(obj_name, created_count, updated_count,
                             skipped_count)

        if full_option:
            msg = _('{} Sync Summary - Created: {}, Updated: {}, Skipped: {}, '
                    'Deleted: {}')
            fmt_msg = msg.format(obj_name, created_count, updated_count,
                                 skipped_count, deleted_count)

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

            except apirest.AutotaskAPIError as e:
                error_msg = ERROR_MESSAGE_TEMPLATE.format(obj_name, e)

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
