import base64
import logging
import re

from django.conf import settings

logger = logging.getLogger(__name__)

AT_DATA_TYPE_MAP = {
    'string': 'string',
    'double': 'number',
    'datetime': 'datetime',
}


class DjautotaskSettings:

    def get_settings(self):
        request_settings = {
            'timeout': 30.0,
            'batch_size': 50,
            'max_attempts': 3,
            'keep_completed_hours': 8,
            'batch_query_size': 400,
            'queue_sync_filter': [],
            'mass_delete_protection': False,
        }

        if hasattr(settings, 'DJAUTOTASK_CONF_CALLABLE'):
            request_settings.update(settings.DJAUTOTASK_CONF_CALLABLE())

        return request_settings


def encode_file_to_base64(file_content):
    return base64.b64encode(file_content.read()).decode('utf-8')


def caption_to_snake_case(caption):
    """
    Convert a UDF caption/name to a snake_case key.
    Removes special characters, preserves numbers, collapses whitespace.
    e.g. "Hello 3 there?" -> "hello_3_there"
    """
    s = caption.lower()
    s = re.sub(r'[^a-z0-9\s]', '', s)
    s = re.sub(r'\s+', '_', s.strip())
    s = re.sub(r'_+', '_', s)
    return s.strip('_')


def parse_udf(udfs):
    """
    Convert a list of AT userDefinedFields dicts to the standardized format.
    All data comes from the API response — no DB lookups needed.
    """
    result = {}
    for item in udfs:
        name = item.get('name', '')
        snake_name = caption_to_snake_case(name)
        if not snake_name:
            # I should hope this would never happen, but ping it to
            # sentry if it does so we can handle it.
            logger.exception(
                f"UDF name stripped became empty string: {name}.")
            continue

        value = item.get('value')
        is_picklist = item.get('is_picklist', False)
        udf_type = item.get('type', '')

        # For picklists, AT's 'label' field is the resolved display value.
        # For non-picklists, label is the same as name, so use value instead.
        if is_picklist and value:
            display_value = item.get('label', value)
        else:
            display_value = value

        result[snake_name] = {
            'udf_type': udf_type,
            'data_type': AT_DATA_TYPE_MAP.get(udf_type, 'string'),
            'name': name,
            'value': value,
            'display_value': display_value,
            'is_list': is_picklist,
            'extra': {},
        }
    return result
