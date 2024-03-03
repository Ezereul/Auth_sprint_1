from datetime import datetime

from pydantic import UUID4, Field, ConfigDict
from pydantic.main import BaseModel


class HistorySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID4
    login_time: datetime = Field(..., example=datetime.now().strftime('%Y-%m-%dT%H:%M'))
