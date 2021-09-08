from django.conf import settings


class DjautotaskSettings:
    force_batch_query_size = 215

    def get_settings(self):
        request_settings = {
            'timeout': 30.0,
            'batch_size': 50,
            'max_attempts': 3,
            'keep_completed_hours': 8,
            'batch_query_size': self.force_batch_query_size,
        }

        # service_call_task shows errors w/ the value of batch_query_size
        # larger than 215. The error: 404 - File or directory not found.</h2>
        # <h3>The resource you are looking for might have been removed,
        # had its name changed, or is temporarily unavailable.
        if hasattr(settings, 'DJAUTOTASK_CONF_CALLABLE'):
            request_settings.update(settings.DJAUTOTASK_CONF_CALLABLE())
            request_settings['batch_query_size'] = min(
                self.force_batch_query_size,
                request_settings.get('batch_query_size')
            )

        return request_settings
