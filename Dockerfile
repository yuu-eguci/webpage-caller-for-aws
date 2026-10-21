ARG PIPENV_VERSION=2026.10.1

FROM public.ecr.aws/lambda/python:3.14 AS deps
ARG PIPENV_VERSION
COPY Pipfile Pipfile.lock ./
RUN pip install --no-cache-dir pipenv==${PIPENV_VERSION} \
    && pipenv requirements --hash > /tmp/requirements.txt \
    && pip install --no-cache-dir --require-hashes -r /tmp/requirements.txt --target /opt/deps

FROM deps AS zipper
COPY lambda_function.py /opt/deps/
RUN cd /opt/deps && python -m zipfile -c /tmp/project.zip *

FROM scratch AS package
COPY --from=zipper /tmp/project.zip /

FROM python:3.14-slim AS dev
ARG PIPENV_VERSION
WORKDIR /app
COPY Pipfile Pipfile.lock ./
RUN pip install --no-cache-dir pipenv==${PIPENV_VERSION} \
    && pipenv install --dev --system --deploy

FROM public.ecr.aws/lambda/python:3.14 AS app
COPY --from=deps /opt/deps ${LAMBDA_TASK_ROOT}
COPY lambda_function.py ${LAMBDA_TASK_ROOT}
CMD ["lambda_function.lambda_handler"]
