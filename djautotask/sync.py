import logging
from dateutil.parser import parse
from decimal import Decimal

from django.db import transaction, IntegrityError
from django.db.models import Q
from django.utils import timezone

from djautotask import api
from djautotask import models
from .api import ApiCondition as A, AutotaskRecordNotFoundError
from .utils import DjautotaskSettings

CREATED = 1
UPDATED = 2
SKIPPED = 3

logger = logging.getLogger(__name__)


class InvalidObjectException(Exception):
    """
    If for any reason an object can't be created (for example, it references
    an unknown foreign object, or is missing a required field), raise this
    so that the synchronizer can catch it and continue with other records.
    """
    pass


def log_sync_job(f):
    def wrapper(*args, **kwargs):
        sync_instance = args[0]
        created_count = updated_count = deleted_count = skipped_count = 0
        sync_job = models.SyncJob()
        sync_job.start_time = timezone.now()
        sync_job.entity_name = sync_instance.model_class.__bases__[0].__name__
        sync_job.synchronizer_class = sync_instance.__class__.__name__

        if sync_instance.full:
            sync_job.sync_type = 'full'
        else:
            sync_job.sync_type = 'partial'

        sync_job.save()

        try:
            created_count, updated_count, skipped_count, deleted_count = \
                f(*args, **kwargs)
            sync_job.success = True
        except Exception as e:
            sync_job.message = str(e.args[0])
            sync_job.success = False
            raise
        finally:
            sync_job.end_time = timezone.now()
            sync_job.added = created_count
            sync_job.updated = updated_count
            sync_job.skipped = skipped_count
            sync_job.deleted = deleted_count
            sync_job.save()

        return created_count, updated_count, skipped_count, deleted_count

    return wrapper


class SyncResults:
    """Track results of a sync job."""

    def __init__(self):
        self.created_count = 0
        self.updated_count = 0
        self.skipped_count = 0
        self.deleted_count = 0
        self.synced_ids = set()


class ParentSynchronizer:

    def sync_related(self, instance):
        raise NotImplementedError

    def sync_children(self, *args):
        for synchronizer, query_params in args:
            created_count, updated_count, skipped_count, deleted_count = \
                synchronizer.callback_sync(
                    query_params
                )
            msg = '{} Child Sync - Created: {},' \
                  ' Updated: {}, Skipped: {}, Deleted: {}'.format(
                    synchronizer.model_class.__bases__[0].__name__,
                    created_count,
                    updated_count,
                    skipped_count,
                    deleted_count
                  )

            logger.info(msg)


class ChildSynchronizer:

    def _child_instance_ids(self, query_params):
        ids = self.model_class.objects.filter(
            ticket__id=query_params[1]
        ).values_list('id', flat=True)

        return set(ids)

    def _get_children(self, results, query_params):
        self._build_children_conditions(query_params)
        logger.info('Fetching {} records.'.format(
            self.model_class.__bases__[0].__name__))
        return self.fetch_records(results)

    def _build_children_conditions(self, query_params):
        parent_field, parent_id = query_params
        self.client.clear_conditions()
        self.client.add_condition(
            A(
                op='eq',
                field=parent_field,
                value=parent_id
            )
        )

    def callback_sync(self, query_params):
        results = SyncResults()

        # Set of IDs of all records prior to sync,
        # to find stale records for deletion.
        initial_ids = self._child_instance_ids(query_params)

        results = self._get_children(results, query_params)

        results.deleted_count = self.prune_stale_records(
            initial_ids,
            results.synced_ids
        )

        return results.created_count, results.updated_count, \
            results.skipped_count, results.deleted_count


class BatchQueryMixin:

    condition_pool = None
    condition_field_name = None
    batch_query_size = None
    client = None

    def __init__(self, full=False, *args, **kwargs):
        settings = DjautotaskSettings().get_settings()
        self.batch_query_size = settings.get('batch_query_size')
        super().__init__(full, *args, **kwargs)
        self._add_conditions()

    def _add_conditions(self):
        self.condition_pool = list(self.active_ids)
        self.client.add_condition(
            A(
                op='in',
                field=self.condition_field_name,
                value=self.condition_pool
            )
        )

    # another approach for sync to resolve an issue of AT REST API
    # query limitation(up to 500), especially when OR & IN conditions are used.
    # Split original get call into several small calls and
    # repeat with different api condition
    def get(self, results):

        field_ids = self.condition_pool
        batch_query_size = self.batch_query_size

        while field_ids:
            batch_condition = field_ids[:batch_query_size]
            del field_ids[:batch_query_size]
            self._replace_batch_conditions(self.client.conditions,
                                           batch_condition,
                                           self.condition_field_name)
            self.fetch_records(results)

        return results

    def _replace_batch_conditions(self, conditions, batch_condition,
                                  condition_field_name):
        for c in conditions:
            if c.field == condition_field_name:
                c.value = batch_condition

    @property
    def active_ids(self):
        raise NotImplementedError


class MultiConditionBatchQueryMixin(BatchQueryMixin):

    def _add_conditions(self):
        self.multi_conditions = {}
        for field_name, active_ids in self.active_ids.items():
            self.multi_conditions.update({
                field_name: A(
                    op='in',
                    field=field_name,
                    value=active_ids
                )
            })

    def get(self, results):

        for condition_field_name, condition in self.multi_conditions.items():
            field_ids = condition.value
            batch_query_size = self.batch_query_size
            idx_condition = self.client.add_condition(
                A(
                    op='in',
                    field=condition_field_name,
                    value=[]
                )
            )

            while field_ids:
                batch_condition = field_ids[:batch_query_size]
                del field_ids[:batch_query_size]
                self._replace_batch_conditions(self.client.conditions,
                                               batch_condition,
                                               condition_field_name)
                self.fetch_records(results)

            self.client.remove_condition(idx_condition)

        return results


