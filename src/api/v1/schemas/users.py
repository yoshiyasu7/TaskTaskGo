from datetime import datetime

from pydantic import BaseModel, ConfigDict


class TokenPydantic(BaseModel):
    access_token: str
    token_type: str


class UserIDPydantic(BaseModel):
    id: int
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "user id"
            }
        }
    )


class UsernamePydantic(BaseModel):
    username: str
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "username": "username"
            }
        }
    )


class UserRegister(BaseModel):
    username: str
    password: str

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "username": "username",
                "password": "password"
            }
        }
    )


class UserOut(BaseModel):
    id: int
    username: str
    created_at: datetime
    updated_at: datetime