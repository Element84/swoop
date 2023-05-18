import io
import logging

from minio import Minio
from minio.error import S3Error

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)


class IOClient:

    def __init__(
        self, s3_endpoint: str, access_key: str, secret_key: str, bucket_name: str
    ):
        """Initialize IO Client."""
        if not bucket_name:
            raise ValueError("Bucket name cannot be empty")
        
        self.client = Minio(
            s3_endpoint.split("//").pop() if "http" in s3_endpoint else s3_endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure="http://" not in s3_endpoint,
        )
        self.bucket_name = bucket_name
        self.create_bucket()

    def get_object(self, object_name: str):
        """Retrieve from object storage."""
        object_response = None
        if not object_name:
            raise ValueError("object_name cannot be empty"

        try:
            response = self.client.get_object(self.bucket_name, object_name)
            object_response = response.json()
            logger.debug(f"retrieved object content: {object_response}")
        except (S3Error, UnboundLocalError) as err:
            logger.debug(err)
        finally:
            response.close()
            response.release_conn()
        else:
            object_response = response.json()
            logger.debug("retrieved object content: %s", object_response)

        return object_response

    def put_file_object(self, object_name: str, file_name: str):
        if (
            object_name
            and file_name
            and self.bucket_name
            and self.client.bucket_exists(self.bucket_name)
        ):
            result = self.client.fput_object(self.bucket_name, object_name, file_name)
            logger.debug(
                "created {} object; etag: {}, version-id: {}".format(
                    result.object_name, result.etag, result.version_id
                )
            )

    def put_object(
        self, object_name: str, object_content: str, content_type="application/json"
    ):
        if (
            object_name
            and object_content
            and content_type
            and self.bucket_name
            and self.client.bucket_exists(self.bucket_name)
        ):
            result = self.client.put_object(
                self.bucket_name,
                object_name,
                io.BytesIO(object_content.encode("utf-8")),
                len(object_content.encode("utf-8")),
                content_type,
            )
            logger.debug(
                "created {} object; etag: {}, version-id: {}".format(
                    result.object_name, result.etag, result.version_id
                )
            )

    def delete_object(self, object_name: str):
        if (
            object_name
            and self.bucket_name
            and self.client.bucket_exists(self.bucket_name)
        ):
            self.client.remove_object(self.bucket_name, object_name)
            logger.debug(f"deleted object: {object_name}")

    def create_bucket(self, bucket_name=None):
        self.bucket_name = bucket_name if bucket_name else self.bucket_name
        if self.bucket_name and not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)
            logger.debug(f"created bucket: {self.bucket_name}")

    def delete_bucket(self, bucket_name=None):
        self.bucket_name = bucket_name if bucket_name else self.bucket_name
        if self.bucket_name and self.client.bucket_exists(self.bucket_name):
            self.client.remove_bucket(self.bucket_name)
            logger.debug(f"deleted bucket: {self.bucket_name}")
            self.bucket_name = None

    def bucket_exists(self, bucket_name: str):
        return bucket_name and self.client.bucket_exists(bucket_name)
