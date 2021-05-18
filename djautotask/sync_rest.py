import logging
from dateutil.parser import parse
from decimal import Decimal

from django.db import transaction, IntegrityError
from django.db.models import Q
from django.utils import timezone

from djautotask import api_rest as api
from djautotask import models
from .sync import InvalidObjectException, SyncResults, log_sync_job, \
    TicketNoteSynchronizer, TimeEntrySynchronizer, \
    TicketSecondaryResourceSynchronizer, ParentSynchronizer
from .utils import DjautotaskSettings

CREATED = 1
UPDATED = 2
SKIPPED = 3

logger = logging.getLogger(__name__)


class Synchronizer:
    lookup_key = 'id'
    last_updated_field = 'lastActivityDate'

    def __init__(self, full=False, *args, **kwargs):
        self.api_conditions = []
        self.client = self.client_class()
        self.full = full

    def set_relations(self, instance, json_data):
        for json_field, value in self.related_meta.items():
            model_class, field_name = value
            self._assign_relation(
                instance,
                json_data,
                json_field,
                model_class,
                field_name
            )

    @staticmethod
    def _assign_null_relation(instance, model_field):
        """
        Set the FK to null, but handle issues like the FK being non-null.
        """
        try:
            setattr(instance, model_field, None)
        except ValueError:
            # The model_field may have been non-null.
            raise InvalidObjectException(
                "Unable to set field {} on {} to null, as it's required.".
                format(model_field, instance)
            )

    def _assign_relation(self, instance, json_data,
                         json_field, model_class, model_field):
        """
        Look up the given foreign relation, and set it to the given
        field on the instance.
        """
        uid = json_data.get(json_field)

        try:
            if uid:
                related_instance = model_class.objects.get(pk=uid)
                setattr(instance, model_field, related_instance)
            else:
                self._assign_null_relation(instance, model_field)
        except model_class.DoesNotExist:
            logger.warning(
                'Failed to find {} {} for {} {}.'.format(
                    json_field,
                    uid,
                    type(instance),
                    instance.id
                )
            )
            self._assign_null_relation(instance, model_field)

    def _instance_ids(self, filter_params=None):
        if not filter_params:
            ids = self.model_class.objects.all().order_by(self.lookup_key)\
                .values_list(self.lookup_key, flat=True)
        else:
            ids = self.model_class.objects.filter(filter_params)\
                .order_by(self.lookup_key)\
                .values_list(self.lookup_key, flat=True)
        return set(ids)

    def get(self, results):
        return self.fetch_records(results)

    def fetch_records(self, results):
        """
        For all pages of results, save each page of results to the DB.
        """
        next_url = None
        while True:
            logger.info(
                'Fetching {} records'.format(
                    self.model_class.__bases__[0].__name__)
            )
            api_return = self.get_page(next_url)
            page = api_return.get("items")
            next_url = api_return.get("pageDetails").get("nextPageUrl")
            self.persist_page(page, results)

            if not next_url:
                break

        return results

    def persist_page(self, records, results):
        """Persist one page of records to DB."""
        for record in records:
            try:
                with transaction.atomic():
                    instance, result = self.update_or_create_instance(record)
                if result == CREATED:
                    results.created_count += 1
                elif result == UPDATED:
                    results.updated_count += 1
                else:
                    results.skipped_count += 1
            except InvalidObjectException as e:
                logger.warning('{}'.format(e))

            results.synced_ids.add(record['id'])

        return results

    def get_page(self, *args, **kwargs):
        raise NotImplementedError

    def get_single(self, *args, **kwargs):
        raise NotImplementedError

    def _assign_field_data(self, instance, api_instance):
        raise NotImplementedError

    def _set_datetime_attribute(self, instance, attribute_name):
        if getattr(instance, attribute_name):
            setattr(instance,
                    attribute_name,
                    parse(getattr(instance, attribute_name))
                    )

    def fetch_sync_by_id(self, instance_id):
        api_instance = self.get_single(instance_id)
        instance, created = \
            self.update_or_create_instance(api_instance['item'])
        return instance

    def update_or_create_instance(self, api_instance):
        """
        Creates and returns an instance if it does not already exist.
        """
        result = None
        api_instance = self.remove_null_characters(api_instance)
        try:
            instance_pk = api_instance[self.lookup_key]
            instance = self.model_class.objects.get(pk=instance_pk)
        except self.model_class.DoesNotExist:
            instance = self.model_class()
            result = CREATED

        try:
            self._assign_field_data(instance, api_instance)

            # This will return the created instance, the updated instance, or
            # if the instance is skipped an unsaved copy of the instance.
            if result == CREATED:
                if self.model_class is models.TicketTracker:
                    instance.save(force_insert=True)
                else:
                    instance.save()
            elif instance.tracker.changed():
                instance.save()
                result = UPDATED
            else:
                result = SKIPPED
        except IntegrityError as e:
            # This can happen when multiple threads are creating the
            # same ticket at once.
            msg = "IntegrityError while attempting to create {}." \
                  " Error: {}".format(self.model_class, e)
            logger.error(msg)
            raise InvalidObjectException(msg)

        if result == CREATED:
            result_log = 'Created'
        elif result == UPDATED:
            result_log = 'Updated'
        else:
            result_log = 'Skipped'

        logger.info('{}: {} {}'.format(
            result_log,
            self.model_class.__bases__[0].__name__,
            instance
        ))

        return instance, result

    def prune_stale_records(self, initial_ids, synced_ids):
        """
        Delete records that existed when sync started but were
        not seen as we iterated through all records from REST API.
        """
        stale_ids = initial_ids - synced_ids
        deleted_count = 0
        if stale_ids:
            delete_qset = self.get_delete_qset(stale_ids)
            deleted_count = delete_qset.count()

            logger.info(
                'Removing {} stale records for model: {}'.format(
                    len(stale_ids), self.model_class.__bases__[0].__name__,
                )
            )
            delete_qset.delete()

        return deleted_count

    def get_delete_qset(self, stale_ids):
        return self.model_class.objects.filter(pk__in=stale_ids)

    def get_sync_job_qset(self):
        return models.SyncJob.objects.filter(
            entity_name=self.model_class.__bases__[0].__name__
        )

    @log_sync_job
    def sync(self):
        sync_job_qset = self.get_sync_job_qset().filter(success=True)

        if sync_job_qset.count() > 1 and not self.full:
            last_sync_job_time = sync_job_qset.last().start_time.strftime(
                '%Y-%m-%dT%H:%M:%S.%fZ')
            self.api_conditions.append(
                [self.last_updated_field, last_sync_job_time, "gt"]
            )
        results = SyncResults()
        results = self.get(results)

        if self.full:
            # Set of IDs of all records prior to sync,
            # to find stale records for deletion.
            initial_ids = self._instance_ids()

            results.deleted_count = self.prune_stale_records(
                initial_ids, results.synced_ids
            )

        return results.created_count, results.updated_count, \
            results.skipped_count, results.deleted_count

    def remove_null_characters(self, json_data):
        for value in json_data:
            if isinstance(json_data.get(value), str):
                json_data[value] = json_data[value].replace('\x00', '')

        return json_data


