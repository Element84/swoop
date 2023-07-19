FROM debian:bookworm-slim

WORKDIR /app

COPY . /app

RUN apt-get update

RUN apt-get install -y gcc musl-dev python3-dev python3-pip

# Resolving libcurl4 vulnerability https://security-tracker.debian.org/tracker/CVE-2023-23914
# Resolving libcurl4 vulnerability https://security.snyk.io/vuln/SNYK-DEBIAN12-CURL-5561883
RUN apt-get install -y libcurl4>=7.88.1-10 curl>=7.88.1-10

# Resolving libcap2 vulnerability https://security.snyk.io/vuln/SNYK-DEBIAN12-LIBCAP2-5537069
RUN apt-get install -y libcap2>=1:2.66-4

# Resolving libwebp7 vulnerability https://security.snyk.io/vuln/SNYK-DEBIAN12-LIBWEBP-5489176
RUN apt-get install -y libwebp7>=1.2.4-0.2

# Resolving libx11-data vulnerability https://security.snyk.io/vuln/SNYK-DEBIAN12-LIBX11-5710892
RUN apt-get install -y libx11-data>=2:1.8.4-2+deb12u1

# Resolving libssl3 vulnerability https://security.snyk.io/vuln/SNYK-DEBIAN12-OPENSSL-5661565
# Resolving libssl3 vulnerability https://security.snyk.io/vuln/SNYK-DEBIAN12-OPENSSL-3368733
RUN apt-get install -y libssl3>=3.0.9-1

# Resolving libaom vulnerabilities:
#  - https://security-tracker.debian.org/tracker/CVE-2021-30473
#  - https://security-tracker.debian.org/tracker/CVE-2021-30474
#  - https://security-tracker.debian.org/tracker/CVE-2021-30475
RUN apt-get install -y libaom-dev>=3.6.0-1

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
