from abc import ABC, abstractmethod

from fastapi import UploadFile


class StorageService(ABC):
    @abstractmethod
    async def upload_file(self, file: UploadFile, folder: str) -> str:
        pass

    @abstractmethod
    async def delete_file(self, file_path: str) -> None:
        pass

    @abstractmethod
    async def get_file_for_download(self, file_path: str):
        pass
