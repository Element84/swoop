import logging

from minio import Minio
from minio.error import S3Error

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)


# Change this file to an IO class
class IOClient:
    client = None
    bucket_name = None

    def __init__(
        self, s3_endpoint: str, access_key: str, secret_key: str, bucket_name=None
    ):
        """Initialize IO Client."""
        self.client = Minio(
            s3_endpoint.split("//").pop() if "http" in s3_endpoint else s3_endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure="http://" not in s3_endpoint,
        )
        self.bucket_name = bucket_name

    def set_bucket_name(self, bucket_name: str):
        self.bucket_name = bucket_name

    def get_object(self, object_name: str):
        """Retrieve from object storage."""
        object_response = None
        if (
            object_name
            and self.bucket_name
            and self.client.bucket_exists(self.bucket_name)
        ):
            try:
                try:
                    response = self.client.get_object(self.bucket_name, object_name)
                    object_response = response.json()
                except S3Error as err:
                    logger.debug(err)
                finally:
                    response.close()
                    response.release_conn()
            except UnboundLocalError as err:
                logger.debug(err)

        return object_response
