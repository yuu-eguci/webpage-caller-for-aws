import json
import requests


def lambda_handler(event, context):
    # TODO: Specify access url with environment variable.
    res = requests.get('')
    return {
        'statusCode': 200,
        'body': json.dumps({
            'result': res.status_code,
        }),
    }


if __name__ == '__main__':
    print(lambda_handler(None, None))
