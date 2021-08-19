import logging

from suds.client import Client
from atws.wrapper import AutotaskProcessException, AutotaskAPIException
from atws import Query, helpers, picklist
from django.db import transaction, IntegrityError
from django.utils import timezone
from djautotask.utils import DjautotaskSettings

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
        ).order_by(self.db_lookup_key).values_list('id', flat=True)

        return set(ids)

    def _child_query_condition(self, query, query_params):
        parent_field, parent_id = query_params
        query.open_bracket('AND')
        query.WHERE(
            parent_field, query.Equals, parent_id)
        query.close_bracket()

        # Apply extra conditions if they exist, else nothing happens
        self._get_query_conditions(query)

    def _get_children(self, results, query_params):
        sync_job_qset = models.SyncJob.objects.filter(
            entity_name=self.model_class.__bases__[0].__name__)

        query = self.build_base_query(sync_job_qset)
        self._child_query_condition(query, query_params)

        logger.info('Fetching {} records.'.format(
            self.model_class.__bases__[0].__name__))
        self.fetch_records(query, results)

        return results

    def callback_sync(self, query_params):
        results = SyncResults()
        self.at_api_client = api.init_api_connection()

        # Set of IDs of all records prior
        # to sync, to find stale records for deletion.
        initial_ids = self._child_instance_ids(query_params)

        results = self._get_children(results, query_params)

        results.deleted_count = self.prune_stale_records(
            initial_ids,
            results.synced_ids
        )

        return results.created_count, results.updated_count, \
            results.skipped_count, results.deleted_count


class BatchQueryMixin:
    """
    Fetch records from the API only fetching records if the related model(s)
    are already in the database.
    """

    def __init__(self, *args, **kwargs):
        settings = DjautotaskSettings().get_settings()
        self.batch_size = settings.get('batch_query_size')
        super().__init__(*args, **kwargs)

    def build_batch_queries(self, sync_job_qset):
        raise NotImplementedError

    def get(self, results):

        sync_job_qset = models.SyncJob.objects.filter(
            entity_name=self.model_class.__bases__[0].__name__
        )
        object_queries = self.build_batch_queries(sync_job_qset)

        logger.info(
            'Fetching {} records.'.format(self.model_class)
        )
        for query in object_queries:
            # Apply extra conditions if they exist, and then run the query.
            self._get_query_conditions(query)
            self.fetch_records(query, results)

        return results

    def _build_fk_batch(self, model_class, object_id_fields, sync_job_qset):
        """
        Generic batching method for batching based off of the fk relation of
        an object currently present in the local DB.
        """
        queries = []
        object_ids = list(model_class.objects.order_by(self.db_lookup_key)
                          .values_list('id', flat=True))

        while object_ids:
            query = self.build_base_query(sync_job_qset)
            query.open_bracket('AND')

            batch_size = self.get_batch_size()
            batch = object_ids[:batch_size]
            del object_ids[:batch_size]

            self._set_or_conditions(batch, object_id_fields, query)

            query.close_bracket()
            queries.append(query)

        return queries

    def get_batch_size(self):
        return self.batch_size

    def _set_or_conditions(self, batch, object_id_field, query):
        # Create queries from batches of records
        for object_id in batch:
            query.OR(object_id_field, query.Equals, object_id)


class TicketPicklistSynchronizer(PicklistSynchronizer):
    entity_type = 'Ticket'


class SubIssueTypeSynchronizer(TicketPicklistSynchronizer):
    model_class = models.SubIssueTypeTracker
    picklist_field = 'SubIssueType'

    related_meta = {
        'parentValue': (models.IssueType, 'parent_value'),
    }

    def _assign_field_data(self, instance, object_data):

        self.set_relations(instance, object_data)
        super()._assign_field_data(instance, object_data)

        return instance


class TicketTypeSynchronizer(TicketPicklistSynchronizer):
    model_class = models.TicketTypeTracker
    picklist_field = 'TicketType'


class ProjectStatusSynchronizer(PicklistSynchronizer):
    model_class = models.ProjectStatusTracker
    entity_type = 'Project'
    picklist_field = 'Status'


