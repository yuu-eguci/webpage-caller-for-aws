import json
import socket
from unittest import mock

import pytest
import requests

import lambda_function


def test_lambda_handler_calls_target_url_and_returns_its_status(monkeypatch):
    monkeypatch.setenv("TARGET_URL", "https://example.com/")
    with mock.patch("lambda_function.requests.get") as get:
        get.return_value.status_code = 404

        result = lambda_function.lambda_handler({}, None)

    assert get.call_args.args == ("https://example.com/",)
    assert result == {"statusCode": 200, "body": json.dumps({"result": 404})}


def test_lambda_handler_raises_timeout_when_target_does_not_respond(monkeypatch):
    # The kernel completes the TCP handshake via the backlog, but nobody ever
    # accepts the connection, so no response comes back.
    with socket.create_server(("127.0.0.1", 0)) as server:
        port = server.getsockname()[1]
        monkeypatch.setenv("TARGET_URL", f"http://127.0.0.1:{port}/")
        monkeypatch.setattr(lambda_function, "TIMEOUT_SECONDS", 0.1)

        with pytest.raises(requests.exceptions.Timeout):
            lambda_function.lambda_handler({}, None)
