from unittest.mock import Mock, patch

import pytest

from wifi_logger_visualizer.web_viewer import ViewerHandler


@pytest.mark.parametrize('error', [ConnectionResetError, BrokenPipeError])
def test_client_disconnect_during_response_is_ignored(error):
    handler = object.__new__(ViewerHandler)
    handler.path = '/'
    handler.send_response = Mock()
    handler.send_header = Mock()
    handler.end_headers = Mock()
    handler.wfile = Mock()
    handler.wfile.write.side_effect = error()
    handler.do_GET()
    handler.wfile.write.assert_called_once()


def test_unexpected_request_errors_are_not_hidden():
    handler = object.__new__(ViewerHandler)
    handler._handle_get = Mock(side_effect=RuntimeError('unexpected'))
    with pytest.raises(RuntimeError, match='unexpected'):
        handler.do_GET()


def test_favicon_does_not_open_database():
    handler = object.__new__(ViewerHandler)
    handler.path = '/favicon.ico'
    handler.send_response = Mock()
    handler.end_headers = Mock()
    with patch('wifi_logger_visualizer.web_viewer.DatabaseManager') as database:
        handler.do_GET()
    database.assert_not_called()
    handler.send_response.assert_called_once_with(204)
    handler.end_headers.assert_called_once()