class ProjectTypeSynchronizer(PicklistSynchronizer):
    model_class = models.ProjectTypeTracker
    entity_type = 'Project'
    picklist_field = 'Type'


class NoteTypeSynchronizer(PicklistSynchronizer):
    # We are using ticket note to get the picklist, but like Ticket Status
    # and Task Status both use one status type, so do Ticket and Task notes
    model_class = models.NoteTypeTracker
    entity_type = 'TicketNote'
    picklist_field = 'NoteType'


class ServiceCallStatusSynchronizer(PicklistSynchronizer):
    model_class = models.ServiceCallStatusTracker
    entity_type = 'ServiceCall'
    picklist_field = 'Status'


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


class TicketCategorySynchronizer(Synchronizer):
    model_class = models.TicketCategoryTracker
    last_updated_field = None

    related_meta = {
        'DisplayColorRGB': (models.DisplayColor, 'display_color')
    }

    def _assign_field_data(self, instance, object_data):
        instance.id = object_data['id']
        instance.name = object_data.get('Name')
        instance.active = object_data.get('Active')

        self.set_relations(instance, object_data)

        return instance


class SecondaryResourceSyncronizer(Synchronizer):
    def create(self, resource, role, entity):
        """
        Make a request to Autotask to create a SecondaryResource.
        """

        body = {
            'ResourceID': resource,
            'RoleID': role,
            self.id_type: entity
        }
        instance = api.create_object(self.model_name, body)

        return self.update_or_create_instance(instance)

    def delete(self, instances):
        """
        Takes a queryset of instances and deletes them from the remote
        Autotask instance and the local database.
        """

        api.delete_objects(self.model_name, instances)

        instances.delete()


class TicketSecondaryResourceSynchronizer(
        SecondaryResourceSyncronizer, ChildSynchronizer):
    last_updated_field = None
    model_class = models.TicketSecondaryResourceTracker
    model_name = 'TicketSecondaryResource'
    id_type = 'TicketID'

    related_meta = {
        'ResourceID': (models.Resource, 'resource'),
        'TicketID': (models.Ticket, 'ticket'),
        'RoleID': (models.Role, 'role'),
    }

    def _assign_field_data(self, instance, object_data):
        instance.id = object_data['id']
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


class AccountPhysicalLocationSynchronizer(BatchQueryMixin, Synchronizer):
    model_class = models.AccountPhysicalLocationTracker

    related_meta = {
        'AccountID': (models.Account, 'account'),
    }

    def _assign_field_data(self, instance, object_data):
        instance.id = object_data['id']
        instance.name = object_data.get('Name')
        instance.active = object_data.get('Active')
        instance.primary = object_data.get('Primary')
        self.set_relations(instance, object_data)

        return instance

    def build_batch_queries(self, sync_job_qset):
        batch_query_list = self._build_fk_batch(
            models.Account, 'AccountID', sync_job_qset)

        return batch_query_list


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


class TaskSecondaryResourceSynchronizer(SecondaryResourceSyncronizer):
    last_updated_field = None
    model_class = models.TaskSecondaryResourceTracker
    model_name = 'TaskSecondaryResource'
    id_type = 'TaskID'

    related_meta = {
        'ResourceID': (models.Resource, 'resource'),
        'TaskID': (models.Task, 'task'),
        'RoleID': (models.Role, 'role'),
    }

    def _assign_field_data(self, instance, object_data):
        instance.id = object_data['id']

        self.set_relations(instance, object_data)

        return instance


