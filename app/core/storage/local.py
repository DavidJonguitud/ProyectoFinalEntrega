import logging
import os
import uuid

import anyio
from fastapi import UploadFile

from app.core.config import settings
from app.core.storage.base import StorageService

logger = logging.getLogger(__name__)


class LocalStorageStrategy(StorageService):
    def __init__(self, upload_dir: str = settings.UPLOAD_DIR):
        self.upload_dir = upload_dir

        os.makedirs(self.upload_dir, exist_ok=True)

    async def upload_file(self, file: UploadFile, folder: str) -> str:
        destination_dir = os.path.join(self.upload_dir, folder)
        os.makedirs(destination_dir, exist_ok=True)

        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(destination_dir, unique_filename)

        try:
            await file.seek(0)
            content = await file.read()
            async with await anyio.open_file(file_path, "wb") as buffer:
                await buffer.write(content)
        except Exception as e:
            logger.exception("Failed to write file to local disk")
            raise OSError(f"Failed to write file to local disk: {e!s}")
        finally:
            await file.close()

        return file_path

    async def delete_file(self, file_path: str) -> None:
        try:
            absolute_path = os.path.abspath(file_path)
            if os.path.exists(absolute_path):
                os.remove(absolute_path)
                logger.info(f"File succesfully deleted from disk: {absolute_path}")
            else:
                logger.warning(
                    f"Fle to delete does not exist in the disk: {absolute_path}"
                )
        except Exception as e:
            logger.exception("Error deleting file")
            raise OSError(f"Error deleting the file from disk: {e!s}")

    async def get_file_for_download(self, file_path: str) -> str:
        absolute_path = os.path.abspath(file_path)
        if not os.path.exists(absolute_path):
            raise FileNotFoundError(
                f"The physiical file was not found on the server path: {absolute_path}"
            )
        return absolute_path