class SyncRestRecordUDFMixin:

    def _assign_udf_data(self, instance, udfs):
        for item in udfs:
            try:
                name = item['name']
                value = item['value']

                udf = self.udf_class.objects.get(
                    name=name
                )

                instance.udf[str(udf.id)] = {
                    'name': name,
                    'value': value,
                    'label': udf.label,
                    'type': udf.type,
                    'is_picklist': udf.is_picklist
                }

                if value and udf.is_picklist:
                    # On a picklist item, the label is different from
                    # the name.
                    instance.udf[str(udf.id)]['label'] = \
                        udf.picklist[value]['label']

            except self.udf_class.MultipleObjectsReturned as e:
                # Shouldn't ever happen but just in case, log and continue
                logger.error(
                    'Multiple UDF records returned for 1 name: {}'.format(e))
            except self.udf_class.DoesNotExist as e:
                # Can happen if sync not 100% up to date, debug log and
                # continue
                logger.debug(
                    'No UDF records returned for name: {}'.format(e))
            except KeyError as e:
                # UDF has likely been updated but we don't have the
                # updated changes locally until the UDF class has been synced.
                logger.warning(
                    'KeyError when trying to access UDF '
                    'picklist label. {}'.format(e)
                )


class ContactSynchronizer(Synchronizer):
    client_class = api.ContactsAPIClient
    model_class = models.ContactTracker

    related_meta = {
        'companyID': (models.Account, 'account'),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_conditions = [['IsActive', 'true']]

    def _assign_field_data(self, instance, json_data):
        instance.id = json_data['id']
        instance.first_name = json_data.get('firstName')
        instance.last_name = json_data.get('lastName')
        instance.email_address = json_data.get('emailAddress')
        instance.email_address2 = json_data.get('emailAddress2')
        instance.email_address3 = json_data.get('emailAddress3')
        instance.phone = json_data.get('phone')
        instance.alternate_phone = json_data.get('alternatePhone')
        instance.mobile_phone = json_data.get('mobilePhone')

        self.set_relations(instance, json_data)

        return instance

    def get_page(self, next_url=None, *args, **kwargs):
        kwargs['conditions'] = self.api_conditions
        return self.client.get_contacts(next_url, *args, **kwargs)


class TicketTaskMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request_settings = DjautotaskSettings().get_settings()
        self.completed_date = (timezone.now() - timezone.timedelta(
                hours=request_settings.get('keep_completed_hours')
            )).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        self.api_conditions = [
            [
                {
                    "op": "or",
                    "operands": [
                        [self.completed_date_field, self.completed_date, 'gt'],
                        ['status', models.Status.COMPLETE_ID, 'noteq']
                    ]
                }
            ]
        ]


# ParentSynchronizer: using SOAP API
class TicketSynchronizer(SyncRestRecordUDFMixin, TicketTaskMixin, Synchronizer,
                         ParentSynchronizer):
    client_class = api.TicketsAPIClient
    model_class = models.TicketTracker
    udf_class = models.TicketUDF
    completed_date_field = 'completedDate'

    related_meta = {
        'companyID': (models.Account, 'account'),
        'status': (models.Status, 'status'),
        'assignedResourceID': (models.Resource, 'assigned_resource'),
        'priority': (models.Priority, 'priority'),
        'queueID': (models.Queue, 'queue'),
        'projectID': (models.Project, 'project'),
        'ticketCategory': (models.TicketCategory, 'category'),
        'ticketType': (models.TicketType, 'type'),
        'source': (models.Source, 'source'),
        'issueType': (models.IssueType, 'issue_type'),
        'subIssueType': (models.SubIssueType, 'sub_issue_type'),
        'assignedResourceRoleID': (models.Role, 'assigned_resource_role'),
        'billingCodeID': (models.AllocationCode, 'allocation_code'),
        'contractID': (models.Contract, 'contract'),
        'contactID': (models.Contact, 'contact'),
    }

    def _assign_field_data(self, instance, json_data):
        instance.id = json_data['id']
        instance.title = json_data['title']

        instance.ticket_number = json_data.get('ticketNumber')
        instance.description = json_data.get('description')
        instance.estimated_hours = json_data.get('estimatedHours')
        instance.service_level_agreement = \
            json_data.get('serviceLevelAgreementID')
        instance.service_level_agreement_has_been_met = \
            bool(json_data.get('serviceLevelAgreementHasBeenMet'))
        sla_paused = \
            json_data.get('serviceLevelAgreementPausedNextEventHours')
        instance.first_response_date_time = \
            json_data.get('firstResponseDateTime')
        instance.first_response_due_date_time = \
            json_data.get('firstResponseDueDateTime')
        instance.resolution_plan_date_time = \
            json_data.get('resolutionPlanDateTime')
        instance.resolution_plan_due_date_time = \
            json_data.get('resolutionPlanDueDateTime')
        instance.resolved_date_time = \
            json_data.get('resolvedDateTime')
        instance.resolved_due_date_time = \
            json_data.get('resolvedDueDateTime')
        instance.create_date = json_data.get('createDate')
        instance.due_date_time = json_data.get('dueDateTime')
        instance.completed_date = json_data.get('completedDate')
        instance.last_activity_date = json_data.get('lastActivityDate')

        self._set_datetime_attribute(instance, 'first_response_date_time')
        self._set_datetime_attribute(instance,
                                     'first_response_due_date_time')
        self._set_datetime_attribute(instance, 'resolution_plan_date_time')
        self._set_datetime_attribute(instance,
                                     'resolution_plan_due_date_time')
        self._set_datetime_attribute(instance, 'resolved_date_time')
        self._set_datetime_attribute(instance, 'resolved_due_date_time')
        self._set_datetime_attribute(instance, 'create_date')
        self._set_datetime_attribute(instance, 'due_date_time')
        self._set_datetime_attribute(instance, 'completed_date')
        self._set_datetime_attribute(instance, 'last_activity_date')

        udfs = json_data.get('userDefinedFields')

        # Refresh udf field to eliminate stale udfs
        instance.udf = dict()

        if len(udfs):
            self._assign_udf_data(instance, udfs)

        if sla_paused:
            instance.service_level_agreement_paused_next_event_hours = \
                Decimal(str(round(sla_paused, 2)))
        if instance.estimated_hours:
            instance.estimated_hours = \
                Decimal(str(round(instance.estimated_hours, 2)))

        self.set_relations(instance, json_data)
        return instance

    def get_page(self, next_url=None, *args, **kwargs):
        kwargs['conditions'] = self.api_conditions
        return self.client.get_tickets(next_url, *args, **kwargs)

    def get_single(self, ticket_id):
        return self.client.get_ticket(ticket_id)

    def fetch_sync_by_id(self, instance_id):
        instance = super().fetch_sync_by_id(instance_id)
        if instance.status.id != models.Status.COMPLETE_ID:
            self.sync_related(instance)
        return instance

    # method in ParentSynchronizer: using SOAP API
    def sync_related(self, instance):
        sync_classes = []
        query_params = ('TicketID', instance.id)

        sync_classes.append(
            (TicketNoteSynchronizer(), query_params)
        )
        sync_classes.append(
            (TimeEntrySynchronizer(), query_params)
        )
        sync_classes.append(
            (TicketSecondaryResourceSynchronizer(), query_params)
        )

        self.sync_children(*sync_classes)


class TaskSynchronizer(SyncRestRecordUDFMixin, TicketTaskMixin, Synchronizer):
    client_class = api.TasksAPIClient
    model_class = models.TaskTracker
    udf_class = models.TaskUDF
    object_filter_field = 'projectID'
    completed_date_field = 'completedDateTime'

    related_meta = {
        'assignedResourceID': (models.Resource, 'assigned_resource'),
        'assignedResourceRoleID': (models.Role, 'assigned_resource_role'),
        'billingCodeID': (models.AllocationCode, 'allocation_code'),
        'departmentID': (models.Department, 'department'),
        'phaseID': (models.Phase, 'phase'),
        'projectID': (models.Project, 'project'),
        'priorityLabel': (models.Priority, 'priority'),
        'status': (models.Status, 'status'),
    }

    def __init__(self, *args, **kwargs):
        self.last_updated_field = 'lastActivityDateTime'
        super().__init__(*args, **kwargs)
        self.api_conditions += [
            ['projectId', list(self.get_active_ids()), 'in']
        ]

    def get_active_ids(self):
        active_projects = models.Project.objects.exclude(
            Q(status__is_active=False) |
            Q(status__id=models.ProjectStatus.COMPLETE_ID)
        ).values_list('id', flat=True).order_by(self.lookup_key)

        return active_projects

    def _assign_field_data(self, instance, json_data):
        instance.id = json_data['id']
        instance.title = json_data['title']

        instance.number = json_data.get('taskNumber')
        instance.description = json_data.get('description')
        instance.create_date = json_data.get('createDateTime')
        instance.completed_date = json_data.get('completedDateTime')
        instance.start_date = json_data.get('startDateTime')
        instance.end_date = json_data.get('endDateTime')
        instance.estimated_hours = json_data.get('estimatedHours')
        instance.remaining_hours = json_data.get('remainingHours')
        instance.last_activity_date = json_data.get('lastActivityDateTime')

        self._set_datetime_attribute(instance, 'create_date')
        self._set_datetime_attribute(instance, 'completed_date')
        self._set_datetime_attribute(instance, 'start_date')
        self._set_datetime_attribute(instance, 'end_date')
        self._set_datetime_attribute(instance, 'last_activity_date')

        udfs = json_data.get('userDefinedFields')

        # Refresh udf field to eliminate stale udfs
        instance.udf = dict()

        if len(udfs):
            self._assign_udf_data(instance, udfs)

        if instance.estimated_hours:
            instance.estimated_hours = \
                Decimal(str(round(instance.estimated_hours, 2)))
        if instance.remaining_hours:
            instance.remaining_hours = \
                Decimal(str(round(instance.remaining_hours, 2)))

        self.set_relations(instance, json_data)
        return instance

    def get_page(self, next_url=None, *args, **kwargs):
        kwargs['conditions'] = self.api_conditions
        return self.client.get_tasks(next_url, *args, **kwargs)