class NoteSynchronizer(Synchronizer):
    def _assign_field_data(self, instance, object_data):

        instance.id = object_data['id']
        instance.title = object_data.get('Title')
        instance.description = object_data.get('Description')
        instance.create_date_time = object_data.get('CreateDateTime')
        instance.last_activity_date = object_data.get('LastActivityDate')

        if instance.description:
            # Autotask docs say the max description length is 3200
            # characters but we've seen descriptions that are longer than that.
            # So truncate the field to 3200 characters just in case.
            instance.description = instance.description[:3200]

        self.set_relations(instance, object_data)

        return instance

    def _get_query_conditions(self, query):
        query.open_bracket('AND')
        query.WHERE(
            'NoteType',
            query.NotEqual,
            models.NoteType.WORKFLOW_RULE_NOTE_ID
        )
        query.close_bracket()
        return query

    def create(self, **kwargs):
        """
        Make a request to Autotask to create a Note.
        """

        description = "{}\n\nNote was added by {} {}.".format(
            kwargs['description'],
            kwargs['resource'].first_name,
            kwargs['resource'].last_name
        )

        body = {
            'Title': kwargs['title'],
            'Description': description,
            'NoteType': kwargs['note_type'],
            'Publish': kwargs['publish'],
            self.related_model_field: kwargs['object_id'],
        }
        instance = api.create_object(self.model_name, body)

        return self.update_or_create_instance(instance)


class TicketNoteSynchronizer(
        BatchQueryMixin, NoteSynchronizer, ChildSynchronizer):

    model_class = models.TicketNoteTracker
    last_updated_field = 'LastActivityDate'
    related_model_field = 'TicketID'
    model_name = 'TicketNote'

    related_meta = {
        'NoteType': (models.NoteType, 'note_type'),
        'CreatorResourceID': (models.Resource, 'creator_resource'),
        'TicketID': (models.Ticket, 'ticket'),
    }

    def build_batch_queries(self, sync_job_qset):
        batch_query_list = self._build_fk_batch(
            models.Ticket, 'TicketID', sync_job_qset)

        return batch_query_list


class TaskNoteSynchronizer(
        BatchQueryMixin, NoteSynchronizer):

    model_class = models.TaskNoteTracker
    last_updated_field = 'LastActivityDate'
    related_model_field = 'TaskID'
    model_name = 'TaskNote'

    related_meta = {
        'NoteType': (models.NoteType, 'note_type'),
        'CreatorResourceID': (models.Resource, 'creator_resource'),
        'TaskID': (models.Task, 'task'),
    }

    def build_batch_queries(self, sync_job_qset):
        batch_query_list = self._build_fk_batch(
            models.Task, 'TaskID', sync_job_qset)

        return batch_query_list


class TimeEntrySynchronizer(BatchQueryMixin, Synchronizer, ChildSynchronizer):
    model_class = models.TimeEntryTracker
    last_updated_field = 'LastModifiedDateTime'

    related_meta = {
        'ResourceID': (models.Resource, 'resource'),
        'TicketID': (models.Ticket, 'ticket'),
        'TaskID': (models.Task, 'task'),
        'Type': (models.TaskTypeLink, 'type'),
        'AllocationCodeID': (models.AllocationCode, 'allocation_code'),
        'RoleID': (models.Role, 'role'),
        'ContractID': (models.Contract, 'contract'),
    }

    def _assign_field_data(self, instance, object_data):
        instance.id = object_data['id']
        instance.date_worked = object_data.get('DateWorked')
        instance.start_date_time = object_data.get('StartDateTime')
        instance.end_date_time = object_data.get('EndDateTime')
        instance.summary_notes = object_data.get('SummaryNotes')
        instance.internal_notes = object_data.get('InternalNotes')
        instance.non_billable = object_data.get('NonBillable')
        instance.hours_worked = object_data.get('HoursWorked')
        instance.hours_to_bill = object_data.get('HoursToBill')
        instance.offset_hours = object_data.get('OffsetHours')

        self.set_relations(instance, object_data)

        return instance

    def build_batch_queries(self, sync_job_qset):
        batch_query_list = []

        batch_query_list.extend(
            self._build_fk_batch(
                models.Ticket, 'TicketID', sync_job_qset))
        batch_query_list.extend(
            self._build_fk_batch(
                models.Task, 'TaskID', sync_job_qset))

        return batch_query_list

    def create_new_entry(self, entry_body):
        """
        Accepts a time entry dictionary which is then used to create a
        time entry Autotask object and created via the API.
        """
        instance = api.create_object('TimeEntry', entry_body)

        return self.update_or_create_instance(instance)


