# build python venv for inclusion into image
FROM python:slim-bookworm as APP
RUN apt-get update && apt-get install -y git python3-venv
WORKDIR /opt/swoop/api
RUN python3 -m venv --copies swoop-api-venv
COPY requirements.txt .
COPY workflow-config.yml .
RUN ./swoop-api-venv/bin/pip install -r requirements.txt
RUN --mount=source=.git,target=.git,type=bind git clone . clone
RUN ./swoop-api-venv/bin/pip install ./clone

FROM python:slim-bookworm

ENV SWOOP_ACCESS_KEY_ID=$SWOOP_ACCESS_KEY_ID  \
    SWOOP_SECRET_ACCESS_KEY=$SWOOP_ACCESS_KEY_ID  \
    SWOOP_S3_ENDPOINT=$SWOOP_S3_ENDPOINT  \
    SWOOP_BUCKET_NAME=$SWOOP_BUCKET_NAME  \
    SWOOP_EXECUTION_DIR=$SWOOP_EXECUTION_DIR  \
    SWOOP_WORKFLOW_CONFIG_FILE=$SWOOP_WORKFLOW_CONFIG_FILE \
    PGDATABASE=$PGDATABASE \
    PGHOST=$PGHOST \
    PGUSER=$PGUSER

COPY --from=APP /opt/swoop/api/swoop-api-venv /opt/swoop/api/swoop-api-venv
COPY --from=APP /opt/swoop/api/$SWOOP_WORKFLOW_CONFIG_FILE /opt/swoop/api/swoop-api-venv
ENV PATH=/opt/swoop/api/swoop-api-venv/bin:$PATH

RUN env

WORKDIR /opt/swoop/api/swoop-api-venv

CMD ["uvicorn", "swoop.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
