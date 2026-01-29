from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class ManualOverrideBase(BaseModel):
    override_type: str
    entity_id: Optional[UUID] = None
    entity_type: Optional[str] = None
    new_value: Optional[Dict[str, Any]] = None
    reason: str
    duration_minutes: Optional[int] = None

class ManualOverrideCreate(ManualOverrideBase):
    pass

class ManualOverrideResponse(ManualOverrideBase):
    id: UUID
    previous_value: Optional[Dict[str, Any]] = None
    user_id: UUID
    simulation_run: bool = False
    simulation_result: Optional[Dict[str, Any]] = None
    approved: bool = False
    applied: bool = False
    expires_at: Optional[datetime] = None
    created_at: datetime
    applied_at: Optional[datetime] = None
    reverted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
