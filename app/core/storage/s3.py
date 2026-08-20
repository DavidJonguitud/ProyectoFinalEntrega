import asyncio
import logging
import uuid

from botocore.exceptions import ClientError
from fastapi import UploadFile

from app.core.config import settings

logger = logging.getLogger(__name__)


class S3StorageStrategy:
    def __init__(
        self,
        bucket_name: str = settings.AWS_S3_BUCKET_NAME,
        # asignacion directa
    ):
        self.bucket_name = bucket_name
        self.s3_client = settings.s3_client

    async def upload_file(self, file: UploadFile, folder: str) -> str:
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        s3_key = f"{folder}/{unique_filename}" if folder else unique_filename
        # cambiar nombre de variable
        try:
            await file.seek(0)
            content = await file.read()

            await asyncio.to_thread(
                self.s3_client.put_object,
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=content,
                ContentType=file.content_type,
            )
            logger.info(
                f"File succesfully uploaded to S3: s3://{self.bucket_name}/{s3_key}"
            )
        # estudiar como aplicamos los patrones, strategy, repository

        except ClientError as e:
            logger.exception("Failed to upload file to S3:")
            raise OSError(f"Failed to upload file to S3: {e!s}")

        finally:
            await file.close()

        return s3_key

    async def delete_file(self, s3_key: str) -> None:
        try:
            await asyncio.to_thread(
                self.s3_client.head_object, Bucket=self.bucket_name, Key=s3_key
            )

            await asyncio.to_thread(
                self.s3_client.delete_object, Bucket=self.bucket_name, Key=s3_key
            )
            logger.info(
                f"File successfully deleted from S3: s3://{self.bucket_name}/{s3_key}"
            )

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            if error_code == "404":
                logger.warning(
                    f"File to delete does not exist in S3: s3://{self.bucket_name}/{s3_key}"
                )
            else:
                logger.exception("Error deleting file from S3")
                raise OSError(f"Error deleting file from S3L {e!s}")

    async def get_file_for_download(self, s3_key: str, expires_in: int = 3600) -> str:
        try:
            await asyncio.to_thread(
                self.s3_client.head_object, Bucket=self.bucket_name, Key=s3_key
            )

            presigned_url = await asyncio.to_thread(
                self.s3_client.generate_presigned_url,
                ClientMethod="get_object",
                Params={"Bucket": self.bucket_name, "Key": s3_key},
                ExpiresIn=expires_in,
            )
            return presigned_url

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            if error_code == "404":
                raise FileNotFoundError(
                    f"The physical file was not found in S3 bucket: {s3_key}"
                )
            else:
                logger.exception("Error generating download URL")
                raise OSError(f"Could not retrieve file download URL: {e!s}")
