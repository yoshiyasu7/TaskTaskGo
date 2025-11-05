from pydantic import BaseModel, ConfigDict, Field


class ProjectFilter(BaseModel):
    user_id: int
    id: int | None = None
    title: str | None = None


class ProjectCreate(BaseModel):
    title: str | None = None
    content: str | None = None
    user_id: int

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "title": "Project title to create",
                "content": "Project content to create",
            }
        }
    )


class ProjectRead(BaseModel):
    id: int
    title: str
    content: str
    user_id: int

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "title": "Project title to read",
                "content": "Project content to read",
            }
        }
    )


class ProjectUpdate(BaseModel):
    title: str | None = None
    content: str | None = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "title": "Project title to update",
                "content": "Project content to update",
            }
        }
    )


class ProjectDelete(BaseModel):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "project_id": "Project ID to delete",
                "title": "Project title to delete",
            }
        }
    )