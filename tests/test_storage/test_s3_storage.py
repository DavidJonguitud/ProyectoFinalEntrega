import io
from unittest.mock import patch

import pytest
from botocore.exceptions import ClientError
from fastapi import UploadFile

from app.core.storage.s3 import S3StorageStrategy

pytestmark = pytest.mark.asyncio

TEST_BUCKET = "test-project-bucket-ficticio"
TEST_FOLDER = "project_99"


async def test_s3_delete_file_success(mock_s3_env):
    s3_client = mock_s3_env

    with patch("app.core.storage.s3.boto3.client", return_value=s3_client):
        strategy = S3StorageStrategy(bucket_name=TEST_BUCKET)

    s3_path = f"{TEST_FOLDER}/archivo_para_borrar.pdf"

    s3_client.put_object(
        Bucket=TEST_BUCKET,
        Key=s3_path,
        Body=b"contenido temporal",
        ContentType="application/pdf",
    )

    try:
        pre_check = s3_client.head_object(Bucket=TEST_BUCKET, Key=s3_path)
        assert pre_check is not None
    except ClientError:
        pytest.fail(
            "El archivo de pruebas no pudo ser creado inicialmente en S3 simulado."
        )

    await strategy.delete_file(s3_path=s3_path)

    with pytest.raises(ClientError) as exc_info:
        s3_client.head_object(Bucket=TEST_BUCKET, Key=s3_path)

    assert exc_info.value.response["Error"]["Code"] == "404"


async def test_s3_delete_file_not_found_does_not_raise_error(mock_s3_env):
    s3_client = mock_s3_env

    with patch("app.core.storage.s3.boto3.client", return_value=s3_client):
        strategy = S3StorageStrategy(bucket_name=TEST_BUCKET)

    non_existent_key = "project_99/no_existo.pdf"

    await strategy.delete_file(s3_path=non_existent_key)


async def test_s3_get_file_for_download_success(mock_s3_env):
    s3_client = mock_s3_env

    with patch("app.core.storage.s3.boto3.client", return_value=s3_client):
        strategy = S3StorageStrategy(bucket_name=TEST_BUCKET)

    s3_path = f"{TEST_FOLDER}/archivo_desgarga.pdf"

    s3_client.put_object(
        Bucket=TEST_BUCKET,
        Key=s3_path,
        Body=b"contenido descarga",
        ContentType="application/pdf",
    )

    presigned_url = await strategy.get_file_for_download(
        s3_path=s3_path, expires_in=1800
    )

    assert presigned_url is not None
    assert f"https://{TEST_BUCKET}.s3.amazonaws.com/{s3_path}" in presigned_url
    assert "AWSAccessKeyId" in presigned_url or "X-Amz-Signature" in presigned_url


async def test_s3_get_file_for_download_not_found(mock_s3_env):
    s3_client = mock_s3_env

    with patch("app.core.storage.s3.boto3.client", return_value=s3_client):
        strategy = S3StorageStrategy(bucket_name=TEST_BUCKET)

    non_existent_key = "project_99/no_existe.pdf"

    with pytest.raises(FileNotFoundError) as exc_info:
        await strategy.get_file_for_download(s3_path=non_existent_key)

    assert "was not found in S3 bucket" in str(exc_info.value)


async def test_s3_upload_file_success(mock_s3_env):
    s3_client = mock_s3_env

    with patch("app.core.storage.s3.boto3.client", return_value=s3_client):
        strategy = S3StorageStrategy(bucket_name=TEST_BUCKET)

    file_content = b"%PDF-1.4 contenido s3 mockeado"
    file_name = "documento_s3_test.pdf"

    upload_file = UploadFile(
        filename=file_name,
        file=io.BytesIO(file_content),
        headers={"content-type": "application/pdf"},
    )

    s3_path = await strategy.upload_file(file=upload_file, folder=TEST_FOLDER)

    assert s3_path.startswith(f"{TEST_FOLDER}/")
    assert s3_path.endswith(".pdf")

    response = s3_client.get_object(Bucket=TEST_BUCKET, Key=s3_path)
    downloaded_content = response["Body"].read()

    assert downloaded_content == file_content
    assert response["ContentType"] == "application/pdf"