class AllocationCodeSynchronizer(Synchronizer):
    model_class = models.AllocationCodeTracker
    last_updated_field = None

    related_meta = {
        'UseType': (models.UseType, 'use_type')
    }

    def _assign_field_data(self, instance, object_data):
        instance.id = object_data['id']
        instance.name = object_data.get('Name')
        instance.description = object_data.get('Description')
        instance.active = object_data.get('Active')

        self.set_relations(instance, object_data)

        return instance


class ContractSynchronizer(Synchronizer):
    model_class = models.ContractTracker

    related_meta = {
        'AccountID': (models.Account, 'account')
    }

    def _assign_field_data(self, instance, object_data):
        instance.id = object_data['id']
        instance.name = object_data.get('ContractName')
        instance.number = object_data.get('ContractNumber')
        instance.status = str(object_data.get('Status'))

        self.set_relations(instance, object_data)

        return instance


class ServiceCallSynchronizer(BatchQueryMixin, Synchronizer):
    model_class = models.ServiceCallTracker
    last_updated_field = 'LastModifiedDateTime'

    related_meta = {
        'AccountID': (models.Account, 'account'),
        'AccountPhysicalLocationID':
            (models.AccountPhysicalLocation, 'location'),
        'Status': (models.ServiceCallStatus, 'status'),
        'CreatorResourceID': (models.Resource, 'creator_resource'),
        'CanceledByResource': (models.Resource, 'canceled_by_resource')
    }

    def _assign_field_data(self, instance, object_data):
        instance.id = object_data['id']
        instance.description = object_data.get('Description')
        instance.duration = object_data.get('Duration')
        instance.complete = object_data.get('Complete')
        instance.create_date_time = object_data.get('CreateDateTime')
        instance.start_date_time = object_data.get('StartDateTime')
        instance.end_date_time = object_data.get('EndDateTime')
        instance.canceled_date_time = object_data.get('CanceledDateTime')
        instance.last_modified_date_time = \
            object_data.get('LastModifiedDateTime')

        self.set_relations(instance, object_data)

        return instance

    def build_batch_queries(self, sync_job_qset):
        batch_query_list = self._build_fk_batch(
            models.Account, 'AccountID', sync_job_qset)

        return batch_query_list

    def create(self, **kwargs):
        """
        Make a request to Autotask to create a ServiceCall.
        """

        body = {
            'AccountID': kwargs['account'].id,
            'AccountPhysicalLocationID': kwargs['location'].id,
            'StartDateTime': kwargs['start_date_time'],
            'EndDateTime': kwargs['end_date_time'],
            'Status': kwargs['status'].id,
            'Description': kwargs['description'],
            'Duration': kwargs['duration'],
        }
        instance = api.create_object(
            self.model_class.__bases__[0].__name__, body)

        return self.update_or_create_instance(instance)


class ServiceCallTicketSynchronizer(BatchQueryMixin, Synchronizer):
    model_class = models.ServiceCallTicketTracker

    related_meta = {
        'ServiceCallID': (models.ServiceCall, 'service_call'),
        'TicketID': (models.Ticket, 'ticket')
    }

    def _assign_field_data(self, instance, object_data):
        instance.id = object_data['id']
        self.set_relations(instance, object_data)

        return instance

    def build_batch_queries(self, sync_job_qset):
        batch_query_list = self._build_fk_batch(
            models.Ticket, 'TicketID', sync_job_qset)

        return batch_query_list

    def create(self, **kwargs):
        """
        Make a request to Autotask to create a ServiceCallTicket.
        """

        body = {
            'ServiceCallID': kwargs['service_call'].id,
            'TicketID': kwargs['ticket'].id,
        }
        instance = api.create_object(
            self.model_class.__bases__[0].__name__, body)

        return self.update_or_create_instance(instance)


