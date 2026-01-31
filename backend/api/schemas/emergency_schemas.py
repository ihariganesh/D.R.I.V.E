from pydantic import BaseModel
from typing import List, Optional, Any
from uuid import UUID
from datetime import datetime

class EmergencyVehicleBase(BaseModel):
    vehicle_id: str
    vehicle_type: str
    license_plate: Optional[str] = None
    priority: int = 1
    status: str = "inactive"

class EmergencyVehicleCreate(EmergencyVehicleBase):
    pass

class EmergencyVehicleResponse(EmergencyVehicleBase):
    id: UUID
    current_location: Optional[Any] = None
    destination: Optional[Any] = None
    green_wave_active: bool
    speed_kmh: Optional[float] = None
    eta_seconds: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class GreenWaveActivate(BaseModel):
    vehicle_id: UUID
    route: List[List[float]] # List of coordinates [[lat, lon], ...]
    priority: int = 5
