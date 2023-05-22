FROM alpine:3.18.0

WORKDIR /app

COPY . /app

RUN apk add --no-cache gcc build-base musl-dev python3-dev py3-pip

RUN python3 -m pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install '.[dev]'

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
