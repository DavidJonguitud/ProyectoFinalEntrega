import io
import pytest
from fastapi import UploadFile
from botocore.exceptions import ClientError
import logging

from app.core.config import Settings, settings
from app.core.storage.s3 import S3StorageStrategy

pytestmark = pytest.mark.asyncio

TEST_BUCKET = "test-project-bucket-ficticio"
TEST_FOLDER = "project_99"


async def test_s3_upload_file_success(mock_s3_env, monkeypatch):
    s3_client = mock_s3_env
    monkeypatch.setattr(Settings, "s3_client", s3_client)

    strategy = S3StorageStrategy(bucket_name=TEST_BUCKET)

    file_content = b"%PDF-1.4 contenido s3 mockeado"
    file_name = "documento_s3_test.pdf"

    upload_file = UploadFile(
        filename=file_name,
        file=io.BytesIO(file_content),
        headers={"content-type": "application/pdf"}
    )

    s3_key = await strategy.upload_file(file=upload_file, folder=TEST_FOLDER)

    assert s3_key.startswith(f"{TEST_FOLDER}/")
    assert file_name in s3_key

    response = s3_client.get_object(Bucket=TEST_BUCKET, Key=s3_key)
    downloaded_content = response["Body"].read()

    assert downloaded_content == file_content
    assert response["ContentType"] == "application/pdf"


async def test_s3_delete_file_success(mock_s3_env, monkeypatch):
    s3_client = mock_s3_env
    monkeypatch.setattr(Settings, "s3_client", s3_client)

    strategy = S3StorageStrategy(bucket_name=TEST_BUCKET)
    s3_key = f"{TEST_FOLDER}/archivo_para_borrar.pdf"

    s3_client.put_object(
        Bucket=TEST_BUCKET,
        Key=s3_key,
        Body=b"contenido temporal",
        ContentType="application/pdf"
    )

    try:
        pre_check = s3_client.head_object(Bucket=TEST_BUCKET, Key=s3_key)
        assert pre_check is not None
    except ClientError:
        pytest.fail("El archivo de pruebas no pudo ser creado inicialmente en S3 simulado.")


    await strategy.delete_file(s3_key=s3_key)

    with pytest.raises(ClientError) as exc_info:
        s3_client.head_object(Bucket=TEST_BUCKET, Key=s3_key)

    assert exc_info.value.response["Error"]["Code"] == "404"


async def test_s3_delete_file_not_found_does_not_rise_error(mock_s3_env, monkeypatch):
    s3_client = mock_s3_env
    monkeypatch.setattr(Settings, "s3_client", s3_client)

    strategy = S3StorageStrategy(bucket_name=TEST_BUCKET)
    non_existent_key = "project_99/no_existo.pdf"

    await strategy.delete_file(s3_key=non_existent_key)


async def test_s3_get_file_for_download_success(mock_s3_env, monkeypatch):
    s3_client = mock_s3_env
    monkeypatch.setattr(Settings, "s3_client", s3_client)

    strategy = S3StorageStrategy(bucket_name=TEST_BUCKET)
    s3_key = f"{TEST_FOLDER}/archivo_desgarga.pdf"

    s3_client.put_object(
        Bucket=TEST_BUCKET,
        Key=s3_key,
        Body=b"contenido descarga",
        ContentType="application/pdf"
    )

    presigned_url = await strategy.get_file_for_download(s3_key=s3_key, expires_in=1800)

    assert presigned_url is not None
    assert f"https://{TEST_BUCKET}.s3.amazonaws.com/{s3_key}" in presigned_url
    assert "AWSAccessKeyId" in presigned_url or "X-Amz-Signature" in presigned_url


async def test_s3_get_file_for_download_not_found(mock_s3_env, monkeypatch):
    s3_client = mock_s3_env
    monkeypatch.setattr(Settings, "s3_client", s3_client)

    strategy = S3StorageStrategy(bucket_name=TEST_BUCKET)
    non_existent_key = "project_99/no_existe.pdf"

    with pytest.raises(FileNotFoundError) as exc_info:
        await strategy.get_file_for_download(s3_key=non_existent_key)

    assert "was not found in S3 bucket" in str(exc_info.value)