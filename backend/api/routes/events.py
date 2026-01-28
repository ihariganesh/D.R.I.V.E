from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from uuid import UUID

from database.connection import get_db
from database.models import TrafficEvent, Camera, User
from api.schemas.event_schemas import TrafficEventCreate, TrafficEventResponse, EventSearch
from services.auth_service import get_current_user
from services.websocket_manager import manager

router = APIRouter()

@router.get("/", response_model=List[TrafficEventResponse])
async def list_events(
    skip: int = 0,
    limit: int = 50,
    event_type: str = None,
    status: str = None,
    severity: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List traffic events with filtering"""
    query = select(TrafficEvent)
    
    if event_type:
        query = query.where(TrafficEvent.event_type == event_type)
    if status:
        query = query.where(TrafficEvent.status == status)
    if severity:
        query = query.where(TrafficEvent.severity == severity)
    
    query = query.order_by(TrafficEvent.detected_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    events = result.scalars().all()
    
    return events

@router.post("/", response_model=TrafficEventResponse, status_code=201)
async def create_event(
    event_data: TrafficEventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new traffic event (manual or AI)"""
    new_event = TrafficEvent(**event_data.dict())
    
    db.add(new_event)
    await db.commit()
    await db.refresh(new_event)
    
    # Broadcast to WebSocket clients
    await manager.broadcast({
        "type": "new_event",
        "event": {
            "id": str(new_event.id),
            "type": new_event.event_type,
            "severity": new_event.severity,
            "description": new_event.description
        }
    })
    
    return new_event

@router.get("/{event_id}", response_model=TrafficEventResponse)
async def get_event(
    event_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific event details"""
    result = await db.execute(select(TrafficEvent).where(TrafficEvent.id == event_id))
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return event

@router.patch("/{event_id}/acknowledge")
async def acknowledge_event(
    event_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Acknowledge a traffic event"""
    result = await db.execute(select(TrafficEvent).where(TrafficEvent.id == event_id))
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event.status = 'acknowledged'
    event.acknowledged_at = func.now()
    
    await db.commit()
    
    return {"message": "Event acknowledged", "event_id": str(event_id)}

@router.patch("/{event_id}/resolve")
async def resolve_event(
    event_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark event as resolved"""
    result = await db.execute(select(TrafficEvent).where(TrafficEvent.id == event_id))
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event.status = 'resolved'
    event.resolved_at = func.now()
    
    await db.commit()
    
    await manager.broadcast({
        "type": "event_resolved",
        "event_id": str(event_id)
    })
    
    return {"message": "Event resolved", "event_id": str(event_id)}
