import time
from typing import TypeVar, Generic

from pydantic import BaseModel
from sqlalchemy import select, delete, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.base_model import Base
from src.utils.logger import db_logger, error_logger
from src.utils.time_service import get_moscow_time


T = TypeVar("T", bound=Base)


class BaseDAO(Generic[T]):
    model: type[T]

    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, values: BaseModel):
        start_time = time.time()
        operation = f"INSERT INTO {self.model.__tablename__}"

        try:
            values_dict = values.model_dump(exclude_unset=True)
            new_instance = self.model(**values_dict)
            new_instance.created_at = await get_moscow_time()
            self._session.add(new_instance)
            await self._session.flush()

            execution_time = time.time() - start_time
            db_logger.info(f"DB Flush Operation: {operation} - Success, ID: {new_instance.id}, Time: {execution_time:.3f}s")

            return new_instance

        except SQLAlchemyError as e:
            execution_time = time.time() - start_time
            await self._session.rollback()
            error_logger.error(f"DB Flush Operation Failed: {operation} - {str(e)} за {execution_time:.3f}с")
            raise e


    async def find_one_or_none(self, filters: BaseModel):
        start_time = time.time()
        operation = f"SELECT FROM {self.model.__tablename__}"

        try:
            filters_dict = filters.model_dump(exclude_unset=True) if filters else {}
            query = select(self.model).filter_by(**filters_dict)
            result = await self._session.execute(query)
            record = result.scalar_one_or_none()

            execution_time = time.time() - start_time
            db_logger.info(f"DB Operation: {operation} - Success, Found: {record is not None}, Time: {execution_time:.3f}s")
            return record

        except SQLAlchemyError as e:
            execution_time = time.time() - start_time
            error_logger.error(f"DB Operation Failed: {operation} - {str(e)} за {execution_time:.3f}с")
            raise e


    async def find_all_by_filters(self, filters: BaseModel | None):
        start_time = time.time()
        operation = f"SELECT FROM {self.model.__tablename__}"

        try:
            filters_dict = filters.model_dump(exclude_unset=True) if filters else {}
            query = select(self.model).filter_by(**filters_dict)
            result = await self._session.execute(query)
            records = result.scalars().all()

            execution_time = time.time() - start_time
            db_logger.info(f"DB Operation: {operation} - Success, Found: {records is not None}, Time: {execution_time:.3f}s")
            return records

        except SQLAlchemyError as e:
            execution_time = time.time() - start_time
            error_logger.error(f"DB Operation Failed: {operation} - {str(e)} за {execution_time:.3f}с")
            raise e


    async def update_one_by_id(self, data_id: int, values: BaseModel):
        start_time = time.time()
        operation = f"UPDATE {self.model.__tablename__} WHERE id={data_id}"

        try:
            values_dict = values.model_dump(exclude_unset=True)
            query = update(self.model).where(self.model.id == data_id).values(**values_dict)
            result = await self._session.execute(query)
            await self._session.flush()

            execution_time = time.time() - start_time
            db_logger.info(f"DB Flush Operation: {operation} - Success, Time: {execution_time:.3f}s")

            return result.rowcount

        except SQLAlchemyError as e:
            execution_time = time.time() - start_time
            error_logger.error(f"DB Flush Operation Failed: {operation} - {str(e)} за {execution_time:.3f}с")
            raise e


    async def delete_by_filters(self, filters: BaseModel | None):
        start_time = time.time()
        operation = f"DELETE FROM {self.model.__tablename__}"

        try:
            if not filters:
                raise ValueError("Нужен хотя бы один фильтр для удаления.")

            filter_dict = filters.model_dump(exclude_unset=True)
            query = delete(self.model).filter_by(**filter_dict)
            result = await self._session.execute(query)
            await self._session.flush()

            execution_time = time.time() - start_time
            db_logger.info(
                f"DB Flush Operation: {operation} - Success, Deleted: {result.rowcount} records, Time: {execution_time:.3f}s")
            return result.rowcount

        except SQLAlchemyError as e:
            execution_time = time.time() - start_time
            await self._session.rollback()
            error_logger.error(f"DB Flush Operation Failed: {operation} - {str(e)} за {execution_time:.3f}с")
            raise e

        except Exception as e:
            execution_time = time.time() - start_time
            await self._session.rollback()
            error_logger.error(f"DB Flush Operation Failed: {operation} - {str(e)} за {execution_time:.3f}с")
            raise e