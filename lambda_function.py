import json
import os

import requests

TIMEOUT_SECONDS = 10


def lambda_handler(event, context):
    res = requests.get(os.environ["TARGET_URL"], timeout=TIMEOUT_SECONDS)
    print(f"TARGET_URL responded with {res.status_code}")
    return {
        "statusCode": 200,
        "body": json.dumps({"result": res.status_code}),
    }


if __name__ == "__main__":
    print(lambda_handler(None, None))
