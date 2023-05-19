class SwoopApiException(Exception):
    pass


class WorkflowConfigError(SwoopApiException, ValueError):
    pass
