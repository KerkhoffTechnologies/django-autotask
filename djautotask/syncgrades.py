"""
SyncGrade and SyncGrades are a copy of djpsa.sync.grades. They don't
need to be migrated when AutotaskSyncGrades is migrated.
"""
class SyncGrade:
    description = ""
    synchronizers = []
    schedule = ""  # For app to describe the frequency of use. (ie "Every 5 minutes.")

    def __init__(self, description=None, synchronizers=None):
        self.description = description
        self.synchronizers = synchronizers if synchronizers is not None else []


class SyncGrades:
    """
    Define grades of synchronizers.

    The result of operational+configuration+slow grades+ludicrous slow
    should be all the synchronizers.
    """
    def __init__(self, *args, **kwargs):
        self.filter_cb = kwargs.pop('filter_cb', None)
        self.grades = {
            'partial': SyncGrade(
                """Resources that are useful to keep up-to-date at high 
                   frequency and can be retrieved by limiting to those which have changed recently.""",
                []
            ),
            # Synchronizers for resources that change throughout a typical day. For example,
            # tickets, service calls, notes, etc.
            # Exclude resources that can potentially take a very long time to sync.
            'operational': SyncGrade(
                """Resources that change throughout a day.""",
                []
            ),
            # Synchronizers for resources that change infrequently- such as on a weekly or
            # monthly basis. For example, ticket types, statuses, priorities, etc.
            'configuration': SyncGrade(
                """Resources that change infrequently.""",
                []
            ),
            # Synchronizers for resources that can potentially take a very long
            # time to sync. For example, notes, time entries, etc.
            'slow': SyncGrade(
                """Resources that can take a long time to retrieve.""",
                []
            ),
            # Synchronizers for resources that can take an unbelievable amount of time to sync,
            # so much it makes you cry.
            'ludicrous_slow': SyncGrade(
                """Resources that can take an unbelievable amount of time to retrieve.""",
                []
            ),
        }

    def get_grade(self, grade_key):
        grade = self.grades.get(grade_key)
        if grade and self.filter_cb:
            grade = self.filter_cb(grade)
        return grade

from djautotask import sync


class AutotaskSyncGrades(SyncGrades):
    def __init__(self, *args, **kwargs):
        super(AutotaskSyncGrades, self).__init__(*args, **kwargs)
        self.grades['partial'].synchronizers = [
            sync.ResourceSynchronizer,
            sync.AccountSynchronizer,
            sync.ContactSynchronizer,
            sync.ContractSynchronizer,
            sync.ServiceCallSynchronizer,
            sync.TicketSynchronizer,
            sync.ServiceCallTicketSynchronizer,
            sync.ServiceCallTicketResourceSynchronizer,
            sync.TicketSecondaryResourceSynchronizer,
            sync.TaskSynchronizer,
            sync.ServiceCallTaskSynchronizer,
            sync.ServiceCallTaskResourceSynchronizer,
            sync.TaskSecondaryResourceSynchronizer,
            sync.ProjectSynchronizer,
            sync.TicketNoteSynchronizer,
            sync.TaskNoteSynchronizer,
            sync.TaskPredecessorSynchronizer,
        ]
        self.grades['operational'].synchronizers = [
            sync.ResourceSynchronizer,
            sync.AccountSynchronizer,
            sync.ProjectUDFSynchronizer,
            sync.ProjectSynchronizer,
            sync.PhaseSynchronizer,
            sync.TicketUDFSynchronizer,
            sync.TicketSynchronizer,
            sync.TicketSecondaryResourceSynchronizer,
            sync.TaskUDFSynchronizer,
            sync.TaskSynchronizer,
            sync.TaskSecondaryResourceSynchronizer,
        ]
        self.grades['configuration'].synchronizers = [
            sync.IssueTypeSynchronizer,
            sync.StatusSynchronizer,
            sync.PrioritySynchronizer,
            sync.QueueSynchronizer,
            sync.DisplayColorSynchronizer,
            sync.SourceSynchronizer,
            sync.LicenseTypeSynchronizer,
            sync.UseTypeSynchronizer,
            sync.RoleSynchronizer,
            sync.TaskCategorySynchronizer,
            sync.TaskTypeSynchronizer,
            sync.TaskTypeLinkSynchronizer,
            sync.DepartmentSynchronizer,
            sync.AccountTypeSynchronizer,
            sync.SubIssueTypeSynchronizer,
            sync.BillingCodeTypeSynchronizer,
            sync.BillingCodeSynchronizer,
            sync.ContractSynchronizer,
            sync.ContractExclusionSetSynchronizer,
            sync.ContractExcludedWorkTypeSynchronizer,
            sync.ContractExcludedRoleSynchronizer,
            sync.ContactSynchronizer,
            sync.AccountPhysicalLocationSynchronizer,
            sync.ServiceCallStatusSynchronizer,
            sync.ServiceCallSynchronizer,
            sync.NoteTypeSynchronizer,
            sync.ProjectStatusSynchronizer,
            sync.ProjectTypeSynchronizer,
            sync.ProjectNoteTypeSynchronizer,
            sync.TicketCategorySynchronizer,
            sync.TicketTypeSynchronizer,
            sync.TicketNoteSynchronizer,
            sync.ServiceCallTicketSynchronizer,
            sync.ServiceCallTicketResourceSynchronizer,
            sync.ResourceServiceDeskRoleSynchronizer,
            sync.TaskNoteSynchronizer,
            sync.ServiceCallTaskSynchronizer,
            sync.ServiceCallTaskResourceSynchronizer,
            sync.TaskPredecessorSynchronizer,
            sync.ResourceRoleDepartmentSynchronizer,
        ]
        self.grades['slow'].synchronizers = [
            # Our time entry sync makes some complex queries for Autotask
            # and is CPU-intensive for their database. So they only let us
            # run it once a day. If in the future they support a filter to
            # get time entries only for non-completed tickets, we could use
            # that filter and run the sync more often.
            sync.TimeEntrySynchronizer,
            sync.CompanyAlertSynchronizer,
        ]
        self.grades['ludicrous_slow'].synchronizers = [
        ]
