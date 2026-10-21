import json
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
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


def test_lambda_handler_logs_status_without_url(monkeypatch, capsys):
    monkeypatch.setenv("TARGET_URL", "https://example.com/?token=secret")
    with mock.patch("lambda_function.requests.get") as get:
        get.return_value.status_code = 503

        lambda_function.lambda_handler({}, None)

    out = capsys.readouterr().out
    assert "503" in out
    assert "secret" not in out


def test_lambda_handler_raises_timeout_when_target_does_not_respond(monkeypatch):
    # The kernel completes the TCP handshake via the backlog, but nobody ever
    # accepts the connection, so no response comes back. Closing the server
    # later resets the connection, so the test fails instead of hanging if
    # the timeout is ever lost.
    with socket.create_server(("127.0.0.1", 0)) as server:
        closer = threading.Timer(3, server.close)
        closer.start()
        port = server.getsockname()[1]
        monkeypatch.setenv("TARGET_URL", f"http://127.0.0.1:{port}/")
        monkeypatch.setattr(lambda_function, "TIMEOUT_SECONDS", 0.1)

        with pytest.raises(requests.exceptions.Timeout):
            lambda_function.lambda_handler({}, None)
        closer.cancel()


class RedirectHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(301)
            self.send_header("Location", "/moved")
        else:
            self.send_response(200)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def log_message(self, format, *args):
        pass


def test_lambda_handler_follows_redirects_and_returns_final_status(monkeypatch):
    with ThreadingHTTPServer(("127.0.0.1", 0), RedirectHandler) as server:
        threading.Thread(target=server.serve_forever, daemon=True).start()
        port = server.server_address[1]
        monkeypatch.setenv("TARGET_URL", f"http://127.0.0.1:{port}/")

        result = lambda_function.lambda_handler({}, None)

        server.shutdown()

    assert result["body"] == json.dumps({"result": 200})