class ServiceCallTaskSynchronizer(BatchQueryMixin, Synchronizer):
    model_class = models.ServiceCallTaskTracker

    related_meta = {
        'ServiceCallID': (models.ServiceCall, 'service_call'),
        'TaskID': (models.Task, 'task')
    }

    def _assign_field_data(self, instance, object_data):
        instance.id = object_data['id']
        self.set_relations(instance, object_data)

        return instance

    def build_batch_queries(self, sync_job_qset):
        batch_query_list = self._build_fk_batch(
            models.Task, 'TaskID', sync_job_qset)

        return batch_query_list

    def create(self, **kwargs):
        """
        Make a request to Autotask to create a ServiceCallTask.
        """

        body = {
            'ServiceCallID': kwargs['service_call'].id,
            'TaskID': kwargs['task'].id,
        }
        instance = api.create_object(
            self.model_class.__bases__[0].__name__, body)

        return self.update_or_create_instance(instance)


class ServiceCallTicketResourceSynchronizer(BatchQueryMixin, Synchronizer):
    model_class = models.ServiceCallTicketResourceTracker

    related_meta = {
        'ServiceCallTicketID':
            (models.ServiceCallTicket, 'service_call_ticket'),
        'ResourceID': (models.Resource, 'resource')
    }

    def _assign_field_data(self, instance, object_data):
        instance.id = object_data['id']
        self.set_relations(instance, object_data)

        return instance

    def build_batch_queries(self, sync_job_qset):
        batch_query_list = self._build_fk_batch(
            models.ServiceCallTicket, 'ServiceCallTicketID', sync_job_qset)

        return batch_query_list

    def create(self, **kwargs):
        """
        Make a request to Autotask to create a ServiceCallTicketResource.
        """

        body = {
            'ServiceCallTicketID': kwargs['service_call_ticket'].id,
            'ResourceID': kwargs['resource'].id,
        }
        instance = api.create_object(
            self.model_class.__bases__[0].__name__, body)

        return self.update_or_create_instance(instance)


class ServiceCallTaskResourceSynchronizer(BatchQueryMixin, Synchronizer):
    model_class = models.ServiceCallTaskResourceTracker

    related_meta = {
        'ServiceCallTaskID':
            (models.ServiceCallTask, 'service_call_task'),
        'ResourceID': (models.Resource, 'resource')
    }

    def _assign_field_data(self, instance, object_data):
        instance.id = object_data['id']
        self.set_relations(instance, object_data)

        return instance

    def build_batch_queries(self, sync_job_qset):
        batch_query_list = self._build_fk_batch(
            models.ServiceCallTask, 'ServiceCallTaskID', sync_job_qset)

        return batch_query_list

    def create(self, **kwargs):
        """
        Make a request to Autotask to create a ServiceCallTaskResource.
        """

        body = {
            'ServiceCallTaskID': kwargs['service_call_task'].id,
            'ResourceID': kwargs['resource'].id,
        }
        instance = api.create_object(
            self.model_class.__bases__[0].__name__, body)

        return self.update_or_create_instance(instance)


class TaskPredecessorSynchronizer(BatchQueryMixin, Synchronizer):
    model_class = models.TaskPredecessorTracker

    related_meta = {
        'PredecessorTaskID': (models.Task, 'predecessor_task'),
        'SuccessorTaskID': (models.Task, 'successor_task'),
    }

    def build_batch_queries(self, sync_job_qset):
        object_id_fields = ['PredecessorTaskID', 'SuccessorTaskID']

        batch_query_list = self._build_fk_batch(
            models.Task, object_id_fields, sync_job_qset)

        return batch_query_list

    def get_batch_size(self):
        # We limit the amount of query conditions on each query to 400
        # by default. Autotask says they won't support any more than
        # 500 conditions but we've observed queries fail with 470
        # conditions. Since we are applying two OR conditions we need
        # to half the size of our regular batch size that only applies
        # one OR condition.
        return int(self.batch_size / 2)

    def _set_or_conditions(self, batch, object_id_fields, query):
        # Create queries from batches of records
        for object_id in batch:
            query.OR(object_id_fields[0], query.Equals, object_id)
            query.OR(object_id_fields[1], query.Equals, object_id)

    def _assign_field_data(self, instance, object_data):
        instance.id = object_data['id']
        instance.lag_days = object_data.get('LagDays')

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
