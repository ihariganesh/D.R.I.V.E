from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID

from database.connection import get_db
from database.models import TrafficLight, User
from api.schemas.traffic_light_schemas import TrafficLightResponse, TrafficLightUpdate, TrafficLightCreate
from services.auth_service import get_current_user

router = APIRouter()

@router.get("/", response_model=List[TrafficLightResponse])
async def list_traffic_lights(
    skip: int = 0,
    limit: int = 100,
    junction_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all traffic lights with optional filtering"""
    query = select(TrafficLight)
    
    if junction_id:
        query = query.where(TrafficLight.junction_id == junction_id)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    lights = result.scalars().all()
    
    return lights

@router.get("/{light_id}", response_model=TrafficLightResponse)
async def get_traffic_light(
    light_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific traffic light details"""
    result = await db.execute(select(TrafficLight).where(TrafficLight.id == light_id))
    light = result.scalar_one_or_none()
    
    if not light:
        raise HTTPException(status_code=404, detail="Traffic light not found")
    
    return light

@router.post("/", response_model=TrafficLightResponse)
async def create_traffic_light(
    light_data: TrafficLightCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new traffic light (Admin only)"""
    if current_user.role not in ['admin', 'supervisor']:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    new_light = TrafficLight(**light_data.model_dump())
    db.add(new_light)
    await db.commit()
    await db.refresh(new_light)
    return new_light

@router.patch("/{light_id}", response_model=TrafficLightResponse)
async def update_traffic_light(
    light_id: UUID,
    light_update: TrafficLightUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update traffic light configuration (Admin/Supervisor only)"""
    if current_user.role not in ['admin', 'supervisor']:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(select(TrafficLight).where(TrafficLight.id == light_id))
    light = result.scalar_one_or_none()
    
    if not light:
        raise HTTPException(status_code=404, detail="Traffic light not found")
    
    for field, value in light_update.model_dump(exclude_unset=True).items():
        setattr(light, field, value)
    
    await db.commit()
    await db.refresh(light)
    
    return light

@router.post("/{light_id}/control", response_model=TrafficLightResponse)
async def control_traffic_light(
    light_id: UUID,
    state: str = Query(..., regex="^(red|yellow|green)$"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually control traffic light state"""
    if current_user.role not in ['admin', 'supervisor']:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    result = await db.execute(select(TrafficLight).where(TrafficLight.id == light_id))
    light = result.scalar_one_or_none()
    
    if not light:
        raise HTTPException(status_code=404, detail="Traffic light not found")
        
    light.current_state = state
    light.control_mode = 'manual'
    # In a real system, this would trigger a hardware event via MQTT/WebSocket
    
    await db.commit()
    await db.refresh(light)
    return light
