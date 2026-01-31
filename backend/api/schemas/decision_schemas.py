from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from uuid import UUID
from datetime import datetime

class AIDecisionBase(BaseModel):
    decision_type: str
    decision_value: Dict[str, Any]
    explanation: str
    reasoning: Optional[Dict[str, Any]] = None
    confidence_score: float
    input_data: Optional[Dict[str, Any]] = None
    related_cameras: List[UUID] = []
    related_events: List[UUID] = []
    affected_entities: Optional[Dict[str, Any]] = None
    model_version: Optional[str] = None
    processing_time_ms: Optional[int] = None
    applied: bool = False
    override_reason: Optional[str] = None

class AIDecisionResponse(AIDecisionBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class DecisionFilter(BaseModel):
    decision_type: Optional[str] = None
    applied: Optional[bool] = None
