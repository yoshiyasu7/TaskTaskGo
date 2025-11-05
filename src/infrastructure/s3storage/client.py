import json
from contextlib import asynccontextmanager

from aiobotocore.session import get_session
from src.api.core.config import settings


class S3Client:
    def __init__(
            self,
            aws_access_key: str = settings.AWS_ACCESS_KEY_ID,
            aws_secret_key: str = settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url: str = settings.AWS_ENDPOINT_URL,
            bucket_name: str = settings.AWS_BUCKET,
    ):
        self.config = {
            "aws_access_key_id": aws_access_key,
            "aws_secret_access_key": aws_secret_key,
            "endpoint_url": endpoint_url,
        }
        self.bucket_name = bucket_name
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self):
        async with self.session.create_client("s3", **self.config) as s3_client:
            yield s3_client

    async def upload_json(
        self,
        data: dict,
        object_name: str,
        indent: int | None = None,
    ) -> None:
        """
        Сериализует dict/list в JSON и загружает в S3 как объект.
        """
        # Сериализация в bytes (UTF-8)
        json_bytes = json.dumps(
            data,
            ensure_ascii=False,  # чтобы русские символы не экранировались
            separators=(",", ":") if indent is None else None,
            indent=indent  # вид записи: компактный(None) / человекочитаемый(2)
        ).encode("utf-8")

        async with self.get_client() as s3_client:
            await s3_client.put_object(
                Bucket=self.bucket_name,
                Key=object_name,
                Body=json_bytes,
                ContentType="application/json; charset=utf-8",
            )