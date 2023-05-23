FROM debian:bookworm-20230522-slim

WORKDIR /app

COPY . /app

RUN apt-get update

RUN apt-get install -y gcc musl-dev python3-dev python3-pip

RUN python3 -m pip install --break-system-packages --upgrade pip && \
    pip install  --break-system-packages -r requirements.txt && \
    pip install  --break-system-packages '.[dev]'

ENV SWOOP_ACCESS_KEY_ID=$SWOOP_ACCESS_KEY_ID  \
    SWOOP_SECRET_ACCESS_KEY=$SWOOP_ACCESS_KEY_ID  \
    SWOOP_S3_ENDPOINT=$SWOOP_S3_ENDPOINT  \
    SWOOP_BUCKET_NAME=$SWOOP_BUCKET_NAME  \
    SWOOP_EXECUTION_DIR=$SWOOP_EXECUTION_DIR  \
    SWOOP_WORKFLOW_CONFIG_FILE=$SWOOP_WORKFLOW_CONFIG_FILE \
    PGDATABASE=$PGDATABASE \
    PGHOST=$PGHOST \
    PGUSER=$PGUSER

RUN env

CMD ["uvicorn", "swoop.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
