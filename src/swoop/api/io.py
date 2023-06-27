import io
import logging

from minio import Minio
from minio.error import S3Error

logger = logging.getLogger(__name__)


class IOClient:
    def __init__(
        self, s3_endpoint: str, access_key: str, secret_key: str, bucket_name: str
    ):
        """Initialize IO Client."""
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
        try:
            response = self.client.get_object(self.bucket_name, object_name)
        except S3Error as err:
            logger.error(err)
        else:
            object_response = response.json()
            logger.debug(f"retrieved object content: {object_response}")
            response.close()
            response.release_conn()

        return object_response

    def put_file_object(self, object_name: str, file_name: str):
        result = self.client.fput_object(self.bucket_name, object_name, file_name)
        logger.debug(
            "created {} object; etag: {}, version-id: {}".format(
                result.object_name, result.etag, result.version_id
            )
        )

    def put_object(
        self, object_name: str, object_content: str, content_type="application/json"
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

    def list_objects(self, prefix: str = "", recursive: bool = True):
        return self.client.list_objects(
            self.bucket_name, prefix=prefix, recursive=recursive
        )

    def delete_objects(self, prefix="", recursive=True):
        objects_to_delete = self.list_objects(prefix=prefix, recursive=recursive)
        for obj in objects_to_delete:
            self.client.remove_object(self.bucket_name, obj.object_name)
