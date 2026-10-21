import json
from unittest import mock

import lambda_function


def test_lambda_handler_calls_target_url_and_returns_its_status(monkeypatch):
    monkeypatch.setenv("TARGET_URL", "https://example.com/")
    with mock.patch("lambda_function.requests.get") as get:
        get.return_value.status_code = 404

        result = lambda_function.lambda_handler({}, None)

    assert get.call_args.args == ("https://example.com/",)
    assert result == {"statusCode": 200, "body": json.dumps({"result": 404})}
