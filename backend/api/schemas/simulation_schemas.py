from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from uuid import UUID
from datetime import datetime

class SimulationBase(BaseModel):
    simulation_type: str
    scenario_description: Optional[str] = None
    input_state: Dict[str, Any]
    proposed_changes: Dict[str, Any]
    simulation_duration: int = 5

class SimulationCreate(SimulationBase):
    pass

class SimulationRequest(SimulationBase):
    pass

class SimulationResponse(SimulationBase):
    id: UUID
    results: Optional[Dict[str, Any]] = None
    predicted_metrics: Optional[Dict[str, Any]] = None
    warnings: Optional[List[Any]] = None
    recommendation: Optional[str] = None
    execution_time_ms: Optional[int] = None
    created_by: Optional[UUID] = None
    related_override_id: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True
