from typing import Optional
from datetime import (
    datetime, timezone
)

from sqlmodel import (
    Field, SQLModel
)


class BaseModel(SQLModel):

    id: Optional[int] = Field(
        primary_key=True,
        index=True
    )

    updated_at: datetime = Field(
        default = datetime.now(timezone.utc),
        sa_column_kwargs = {
            "onupdate": datetime.now(timezone.utc)
        }
    )

    created_at: datetime = Field(
        default = datetime.now(timezone.utc)
    )