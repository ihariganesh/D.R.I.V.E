from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

class TrafficLightBase(BaseModel):
    light_id: str
    name: Optional[str] = None
    junction_id: Optional[str] = None
    current_state: Optional[str] = 'red'
    control_mode: Optional[str] = 'auto'
    cycle_time: Optional[int] = 120
    green_duration: Optional[int] = 45
    yellow_duration: Optional[int] = 5
    red_duration: Optional[int] = 70
    metadata: Optional[Dict[str, Any]] = None

class TrafficLightCreate(TrafficLightBase):
    cameras: Optional[List[UUID]] = []

class TrafficLightUpdate(BaseModel):
    name: Optional[str] = None
    current_state: Optional[str] = None
    control_mode: Optional[str] = None
    cycle_time: Optional[int] = None
    green_duration: Optional[int] = None
    yellow_duration: Optional[int] = None
    red_duration: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class TrafficLightResponse(TrafficLightBase):
    id: UUID
    location: Any = None
    cameras: Optional[List[UUID]] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
