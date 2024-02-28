from datetime import datetime

from pydantic import UUID4, Field
from pydantic.main import BaseModel


class HistorySchema(BaseModel):
    user_id: UUID4
    login_time: datetime = Field(..., example=datetime.now().strftime('%Y-%m-%dT%H:%M'))

    class Config:
        from_attributes = True
