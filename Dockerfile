FROM public.ecr.aws/lambda/python:3.14 AS deps
COPY Pipfile Pipfile.lock ./
RUN pip install --no-cache-dir pipenv \
    && pipenv requirements --hash > /tmp/requirements.txt \
    && pip install --no-cache-dir --require-hashes -r /tmp/requirements.txt --target /opt/deps

FROM deps AS zipper
COPY lambda_function.py /opt/deps/
RUN cd /opt/deps && python -m zipfile -c /tmp/project.zip *

FROM scratch AS package
COPY --from=zipper /tmp/project.zip /

FROM public.ecr.aws/lambda/python:3.14 AS app
COPY --from=deps /opt/deps ${LAMBDA_TASK_ROOT}
COPY lambda_function.py ${LAMBDA_TASK_ROOT}
CMD ["lambda_function.lambda_handler"]
