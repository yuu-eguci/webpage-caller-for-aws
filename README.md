webpage-caller-for-aws
===

This repository does only call a web page which is specified with environment variable, from AWS lambda.

- Docker: 対応!
- Python: 3.14!
- Linter: ruff!
- Test: pytest!
- requests: 2.34!

## パッと実行してみたい

```bash
docker compose up --build -d
curl -s -X POST http://localhost:9000/2015-03-31/functions/function/invocations -d '{}'
# => {"statusCode": 200, "body": "{\"result\": 200}"}
docker compose down
```

呼び出し先は環境変数 `TARGET_URL` で指定します。省略時は `https://example.com/` です。

```bash
TARGET_URL=https://example.org/ docker compose up --build -d
```

呼び出し先が 10 秒以内に応答しないときは `requests.exceptions.Timeout` 系の例外でエラーになります。

呼び出し先のステータスコードはログにも出します。CloudWatch Events から定期実行するときは戻り値がどこにも残らないので、結果は CloudWatch Logs で見てください。
URL はトークン入りのこともあるのでログには出しません。ただ、接続エラーやタイムアウトのときの例外メッセージには URL が含まれます。

Lambda の Runtime Interface Emulator 入りの公式ベースイメージで動かしているので、ローカルでも Lambda と同じ形で invoke できます。

## テストと lint

```bash
docker compose run --rm dev pytest
docker compose run --rm dev ruff check .
docker compose run --rm dev ruff format --check .
```

ローカルに Python 3.14 と pipenv があるなら、`pipenv install --dev` してから `pipenv run pytest` とかでも OK です。

テストは requests をモックするか、ローカルのソケットに投げるだけなので、外には通信しません。
GitHub Actions でも同じコマンドと、Docker イメージのビルド + RIE への invoke を回しています。

## Lambda にアップロードする zip を作る

```bash
docker build --target package --output type=local,dest=dist .
# => dist/project.zip
```

Lambda 側の設定はこんな感じです。

- Runtime: Python 3.14
- Handler: `lambda_function.lambda_handler`
- 環境変数: `TARGET_URL`
- Timeout: 10 秒より長めに (デフォルトの 3 秒のままだと、呼び出し先が遅いとき先に Lambda 側が落ちます)

![](media/media.png)
