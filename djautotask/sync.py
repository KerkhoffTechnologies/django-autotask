import logging

from suds.client import Client
from atws.connection import ATWSAuthException
from atws.wrapper import AutotaskProcessException, AutotaskAPIException
from atws import Query, helpers, picklist
from django.db import transaction, IntegrityError
from django.utils import timezone

from djautotask import api, models

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
        except AutotaskProcessException as e:
            sync_job.message = api.parse_autotaskprocessexception(e)
            sync_job.success = False
            raise
        except AutotaskAPIException as e:
            sync_job.message = api.parse_autotaskapiexception(e)
            sync_job.success = False
            raise
        except ATWSAuthException as e:
            sync_job.message = e
            sync_job.success = False
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


class Synchronizer:
    lookup_key = 'id'
    db_lookup_key = lookup_key
    last_updated_field = None

    def __init__(self, full=False, *args, **kwargs):
        self.full = full
        self.at_api_client = None

    def set_relations(self, instance, object_data):
        for object_field, value in self.related_meta.items():
            model_class, field_name = value
            self._assign_relation(
                instance,
                object_data,
                object_field,
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

    def get_record_id(self, record):
        return int(record[self.lookup_key])

    def _assign_relation(self, instance, object_data,
                         object_field, model_class, field_name):

        relation_id = object_data.get(object_field)
        if relation_id is None:
            self._assign_null_relation(instance, field_name)
            return

        try:
            related_instance = model_class.objects.get(pk=relation_id)
            setattr(instance, field_name, related_instance)
        except model_class.DoesNotExist:
            logger.warning(
                'Failed to find {} {} for {} {}.'.format(
                    object_field, relation_id, type(instance), instance.id
                )
            )

    def _instance_ids(self, filter_params=None):
        if not filter_params:
            ids = self.model_class.objects.all().order_by(self.db_lookup_key)\
                .values_list('id', flat=True)
        else:
            ids = self.model_class.objects.filter(filter_params)\
                .order_by(self.db_lookup_key)\
                .values_list('id', flat=True)
        return set(ids)

    def build_base_query(self, sync_job_qset):
        query = Query(self.model_class.__bases__[0].__name__)

        # Since the job is created before it begins, make sure to exclude
        # itself, and at least one other sync job exists.
        if sync_job_qset.count() > 1 and self.last_updated_field \
                and not self.full:

            last_sync_job_time = sync_job_qset.exclude(
                id=sync_job_qset.last().id).last().start_time
            query.WHERE(self.last_updated_field,
                        query.GreaterThanorEquals, last_sync_job_time)
        else:
            query.WHERE('id', query.GreaterThanorEquals, 0)

        return query

    def get(self, results):
        """
        Fetch records from the API. ATWS automatically makes multiple separate
        queries if the request is over 500 records.
        """
        sync_job_qset = models.SyncJob.objects.filter(
            entity_name=self.model_class.__bases__[0].__name__
        )
        query = self.build_base_query(sync_job_qset)

        # Apply extra conditions if they exist, else nothing happens
        self._get_query_conditions(query)

        logger.info(
            'Fetching {} records.'.format(
                self.model_class.__bases__[0].__name__)
        )
        self.fetch_records(query, results)

        return results

    def fetch_records(self, query, results):
        for record in self.at_api_client.query(query):
            self.persist_record(record, results)

    def persist_record(self, record, results):
        """Persist each record to the DB."""
        try:
            with transaction.atomic():
                instance, result = self.update_or_create_instance(record)
            if result == CREATED:
                results.created_count += 1
            elif result == UPDATED:
                results.updated_count += 1
            else:
                results.skipped_count += 1

            results.synced_ids.add(instance.id)
        except InvalidObjectException as e:
            record_id = self.get_record_id(record)
            # If record ID exists in db, don't delete the stale record we have
            # on InvalidObjectException
            if record_id:
                results.synced_ids.add(record_id)
            logger.warning('{}'.format(e))

        return results

    def update_or_create_instance(self, record):
        """Creates and returns an instance if it does not already exist."""
        result = None
        api_instance = Client.dict(record)

        try:
            instance_pk = api_instance[self.lookup_key]
            instance = self.model_class.objects.get(
                **{
                    self.db_lookup_key: instance_pk
                }
            )
        except self.model_class.DoesNotExist:
            instance = self.model_class()
            result = CREATED

        try:
            self._assign_field_data(instance, api_instance)

            # This will return the created instance, the updated instance, or
            # if the instance is skipped an unsaved copy of the instance.
            if result == CREATED:
                if self.model_class is models.Ticket:
                    instance.save(force_insert=True)
                else:
                    instance.save()
            elif instance.tracker.changed():
                instance.save()
                result = UPDATED
            else:
                result = SKIPPED

        except IntegrityError as e:
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
        not seen as we iterated through all records from the API.
        """
        stale_ids = initial_ids - synced_ids
        deleted_count = 0
        if stale_ids:
            delete_qset = self.model_class.objects.filter(pk__in=stale_ids)
            deleted_count = delete_qset.count()

            logger.info(
                'Removing {} stale records for model: {}'.format(
                    len(stale_ids), self.model_class,
                )
            )
            delete_qset.delete()

        return deleted_count

    @log_sync_job
    def sync(self):
        results = SyncResults()
        self.at_api_client = api.init_api_connection()

        # Set of IDs of all records prior
        # to sync, to find stale records for deletion.
        results = self.get(results)

        if self.full:
            initial_ids = self._instance_ids()
            results.deleted_count = self.prune_stale_records(
                initial_ids, results.synced_ids
            )

        return \
            results.created_count, results.updated_count, \
            results.skipped_count, results.deleted_count

    def _get_query_conditions(self, query):
        pass


class SyncRecordUDFMixin:

    def _assign_udf_data(self, instance, udfs):
        for item in udfs[0]:
            try:
                name = getattr(item, 'Name', None)
                value = getattr(item, 'Value', None)

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
                    'Multiple UDF records returned for 1 Name: {}'.format(e))
            except self.udf_class.DoesNotExist as e:
                # Can happen if sync not 100% up to date, debug log and
                # continue
                logger.debug(
                    'No UDF records returned for Name: {}'.format(e))
            except KeyError as e:
                # UDF has likely been updated but we don't have the
                # updated changes locally until the UDF class has been synced.
                logger.warning(
                    'KeyError when trying to access UDF '
                    'picklist label. {}'.format(e)
                )


class UDFSynchronizer(Synchronizer):
    lookup_key = 'Name'
    db_lookup_key = lookup_key.lower()
    entity_type = None
    model_class = None

    def get_record_id(self, record):
        try:
            return self.model_class.objects.get(name=record["Name"]).id
        except self.model_class.DoesNotExist:
            return None

    @log_sync_job
    def sync(self):
        """
        Fetch udf for a record type from the API and persist in the database.
        """
        results = SyncResults()
        self.at_api_client = api.init_api_connection()

        udf_records = self.at_api_client.get_udf_info(self.entity_type)

        if udf_records:
            logger.info(
                'Fetching {} records.'.format(self.model_class)
            )
            for record in udf_records[0]:
                self.persist_record(record, results)

        if self.full:
            initial_ids = self._instance_ids()
            results.deleted_count = self.prune_stale_records(
                initial_ids, results.synced_ids
            )

        return results.created_count, results.updated_count, \
            results.skipped_count, results.deleted_count

    def _instance_ids(self, filter_params=None):
        ids = self.model_class.objects.all().order_by(self.db_lookup_key)\
            .values_list('id', flat=True)
        return set(ids)

    def _assign_field_data(self, instance, object_data):

        instance.name = object_data.get('Name')
        instance.label = object_data.get('Label')
        instance.type = object_data.get('Type')
        instance.is_picklist = object_data.get('IsPickList')

        if instance.is_picklist:
            # Clear picklist to eliminate stale items
            instance.picklist = {}
            for item in object_data.get('PicklistValues')[0]:
                instance.picklist[item.Value] = {
                    'label': item.Label,
                    'is_default_value': item.IsDefaultValue,
                    'sort_order': item.SortOrder,
                    'is_active': item.IsActive,
                    'is_system': item.IsSystem,
                }

        return instance


class PicklistSynchronizer(Synchronizer):
    lookup_key = 'Value'

    @log_sync_job
    def sync(self):
        """
        Fetch picklist for a field from the API and persist in the database.
        """
        results = SyncResults()
        picklist_objects = None
        self.at_api_client = api.init_api_connection()

        field_info = \
            helpers.get_field_info(self.at_api_client, self.entity_type)

        try:
            field_picklist = \
                picklist.get_field_picklist(self.picklist_field, field_info)
            picklist_objects = field_picklist.PicklistValues[0]

        except KeyError as e:
            logger.warning(
                'Failed to find {} picklist field. {}'.format(
                    self.picklist_field, e
                )
            )
        except IndexError as e:
            logger.warning(
                'Failed to find PicklistValues index at {}. {}'.format(
                    self.picklist_field, e
                )
            )

        if picklist_objects:
            logger.info(
                'Fetching {} records.'.format(self.model_class)
            )
            for record in picklist_objects:
                self.persist_record(record, results)

        if self.full:
            initial_ids = self._instance_ids()
            results.deleted_count = self.prune_stale_records(
                initial_ids, results.synced_ids
            )

        return results.created_count, results.updated_count, \
            results.skipped_count, results.deleted_count

    def _assign_field_data(self, instance, object_data):

        instance.id = int(object_data.get('Value'))
        instance.label = object_data.get('Label')
        instance.is_default_value = object_data.get('IsDefaultValue')
        instance.sort_order = object_data.get('SortOrder')
        instance.is_active = object_data.get('IsActive')
        instance.is_system = object_data.get('IsSystem')

        return instance


class TicketPicklistSynchronizer(PicklistSynchronizer):
    entity_type = 'Ticket'


class NoteTypeSynchronizer(PicklistSynchronizer):
    # We are using ticket note to get the picklist, but like Ticket Status
    # and Task Status both use one status type, so do Ticket and Task notes
    model_class = models.NoteTypeTracker
    entity_type = 'TicketNote'
    picklist_field = 'NoteType'


class ResourceSynchronizer(Synchronizer):
    model_class = models.ResourceTracker
    last_updated_field = None

    related_meta = {
        'LicenseType': (models.LicenseType, 'license_type'),
        'DefaultServiceDeskRoleID': (models.Role, 'default_service_desk_role'),
    }

    def _assign_field_data(self, instance, object_data):
        instance.id = object_data['id']
        instance.user_name = object_data.get('UserName')
        instance.email = object_data.get('Email')
        instance.first_name = object_data.get('FirstName')
        instance.last_name = object_data.get('LastName')
        instance.active = object_data.get('Active')

        self.set_relations(instance, object_data)

        return instance


class AccountSynchronizer(Synchronizer):
    model_class = models.AccountTracker
    last_updated_field = 'LastActivityDate'

    related_meta = {
        'AccountType': (models.AccountType, 'type'),
        'ParentAccountID': (models.Account, 'parent_account'),
    }

    def _assign_field_data(self, instance, object_data):
        instance.id = object_data['id']
        instance.name = object_data.get('AccountName')
        instance.number = object_data.get('AccountNumber')
        instance.active = object_data.get('Active')
        instance.last_activity_date = object_data.get('LastActivityDate')
        self.set_relations(instance, object_data)

        return instance


class PhaseSynchronizer(Synchronizer):
    model_class = models.PhaseTracker
    last_updated_field = 'LastActivityDateTime'

    related_meta = {
        'ProjectID': (models.Project, 'project'),
        'ParentPhaseID': (models.Phase, 'parent_phase'),
    }

    def _assign_field_data(self, instance, object_data):

        instance.id = object_data['id']
        instance.title = object_data.get('Title')
        instance.number = object_data.get('PhaseNumber')
        instance.description = object_data.get('Description')
        instance.start_date = object_data.get('StartDate')
        instance.due_date = object_data.get('DueDate')
        instance.estimated_hours = object_data.get('EstimatedHours')
        instance.last_activity_date = object_data.get('LastActivityDateTime')

        self.set_relations(instance, object_data)

        return instance


class TicketUDFSynchronizer(UDFSynchronizer):
    entity_type = 'Ticket'
    model_class = models.TicketUDFTracker


class TaskUDFSynchronizer(UDFSynchronizer):
    entity_type = 'Task'
    model_class = models.TaskUDFTracker


class ProjectUDFSynchronizer(UDFSynchronizer):
    entity_type = 'Project'
    model_class = models.ProjectUDFTracker
