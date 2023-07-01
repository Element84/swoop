import json
import uuid

WORKFLOW_UUIDv5_NAMESPACE = uuid.UUID(hex="2d1c93d5-111f-4385-8fbb-814a32105aab")


def generate_payload_uuid(workflow_name: str, payload: dict) -> uuid.UUID:
    """
    Hashes the values in the payload and the payload's workflow name into a UUIDv5.

    Parameters:
            workflow_name (str): Name of the workflow which will run this payload
            payload (dict): The payload to be identified (likely filtered to just
                            keys/values of relevance for identification).

    Returns:
            uuid.UUID: A UUIDv5 identifier for the input payload.
    """
    return uuid.uuid5(
        WORKFLOW_UUIDv5_NAMESPACE,
        workflow_name + json.dumps(payload),
    )
