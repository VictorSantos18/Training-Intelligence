from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BodyRegionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    code: str
    name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
