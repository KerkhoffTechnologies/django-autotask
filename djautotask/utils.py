from django.conf import settings


class DjautotaskSettings:

    def get_settings(self):
        request_settings = {
            'timeout': 30.0,
            'batch_size': 50,
            'max_attempts': 3,
            'keep_completed_hours': 8,
            'batch_query_size': 400,
        }

        if hasattr(settings, 'DJAUTOTASK_CONF_CALLABLE'):
            request_settings.update(settings.DJAUTOTASK_CONF_CALLABLE())

        return request_settings
