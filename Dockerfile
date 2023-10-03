# build python venv for inclusion into image
FROM python:3.11-slim-bookworm as APP
RUN apt-get update && apt-get install -y git python3-venv
WORKDIR /opt/swoop/api
RUN python3 -m venv --copies swoop-api-venv
COPY requirements.txt .
COPY swoop-config.yml .
RUN ./swoop-api-venv/bin/pip install -r requirements.txt
RUN --mount=source=.git,target=.git,type=bind git clone . clone
RUN ./swoop-api-venv/bin/pip install ./clone

FROM python:3.11-slim-bookworm

ENV SWOOP_CONFIG_FILE=swoop-config.yml

COPY --from=APP /opt/swoop/api/swoop-api-venv /opt/swoop/api/swoop-api-venv
COPY --from=APP /opt/swoop/api/$SWOOP_CONFIG_FILE /opt/swoop/api/swoop-api-venv
ENV PATH=/opt/swoop/api/swoop-api-venv/bin:$PATH

WORKDIR /opt/swoop/api/swoop-api-venv

ENTRYPOINT ["uvicorn", "swoop.api.main:app"]
