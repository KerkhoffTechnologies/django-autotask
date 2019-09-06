from mock import patch


def create_mock_call(method_name, return_value, side_effect=None):
    """Utility function for mocking the specified function or method"""
    _patch = patch(method_name, side_effect=side_effect)
    mock_get_call = _patch.start()

    if not side_effect:
        mock_get_call.return_value = return_value

    return mock_get_call, _patch


def init_api_connection(return_value):
    method_name = 'djautotask.sync.Synchronizer.init_api_connection'

    return create_mock_call(method_name, return_value)


def service_ticket_api_call(return_value):
    method_name = 'atws.wrapper.Wrapper.query'

    return create_mock_call(method_name, return_value)
