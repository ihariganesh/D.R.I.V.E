from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class TrafficEventBase(BaseModel):
    event_type: str
    severity: str = "medium"
    road_segment: Optional[str] = None
    description: Optional[str] = None
    detected_by: Optional[UUID] = None
    detection_method: str = "ai"
    confidence_score: Optional[float] = None
    video_url: Optional[str] = None
    image_urls: List[str] = []
    affected_radius: int = 500
    vehicles_involved: int = 0
    status: str = "active"

class TrafficEventCreate(TrafficEventBase):
    pass

class TrafficEventResponse(TrafficEventBase):
    id: UUID
    detected_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EventSearch(BaseModel):
    event_type: Optional[str] = None
    status: Optional[str] = None
    severity: Optional[str] = None
    region: Optional[str] = None
