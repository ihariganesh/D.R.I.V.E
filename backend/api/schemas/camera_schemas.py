from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

class CameraBase(BaseModel):
    camera_id: str
    name: str
    region: Optional[str] = None
    status: Optional[str] = 'active'
    resolution_width: Optional[int] = 1920
    resolution_height: Optional[int] = 1080
    fps: Optional[int] = 30
    direction: Optional[float] = None
    coverage_radius: Optional[int] = 100
    metadata: Optional[Dict[str, Any]] = None

class CameraCreate(CameraBase):
    pass

class CameraUpdate(BaseModel):
    name: Optional[str] = None
    region: Optional[str] = None
    status: Optional[str] = None
    resolution_width: Optional[int] = None
    resolution_height: Optional[int] = None
    fps: Optional[int] = None
    direction: Optional[float] = None
    coverage_radius: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None

class CameraResponse(CameraBase):
    id: UUID
    location: Any = None  # Geography field might need careful handling or serialization
    installed_at: datetime
    last_active: datetime
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