class Synchronizer:
    lookup_key = 'id'
    last_updated_field = 'lastActivityDate'

    def __init__(self, full=False, *args, **kwargs):
        self.client = self.client_class(
            impersonation_resource=kwargs.get('impersonation_resource'),
        )
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
            if uid is not None and uid != '':
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
        # self.lookup_key is used only for json_data. In DB, id is fixed for
        # primary key name
        db_lookup_key = 'id'
        if not filter_params:
            ids = self.model_class.objects.all().values_list(
                db_lookup_key, flat=True)
        else:
            ids = self.model_class.objects.filter(filter_params).values_list(
                db_lookup_key, flat=True)
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

            results.synced_ids.add(self.get_record_id(record))

        return results

    def get_record_id(self, record):
        return int(record[self.lookup_key])

    def get_page(self, next_url=None, *args, **kwargs):
        return self.client.get(next_url, *args, **kwargs)

    def get_single(self, instance_id):
        return self.client.get_single(instance_id)

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
            instance_pk = self.get_record_id(api_instance)
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

    def create(self, **kwargs):
        raise NotImplementedError()

    @log_sync_job
    def sync(self):
        sync_job_qset = self.get_sync_job_qset().filter(success=True)

        if sync_job_qset.count() > 1 and self.last_updated_field \
                and not self.full:
            last_sync_job_time = sync_job_qset.last().start_time.strftime(
                '%Y-%m-%dT%H:%M:%S.%fZ')
            self.client.add_condition(
                A(
                    field=self.last_updated_field,
                    value=last_sync_job_time,
                    op="gt"
                )
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


class SyncRecordUDFMixin:

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


class UDFSynchronizer(Synchronizer):
    lookup_key = 'name'
    model_class = None
    last_updated_field = None

    def get_record_id(self, record):
        try:
            return self.model_class.objects.\
                get(name=record[self.lookup_key]).id
        except self.model_class.DoesNotExist:
            return None

    def fetch_records(self, results):
        """
        For UDF, AT returns only 1 page of results; save the results to the DB.
        """
        next_url = self.client_class().get_api_url()
        logger.info(
            'Fetching {} records.'.format(self.model_class)
        )
        api_return = self.get_page(next_url)
        total_page = api_return.get("fields")
        if total_page:
            self.persist_page(total_page, results)

        return results

    def _assign_field_data(self, instance, object_data):

        instance.name = object_data.get('name')
        instance.label = object_data.get('label')
        instance.type = object_data.get('type')
        instance.is_picklist = object_data.get('isPickList')

        if instance.is_picklist:
            # Clear picklist to eliminate stale items
            instance.picklist = {}
            for item in object_data.get('picklistValues'):
                instance.picklist[item['value']] = {
                    'label': item['label'],
                    'is_default_value': item['isDefaultValue'],
                    'sort_order': item['sortOrder'],
                    'is_active': item['isActive'],
                    'is_system': item['isSystem'],
                }

        return instance


class TicketUDFSynchronizer(UDFSynchronizer):
    client_class = api.TicketsUDFAPIClient
    model_class = models.TicketUDFTracker


class TaskUDFSynchronizer(UDFSynchronizer):
    client_class = api.TasksUDFAPIClient
    model_class = models.TaskUDFTracker


class ProjectUDFSynchronizer(UDFSynchronizer):
    client_class = api.ProjectsUDFAPIClient
    model_class = models.ProjectUDFTracker


class CreateRecordMixin:

    def create(self, **kwargs):
        """
        Make a request to Autotask to create an entity.
        """
        instance = self.model_class()
        created_id = self.client.create(instance, **kwargs)

        # get_single retrieves the newly created entity info, which includes
        # generated/calculated fields from AT-side
        created_instance = self.get_single(created_id)

        return self.update_or_create_instance(created_instance['item'])


class DeleteRecordMixin:

    def delete(self, instance, parent=None):
        """
        Make a request to Autotask to delete an entity.
        """
        try:
            deleted_instance_id = self.client.delete(instance, parent)
            if deleted_instance_id:
                instance.delete()
        except AutotaskRecordNotFoundError:
            # We can safely delete instance to sync
            instance.delete()


class ContactSynchronizer(Synchronizer):
    client_class = api.ContactsAPIClient
    model_class = models.ContactTracker

    related_meta = {
        'companyID': (models.Account, 'account'),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client.add_condition(A(op='eq', field='isActive', value='true'))

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
        instance.extension = json_data.get('extension')

        self.set_relations(instance, json_data)

        return instance


class RoleSynchronizer(Synchronizer):
    client_class = api.RolesAPIClient
    model_class = models.RoleTracker
    last_updated_field = None

    def _assign_field_data(self, instance, json_data):
        instance.id = json_data['id']
        instance.active = json_data.get('isActive')
        instance.name = json_data.get('name')
        instance.description = json_data.get('description')
        instance.hourly_factor = json_data.get('hourlyFactor')
        instance.hourly_rate = json_data.get('hourlyRate')
        instance.role_type = json_data.get('roleType')
        instance.system_role = json_data.get('isSystemRole')

        if instance.hourly_factor:
            instance.hourly_factor = \
                Decimal(str(round(instance.hourly_factor, 2)))
        if instance.hourly_rate:
            instance.hourly_rate = \
                Decimal(str(round(instance.hourly_rate, 2)))

        return instance


class DepartmentSynchronizer(Synchronizer):
    client_class = api.DepartmentsAPIClient
    model_class = models.DepartmentTracker
    last_updated_field = None

    def _assign_field_data(self, instance, json_data):
        instance.id = json_data['id']
        instance.name = json_data.get('name')
        instance.description = json_data.get('description')
        instance.number = json_data.get('number')

        return instance


class ResourceServiceDeskRoleSynchronizer(Synchronizer):
    client_class = api.ResourceServiceDeskRolesAPIClient
    model_class = models.ResourceServiceDeskRoleTracker
    last_updated_field = None

    related_meta = {
        'resourceID': (models.Resource, 'resource'),
        'roleID': (models.Role, 'role'),
    }

    def _assign_field_data(self, instance, json_data):
        instance.id = json_data['id']
        instance.active = json_data.get('isActive')
        instance.default = json_data.get('isDefault')

        self.set_relations(instance, json_data)

        return instance


class ResourceRoleDepartmentSynchronizer(Synchronizer):
    client_class = api.ResourceRoleDepartmentsAPIClient
    model_class = models.ResourceRoleDepartmentTracker
    last_updated_field = None

    related_meta = {
        'resourceID': (models.Resource, 'resource'),
        'roleID': (models.Role, 'role'),
        'departmentID': (models.Department, 'department'),
    }

    def _assign_field_data(self, instance, json_data):
        instance.id = json_data['id']
        instance.active = json_data.get('isActive')
        instance.default = json_data.get('isDefault')
        instance.department_lead = json_data.get('isDepartmentLead')

        self.set_relations(instance, json_data)

        return instance


class TicketTaskMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request_settings = DjautotaskSettings().get_settings()
        completed_date = (timezone.now() - timezone.timedelta(
                hours=request_settings.get('keep_completed_hours')
            )).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        self.client.add_condition(
            A(
                A(
                    op='gt',
                    field=self.completed_date_field,
                    value=completed_date
                ),
                A(op='noteq', field='status', value=models.Status.COMPLETE_ID),
                op='or'
            )
        )


class TicketSynchronizer(CreateRecordMixin,
                         SyncRecordUDFMixin,
                         TicketTaskMixin,
                         Synchronizer,
                         ParentSynchronizer):
    client_class = api.TicketsAPIClient
    model_class = models.TicketTracker
    udf_class = models.TicketUDF
    completed_date_field = 'completedDate'

    related_meta = {
        'companyID': (models.Account, 'account'),
        'companyLocationID': (models.AccountPhysicalLocation,
                              'account_physical_location'),
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
        'billingCodeID': (models.BillingCode, 'billing_code'),
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

        # It's important to set the SLA paused field to zero if it's not
        # present in the JSON data because we need to track when a ticket
        # moves from a paused SLA state to one where the SLA timer is running.
        if not sla_paused:
            sla_paused = 0

        instance.service_level_agreement_paused_next_event_hours = \
            Decimal(str(round(sla_paused, 2)))
        if instance.estimated_hours:
            instance.estimated_hours = \
                Decimal(str(round(instance.estimated_hours, 2)))

        self.set_relations(instance, json_data)
        return instance

    def fetch_sync_by_id(self, instance_id):
        instance = super().fetch_sync_by_id(instance_id)
        if not instance.status or \
                instance.status.id != models.Status.COMPLETE_ID:
            self.sync_related(instance)
        return instance

    def sync_related(self, instance):
        sync_classes = []
        query_params = ('ticketID', instance.id)

        sync_classes.append(
            (TicketNoteSynchronizer(), query_params)
        )
        sync_classes.append(
            (TimeEntrySynchronizer(), query_params)
        )
        sync_classes.append(
            (TicketSecondaryResourceSynchronizer(), query_params)
        )

        TicketChecklistItemsSynchronizer().sync_items(instance)

        self.sync_children(*sync_classes)

    # TODO move to parent sync when generalized, OR remove when
    #  "sync/card packager" class created
    def get_changed_values(self, record, **kwargs):
        """
        Only create tickets with manually selected fields, so AT can set its
        own defaults.

        """
        changed_field_keys = kwargs.get('changed_fields')

        new_record = {}
        if changed_field_keys:
            for field in changed_field_keys:
                new_record[field] = getattr(record, field)

        return new_record

    def create(self, **kwargs):
        """
        Make a request to Autotask to create a Ticket.
        """

        description = kwargs.get('description')

        if not self.client.impersonation_resource:
            description = "{}\n\nTicket was created by {} {}.".format(
                description if description is not None else "",
                kwargs['resource'].first_name,
                kwargs['resource'].last_name,
            )
        kwargs.update({
            'description': description
        })

        new_record_fields = self.get_changed_values(**kwargs)
        return super().create(**new_record_fields)


class TaskSynchronizer(SyncRecordUDFMixin, TicketTaskMixin,
                       BatchQueryMixin, Synchronizer):
    client_class = api.TasksAPIClient
    model_class = models.TaskTracker
    udf_class = models.TaskUDF
    completed_date_field = 'completedDateTime'
    condition_field_name = 'projectId'
    last_updated_field = 'lastActivityDateTime'

    related_meta = {
        'taskCategoryID': (models.TaskCategory, 'category'),
        'assignedResourceID': (models.Resource, 'assigned_resource'),
        'assignedResourceRoleID': (models.Role, 'assigned_resource_role'),
        'billingCodeID': (models.BillingCode, 'billing_code'),
        'departmentID': (models.Department, 'department'),
        'phaseID': (models.Phase, 'phase'),
        'projectID': (models.Project, 'project'),
        'priorityLabel': (models.Priority, 'priority'),
        'status': (models.Status, 'status'),
    }

    @property
    def active_ids(self):
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

        if instance.description:
            # Truncate the field to 8000 characters as per AT docs. Since we've
            # received descriptions greater than 8000 we'll truncate here
            # instead of catching the DataError that would be raised.
            # It is preferred to keep the DB schema in-line with the
            # AT specifications, even if they are wrong.
            instance.description = \
                instance.description[:models.Task.MAX_DESCRIPTION]
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


class NoteSynchronizer(CreateRecordMixin, BatchQueryMixin, Synchronizer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client.add_condition(
            A(op='noteq', field='noteType',
              value=models.NoteType.WORKFLOW_RULE_NOTE_ID)
        )

    def _assign_field_data(self, instance, object_data):

        instance.id = object_data['id']
        instance.title = object_data.get('title')
        instance.description = object_data.get('description')
        instance.create_date_time = object_data.get('createDateTime')
        instance.last_activity_date = object_data.get('lastActivityDate')

        self._set_datetime_attribute(instance, 'create_date_time')
        self._set_datetime_attribute(instance, 'last_activity_date')

        if instance.description:
            # Autotask docs say the max description length is 3200
            # characters but we've seen descriptions that are longer than that.
            # So truncate the field to 3200 characters just in case.
            instance.description = instance.description[:3200]

        self.set_relations(instance, object_data)

        return instance

    def create(self, **kwargs):
        """
        Make a request to Autotask to create a Note.
        """
        if self.client.impersonation_resource or \
                kwargs.get('created_by_contact_id'):
            description = kwargs['description']
        else:
            description = "{}\n\nNote was added by {} {}.".format(
                kwargs['description'],
                kwargs['resource'].first_name,
                kwargs['resource'].last_name
            )
        kwargs.update({
            self.related_instance_name: kwargs.pop('card'),
            'description': description
        })

        return super().create(**kwargs)


class TicketNoteSynchronizer(NoteSynchronizer, ChildSynchronizer):
    client_class = api.TicketNotesAPIClient
    model_class = models.TicketNoteTracker
    condition_field_name = 'ticketID'
    related_instance_name = 'ticket'

    related_meta = {
        'noteType': (models.NoteType, 'note_type'),
        'creatorResourceID': (models.Resource, 'creator_resource'),
        'ticketID': (models.Ticket, 'ticket'),
        'createdByContactID': (models.Contact, 'created_by_contact'),
    }

    @property
    def active_ids(self):
        active_ids = models.Ticket.objects.all().\
            values_list('id', flat=True).order_by(self.lookup_key)

        return active_ids

    def _build_children_conditions(self, query_params):
        parent_field, parent_id = query_params
        self.client.clear_conditions()
        self.client.add_condition(
            A(
                A(op='noteq', field='noteType',
                  value=models.NoteType.WORKFLOW_RULE_NOTE_ID),
                A(
                    op='eq',
                    field=parent_field,
                    value=parent_id
                ),
                op='and'
            )
        )


class TaskNoteSynchronizer(NoteSynchronizer):
    client_class = api.TaskNotesAPIClient
    model_class = models.TaskNoteTracker
    condition_field_name = 'taskID'
    related_instance_name = 'task'

    related_meta = {
        'noteType': (models.NoteType, 'note_type'),
        'creatorResourceID': (models.Resource, 'creator_resource'),
        'taskID': (models.Task, 'task'),
        'createdByContactID': (models.Contact, 'created_by_contact'),
    }

    @property
    def active_ids(self):
        active_ids = models.Task.objects.exclude(
            status=models.Status.COMPLETE_ID
        ).values_list('id', flat=True).order_by(self.lookup_key)

        return active_ids


class TimeEntrySynchronizer(CreateRecordMixin, MultiConditionBatchQueryMixin,
                            Synchronizer,
                            ChildSynchronizer):
    client_class = api.TimeEntriesAPIClient
    model_class = models.TimeEntryTracker
    last_updated_field = 'lastModifiedDateTime'

    related_meta = {
        'resourceID': (models.Resource, 'resource'),
        'ticketID': (models.Ticket, 'ticket'),
        'taskID': (models.Task, 'task'),
        'timeEntryType': (models.TaskTypeLink, 'type'),
        'billingCodeID': (models.BillingCode, 'billing_code'),
        'roleID': (models.Role, 'role'),
        'contractID': (models.Contract, 'contract'),
    }

    @property
    def active_ids(self):
        active_tickets = models.Ticket.objects.all().values_list(
            'id', flat=True).order_by(self.lookup_key)
        active_tasks = models.Task.objects.all().values_list(
            'id', flat=True).order_by(self.lookup_key)

        active_ids = dict()
        if len(active_tickets):
            active_ids.update({'ticketID': list(active_tickets)})
        if len(active_tasks):
            active_ids.update({'taskID': list(active_tasks)})
        return active_ids

    def _assign_field_data(self, instance, object_data):
        instance.id = object_data['id']
        instance.date_worked = object_data.get('dateWorked')
        instance.start_date_time = object_data.get('startDateTime')
        instance.end_date_time = object_data.get('endDateTime')
        instance.summary_notes = object_data.get('summaryNotes')
        instance.internal_notes = object_data.get('internalNotes')
        instance.non_billable = object_data.get('isNonBillable')
        instance.hours_worked = object_data.get('hoursWorked')
        instance.hours_to_bill = object_data.get('hoursToBill')
        instance.offset_hours = object_data.get('offsetHours')

        self._set_datetime_attribute(instance, 'date_worked')
        self._set_datetime_attribute(instance, 'start_date_time')
        self._set_datetime_attribute(instance, 'end_date_time')

        if instance.hours_worked:
            instance.hours_worked = \
                Decimal(str(round(instance.hours_worked, 4)))
        if instance.hours_to_bill:
            instance.hours_to_bill = \
                Decimal(str(round(instance.hours_to_bill, 4)))
        if instance.offset_hours:
            instance.offset_hours = \
                Decimal(str(round(instance.offset_hours, 4)))

        self.set_relations(instance, object_data)
        return instance


class SecondaryResourceSyncronizer(CreateRecordMixin, DeleteRecordMixin,
                                   BatchQueryMixin, Synchronizer):

    def create(self, resource, role, entity):
        """
        Make a request to Autotask to create a SecondaryResource.
        """
        body = {
            'resource': resource,
            'role': role,
            self.related_instance_name: entity,
        }
        return super().create(**body)

    def delete(self, instances, parent=None):
        """
        Make a request to Autotask to delete a SecondaryResource.
        """
        for instance in instances:
            super().delete(instance, parent)

    def _assign_field_data(self, instance, object_data):
        instance.id = object_data['id']
        self.set_relations(instance, object_data)
        return instance

    @property
    def active_ids(self):
        active_ids = self.related_instance_model.objects.all(). \
            values_list('id', flat=True).order_by(self.lookup_key)

        return active_ids


class TicketSecondaryResourceSynchronizer(SecondaryResourceSyncronizer,
                                          ChildSynchronizer):
    client_class = api.TicketSecondaryResourcesAPIClient
    model_class = models.TicketSecondaryResourceTracker
    last_updated_field = None
    condition_field_name = 'ticketID'
    related_instance_name = 'ticket'
    related_instance_model = models.Ticket

    related_meta = {
        'resourceID': (models.Resource, 'resource'),
        'roleID': (models.Role, 'role'),
        'ticketID': (models.Ticket, 'ticket'),
    }


class TaskSecondaryResourceSynchronizer(SecondaryResourceSyncronizer):
    client_class = api.TaskSecondaryResourcesAPIClient
    model_class = models.TaskSecondaryResourceTracker
    last_updated_field = None
    condition_field_name = 'taskID'
    related_instance_name = 'task'
    related_instance_model = models.Task

    related_meta = {
        'resourceID': (models.Resource, 'resource'),
        'roleID': (models.Role, 'role'),
        'taskID': (models.Task, 'task'),
    }


class ProjectSynchronizer(SyncRecordUDFMixin, Synchronizer,
                          ParentSynchronizer):
    client_class = api.ProjectsAPIClient
    model_class = models.ProjectTracker
    udf_class = models.ProjectUDF
    last_updated_field = 'lastActivityDateTime'

    related_meta = {
        'projectLeadResourceID': (models.Resource, 'project_lead_resource'),
        'companyID': (models.Account, 'account'),
        'status': (models.ProjectStatus, 'status'),
        'projectType': (models.ProjectType, 'type'),
        'contractID': (models.Contract, 'contract'),
        'department': (models.Department, 'department'),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client.add_condition(
            A(
                A(
                    op='noteq',
                    field='status',
                    value=models.ProjectStatus.COMPLETE_ID
                ),
                A(
                    op='in',
                    field='status',
                    value=list(self.get_active_ids())
                ),
                op="and"
            )
        )

    def get_active_ids(self):
        active_project_statuses = models.ProjectStatus.objects.exclude(
            is_active=False).values_list('id', flat=True).order_by(
            self.lookup_key)

        return active_project_statuses

    def _assign_field_data(self, instance, object_data):

        instance.id = object_data['id']
        instance.name = object_data.get('projectName')
        instance.number = object_data.get('projectNumber')
        instance.description = object_data.get('description')
        instance.actual_hours = object_data.get('actualHours')
        instance.completed_percentage = object_data.get('completedPercentage')
        instance.duration = object_data.get('duration')
        instance.estimated_time = object_data.get('estimatedTime')
        instance.status_detail = object_data.get('statusDetail')

        instance.completed_date = object_data.get('completedDateTime')
        instance.end_date = object_data.get('endDateTime')
        instance.start_date = object_data.get('startDateTime')
        instance.last_activity_date_time = \
            object_data.get('lastActivityDateTime')

        self._set_datetime_attribute(instance, 'completed_date')
        self._set_datetime_attribute(instance, 'end_date')
        self._set_datetime_attribute(instance, 'start_date')
        self._set_datetime_attribute(instance, 'last_activity_date_time')

        if instance.completed_date:
            instance.completed_date = instance.completed_date.date()
        if instance.end_date:
            instance.end_date = instance.end_date.date()
        if instance.start_date:
            instance.start_date = instance.start_date.date()

        udfs = object_data.get('userDefinedFields')

        # Refresh udf field to eliminate stale udfs
        instance.udf = dict()

        if len(udfs):
            self._assign_udf_data(instance, udfs)

        if instance.estimated_time:
            instance.estimated_time = \
                Decimal(str(round(instance.estimated_time, 2)))
        if instance.actual_hours:
            instance.actual_hours = \
                Decimal(str(round(instance.actual_hours, 2)))

        if instance.description:
            # Autotask docs say the max description length is 2000
            # characters but we've seen descriptions that are longer than that.
            # So truncate the field to 2000 characters just in case.
            instance.description = instance.description[:2000]

        self.set_relations(instance, object_data)

        return instance


class TicketCategorySynchronizer(Synchronizer):
    client_class = api.TicketCategoriesAPIClient
    model_class = models.TicketCategoryTracker
    last_updated_field = None

    related_meta = {
        'displayColorRGB': (models.DisplayColor, 'display_color')
    }

    def _assign_field_data(self, instance, json_data):
        instance.id = json_data['id']
        instance.name = json_data.get('name')
        instance.active = json_data.get('isActive')

        self.set_relations(instance, json_data)

        return instance


class TaskPredecessorSynchronizer(BatchQueryMixin, Synchronizer):
    client_class = api.TaskPredecessorsAPIClient
    model_class = models.TaskPredecessorTracker
    condition_field_name = 'predecessorTaskID'
    last_updated_field = None

    related_meta = {
        'predecessorTaskID': (models.Task, 'predecessor_task'),
        'successorTaskID': (models.Task, 'successor_task'),
    }

    @property
    def active_ids(self):
        active_tasks = models.Task.objects.exclude(
            Q(status__is_active=False) |
            Q(status__id=models.Status.COMPLETE_ID)
        ).values_list('id', flat=True).order_by(self.lookup_key)

        return active_tasks

    def _assign_field_data(self, instance, json_data):
        instance.id = json_data['id']
        instance.lag_days = json_data.get('lagDays')

        self.set_relations(instance, json_data)

        return instance


class ServiceCallSynchronizer(
        CreateRecordMixin, BatchQueryMixin, Synchronizer):

    client_class = api.ServiceCallsAPIClient
    model_class = models.ServiceCallTracker
    condition_field_name = 'companyID'
    last_updated_field = 'lastModifiedDateTime'

    related_meta = {
        'companyID': (models.Account, 'account'),
        'companyLocationID':
            (models.AccountPhysicalLocation, 'location'),
        'status': (models.ServiceCallStatus, 'status'),
        'creatorResourceID': (models.Resource, 'creator_resource'),
        'canceledByResourceID': (models.Resource, 'canceled_by_resource')
    }

    @property
    def active_ids(self):
        active_ids = models.Account.objects.filter(
            active=True
        ).values_list('id', flat=True).order_by(self.lookup_key)

        return active_ids

    def _assign_field_data(self, instance, object_data):
        instance.id = object_data['id']
        instance.description = object_data.get('description')
        instance.duration = Decimal(str(object_data.get('duration')))
        instance.complete = object_data.get('isComplete')
        instance.create_date_time = object_data.get('createDateTime')
        instance.start_date_time = object_data.get('startDateTime')
        instance.end_date_time = object_data.get('endDateTime')
        instance.canceled_date_time = object_data.get('canceledDateTime')
        instance.last_modified_date_time = \
            object_data.get('lastModifiedDateTime')

        self._set_datetime_attribute(instance, 'create_date_time')
        self._set_datetime_attribute(instance, 'start_date_time')
        self._set_datetime_attribute(instance, 'end_date_time')
        self._set_datetime_attribute(instance, 'canceled_date_time')
        self._set_datetime_attribute(instance, 'last_modified_date_time')

        self.set_relations(instance, object_data)

        return instance


class ServiceCallTicketSynchronizer(
        CreateRecordMixin, BatchQueryMixin, Synchronizer):

    client_class = api.ServiceCallTicketsAPIClient
    model_class = models.ServiceCallTicketTracker
    condition_field_name = 'ticketID'
    last_updated_field = None

    related_meta = {
        'serviceCallID': (models.ServiceCall, 'service_call'),
        'ticketID': (models.Ticket, 'ticket')
    }

    @property
    def active_ids(self):
        active_ids = models.Ticket.objects.all().\
            values_list('id', flat=True).order_by(self.lookup_key)

        return active_ids

    def _assign_field_data(self, instance, object_data):
        instance.id = object_data['id']
        self.set_relations(instance, object_data)

        return instance


class ServiceCallTaskSynchronizer(
        CreateRecordMixin, BatchQueryMixin, Synchronizer):

    client_class = api.ServiceCallTasksAPIClient
    model_class = models.ServiceCallTaskTracker
    condition_field_name = 'taskID'
    last_updated_field = None

    related_meta = {
        'serviceCallID': (models.ServiceCall, 'service_call'),
        'taskID': (models.Task, 'task')
    }

    @property
    def active_ids(self):
        active_ids = models.Task.objects.exclude(
            status=models.Status.COMPLETE_ID
        ).values_list('id', flat=True).order_by(self.lookup_key)

        return active_ids

    def _assign_field_data(self, instance, object_data):
        instance.id = object_data['id']
        self.set_relations(instance, object_data)

        return instance


class ServiceCallTicketResourceSynchronizer(
        CreateRecordMixin, BatchQueryMixin, Synchronizer):

    client_class = api.ServiceCallTicketResourcesAPIClient
    model_class = models.ServiceCallTicketResourceTracker
    condition_field_name = 'serviceCallTicketID'
    last_updated_field = None

    related_meta = {
        'serviceCallTicketID':
            (models.ServiceCallTicket, 'service_call_ticket'),
        'resourceID': (models.Resource, 'resource')
    }

    @property
    def active_ids(self):
        active_ids = models.ServiceCallTicket.objects.all().\
            values_list('id', flat=True).order_by(self.lookup_key)

        return active_ids

    def _assign_field_data(self, instance, object_data):
        instance.id = object_data['id']
        self.set_relations(instance, object_data)

        return instance


class ServiceCallTaskResourceSynchronizer(
        CreateRecordMixin, BatchQueryMixin, Synchronizer):

    client_class = api.ServiceCallTaskResourcesAPIClient
    model_class = models.ServiceCallTaskResourceTracker
    condition_field_name = 'serviceCallTaskID'
    last_updated_field = None

    related_meta = {
        'serviceCallTaskID':
            (models.ServiceCallTask, 'service_call_task'),
        'resourceID': (models.Resource, 'resource')
    }

    @property
    def active_ids(self):
        active_ids = models.ServiceCallTask.objects.all().\
            values_list('id', flat=True).order_by(self.lookup_key)

        return active_ids

    def _assign_field_data(self, instance, object_data):
        instance.id = object_data['id']
        self.set_relations(instance, object_data)

        return instance


class BillingCodeSynchronizer(Synchronizer):
    client_class = api.BillingCodesAPIClient
    model_class = models.BillingCodeTracker
    last_updated_field = None

    related_meta = {
        'useType': (models.UseType, 'use_type')
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client.add_condition(A(op='eq', field='isActive', value=True))

    def _assign_field_data(self, instance, object_data):
        instance.id = object_data['id']
        instance.name = object_data.get('name')
        instance.description = object_data.get('description')
        instance.active = object_data.get('isActive')

        self.set_relations(instance, object_data)

        return instance


class ContractSynchronizer(Synchronizer):
    client_class = api.ContractsAPIClient
    model_class = models.ContractTracker
    last_updated_field = None

    related_meta = {
        'companyID': (models.Account, 'account')
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client.add_condition(A(op='eq', field='status', value='1'))

    def _assign_field_data(self, instance, object_data):
        instance.id = object_data['id']
        instance.name = object_data.get('contractName')
        instance.number = object_data.get('contractNumber')
        instance.status = str(object_data.get('status'))

        self.set_relations(instance, object_data)

        return instance


class AccountPhysicalLocationSynchronizer(BatchQueryMixin, Synchronizer):
    client_class = api.AccountPhysicalLocationsAPIClient
    model_class = models.AccountPhysicalLocationTracker
    condition_field_name = 'companyID'
    last_updated_field = None

    related_meta = {
        'companyID': (models.Account, 'account'),
    }

    def _assign_field_data(self, instance, object_data):
        instance.id = object_data['id']
        instance.name = object_data.get('name')
        instance.active = object_data.get('isActive')
        instance.primary = object_data.get('isPrimary')
        self.set_relations(instance, object_data)

        return instance

    @property
    def active_ids(self):
        active_ids = models.Account.objects.all().\
            values_list('id', flat=True).order_by(self.lookup_key)

        return active_ids


class ResourceSynchronizer(Synchronizer):
    client_class = api.ResourcesAPIClient
    model_class = models.ResourceTracker
    last_updated_field = None

    related_meta = {
        'licenseType': (models.LicenseType, 'license_type'),
        'defaultServiceDeskRoleID': (models.Role, 'default_service_desk_role'),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client.add_condition(A(op='eq', field='isActive', value=True))

    def _assign_field_data(self, instance, object_data):
        instance.id = object_data['id']
        instance.user_name = object_data.get('userName')
        instance.email = object_data.get('email')
        instance.first_name = object_data.get('firstName')
        instance.last_name = object_data.get('lastName')
        instance.active = object_data.get('isActive')

        self.set_relations(instance, object_data)

        return instance


class AccountSynchronizer(Synchronizer):
    client_class = api.AccountsAPIClient
    model_class = models.AccountTracker

    related_meta = {
        'companyType': (models.AccountType, 'type'),
        'parentCompanyID': (models.Account, 'parent_account'),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client.add_condition(A(op='eq', field='isActive', value=True))

    def _assign_field_data(self, instance, object_data):
        instance.id = object_data['id']
        instance.name = object_data.get('companyName')
        instance.number = object_data.get('companyNumber')
        instance.active = object_data.get('isActive')
        instance.last_activity_date = object_data.get('lastActivityDate')

        self._set_datetime_attribute(instance, 'last_activity_date')

        self.set_relations(instance, object_data)

        return instance


class PhaseSynchronizer(Synchronizer):
    client_class = api.PhasesAPIClient
    model_class = models.PhaseTracker
    last_updated_field = 'lastActivityDateTime'

    related_meta = {
        'projectID': (models.Project, 'project'),
        'parentPhaseID': (models.Phase, 'parent_phase'),
    }

    def _assign_field_data(self, instance, object_data):

        instance.id = object_data['id']
        instance.title = object_data.get('title')
        instance.number = object_data.get('phaseNumber')
        instance.description = object_data.get('description')
        instance.start_date = object_data.get('startDate')
        instance.due_date = object_data.get('dueDate')
        instance.last_activity_date = object_data.get('lastActivityDateTime')

        estimated_hours = object_data.get('estimatedHours')
        instance.estimated_hours = Decimal(str(estimated_hours)) \
            if estimated_hours is not None else None

        self._set_datetime_attribute(instance, 'start_date')
        self._set_datetime_attribute(instance, 'due_date')
        self._set_datetime_attribute(instance, 'last_activity_date')

        self.set_relations(instance, object_data)

        return instance


class PicklistSynchronizer(Synchronizer):
    lookup_name = None
    lookup_key = 'value'
    last_updated_field = None

    def fetch_records(self, results):
        logger.info(
            'Fetching {} records'.format(
                self.model_class.__bases__[0].__name__)
        )
        api_return = self.get_page()
        fields = api_return.get("fields")
        page = None

        if fields:
            for field in fields:
                try:
                    if field.get("name") == self.lookup_name:
                        page = field["picklistValues"]
                        break
                except (AttributeError, NameError):
                    pass

        if page:
            self.persist_page(page, results)

        return results

    def _assign_field_data(self, instance, json_data):
        instance.id = int(json_data[self.lookup_key])
        instance.label = json_data.get('label')
        instance.is_default_value = json_data.get('isDefaultValue')
        instance.sort_order = json_data.get('sortOrder')
        instance.is_active = json_data.get('isActive')
        instance.is_system = json_data.get('isSystem')

        if hasattr(self, 'related_meta'):
            self.set_relations(instance, json_data)
        return instance


class NoteTypeSynchronizer(PicklistSynchronizer):
    # Ticket note types are including task note types, and there are other
    # note types currently not used. e.g. project note types
    client_class = api.NoteTypesAPIClient
    model_class = models.NoteTypeTracker
    lookup_name = 'noteType'


class LicenseTypeSynchronizer(PicklistSynchronizer):
    client_class = api.LicenseTypesAPIClient
    model_class = models.LicenseTypeTracker
    lookup_name = 'licenseType'


class UseTypeSynchronizer(PicklistSynchronizer):
    client_class = api.UseTypesAPIClient
    model_class = models.UseTypeTracker
    lookup_name = 'useType'


class TaskTypeLinkSynchronizer(PicklistSynchronizer):
    client_class = api.TaskTypeLinksAPIClient
    model_class = models.TaskTypeLinkTracker
    lookup_name = 'timeEntryType'


class AccountTypeSynchronizer(PicklistSynchronizer):
    client_class = api.AccountTypesAPIClient
    model_class = models.AccountTypeTracker
    lookup_name = 'companyType'


class DisplayColorSynchronizer(PicklistSynchronizer):
    client_class = api.TicketCategoryPicklistAPIClient
    model_class = models.DisplayColorTracker
    lookup_name = 'displayColorRgb'


class ServiceCallStatusSynchronizer(PicklistSynchronizer):
    client_class = api.ServiceCallStatusPicklistAPIClient
    model_class = models.ServiceCallStatusTracker
    lookup_name = 'status'


class TicketPicklistSynchronizer(PicklistSynchronizer):
    client_class = api.TicketPicklistAPIClient


class StatusSynchronizer(TicketPicklistSynchronizer):
    model_class = models.StatusTracker
    lookup_name = 'status'


class PrioritySynchronizer(TicketPicklistSynchronizer):
    model_class = models.PriorityTracker
    lookup_name = 'priority'


class QueueSynchronizer(TicketPicklistSynchronizer):
    model_class = models.QueueTracker
    lookup_name = 'queueID'


class SourceSynchronizer(TicketPicklistSynchronizer):
    model_class = models.SourceTracker
    lookup_name = 'source'


class IssueTypeSynchronizer(TicketPicklistSynchronizer):
    model_class = models.IssueTypeTracker
    lookup_name = 'issueType'


class SubIssueTypeSynchronizer(TicketPicklistSynchronizer):
    model_class = models.SubIssueTypeTracker
    lookup_name = 'subIssueType'

    related_meta = {
        'parentValue': (models.IssueType, 'parent_value'),
    }


class TicketTypeSynchronizer(TicketPicklistSynchronizer):
    model_class = models.TicketTypeTracker
    lookup_name = 'ticketType'


class TaskPicklistSynchronizer(PicklistSynchronizer):
    client_class = api.TaskPicklistAPIClient


class TaskCategorySynchronizer(TaskPicklistSynchronizer):
    model_class = models.TaskCategoryTracker
    lookup_name = 'taskCategoryID'


class ProjectPicklistSynchronizer(PicklistSynchronizer):
    client_class = api.ProjectPicklistAPIClient


class ProjectStatusSynchronizer(ProjectPicklistSynchronizer):
    model_class = models.ProjectStatusTracker
    lookup_name = 'status'


class ProjectTypeSynchronizer(ProjectPicklistSynchronizer):
    model_class = models.ProjectTypeTracker
    lookup_name = 'projectType'


###################################################################
# Dummy Synchronizers                                             #
###################################################################


class DummySynchronizer:
    # Use FIELDS to list fields we submit to create or update a record, used
    # as a kind of validation method and way to link the snake_case field
    # names to their camelCase api names
    FIELDS = {}

    def __init__(self):
        self.client = self.client_class()

    def get(self, parent=None, conditions=None):

        records = []
        next_url = None
        conditions = conditions or []

        while True:
            logger.info(
                'Fetching {} records'.format(self.record_name)
            )

            api_return = self._get_page(
                next_url, conditions, parent=parent)
            records += api_return.get("items")
            next_url = api_return.get("pageDetails").get("nextPageUrl")

            if not next_url:
                break

        inverted = {v: k for k, v in self.FIELDS.items()}
        formatted_records = []

        # Convert the results from camelCase back to snake_case
        for record in records:
            converted = {}
            for k, v in record.items():
                if inverted.get(k, None):
                    converted[inverted[k]] = v
            formatted_records.append(converted)

        return formatted_records

    def update(self, parent=None, **kwargs):
        raise NotImplementedError

    def create(self, parent=None, **kwargs):
        raise NotImplementedError

    def delete(self, parent=None, **kwargs):
        raise NotImplementedError

    def _get_page(self, next_url, conditions, parent=None):
        raise NotImplementedError

    def _format_record(self, **kwargs):
        # Convert records from snake_case to camelCase
        record = {}
        for key, value in kwargs.items():
            # Only consider fields of the record, discard anything else
            if key in self.FIELDS.keys():
                record[self.FIELDS[key]] = value

        return record


class TicketChecklistItemsSynchronizer(DummySynchronizer):
    FIELDS = {
        'id': 'id',
        'ticket': 'ticketID',
        'item_name': 'itemName',
        'important': 'isImportant',
        'completed': 'isCompleted',
        'position': 'position',
        'resource': 'completedByResourceID',
        'completed_time': 'completedDateTime',
    }
    client_class = api.TicketChecklistItemsAPIClient
    record_name = "TicketChecklistItems"

    # https://webservices2.autotask.net/atservicesrest/V1.0/Tickets/9980/ChecklistItems
    def update(self, parent=None, **kwargs):
        record = self._format_record(**kwargs)

        return self.client.update(parent, **record)

    def create(self, parent=None, **kwargs):
        record = self._format_record(**kwargs)

        return self.client.create(parent, **record)

    def delete(self, parent=None, **kwargs):
        return self.client.delete(parent, **kwargs)

    def sync(self):
        ticket_qs = models.Ticket.objects.all().order_by('id')

        for ticket in ticket_qs:
            self.sync_items(ticket)

    def sync_items(self, instance):
        tasks = self.get(parent=instance.id)
        instance.checklist_total = len(tasks)
        instance.checklist_completed = sum(task['completed'] for task in tasks)

        instance.save()

    def _get_page(self, next_url, conditions, parent=None):
        if parent:
            self.client.add_condition(
                A(op='eq', field='ticketID', value=parent))

        for condition in conditions:
            self.client.add_condition(condition)

        return self.client.get(next_url, conditions)
