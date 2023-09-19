from fastapi import HTTPException as FAPIHttpException
from fastapi.responses import JSONResponse


class SwoopApiException(Exception):
    pass


class WorkflowConfigError(SwoopApiException, ValueError):
    pass


class HTTPException(SwoopApiException, FAPIHttpException):
    def __init__(
        self,
        status_code: int,
        type: str | None = None,
        title: str | None = None,
        instance: str | None = None,
        **kwargs,
    ) -> None:
        super().__init__(status_code, **kwargs)
        self.type = type
        self.title = title
        self.instance = instance

    def to_json(self) -> JSONResponse:
        content = {
            "status": self.status_code,
            "detail": self.detail,
        }

        if self.type is not None:
            content["type"] = self.type

        if self.title is not None:
            content["title"] = self.title

        if self.instance is not None:
            content["instance"] = self.instance

        return JSONResponse(
            status_code=self.status_code,
            content=content,
        )
