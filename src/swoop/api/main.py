from fastapi import FastAPI

from swoop.api.app import get_app

app: FastAPI = get_app()
