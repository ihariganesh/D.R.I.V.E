from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

class SignBoardBase(BaseModel):
    sign_id: str
    name: Optional[str] = None
    sign_type: Optional[str] = 'speed_limit'
    current_display: Optional[str] = None
    default_value: Optional[str] = None
    road_segment: Optional[str] = None
    direction: Optional[str] = None
    status: Optional[str] = 'active'
    metadata: Optional[Dict[str, Any]] = None

class SignBoardCreate(SignBoardBase):
    cameras: Optional[List[UUID]] = []

class SignBoardUpdate(BaseModel):
    name: Optional[str] = None
    current_display: Optional[str] = None
    status: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class SignBoardResponse(SignBoardBase):
    id: UUID
    location: Any = None
    cameras: Optional[List[UUID]] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
