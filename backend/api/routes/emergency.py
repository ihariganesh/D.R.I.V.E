from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from database.connection import get_db
from database.models import EmergencyVehicle, TrafficLight, User
from api.schemas.emergency_schemas import EmergencyVehicleCreate, EmergencyVehicleResponse, GreenWaveActivate
from services.auth_service import get_current_user
from services.green_wave_service import activate_green_wave, deactivate_green_wave
from services.websocket_manager import manager

router = APIRouter()

@router.get("/vehicles", response_model=List[EmergencyVehicleResponse])
async def list_emergency_vehicles(
    status: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List emergency vehicles"""
    query = select(EmergencyVehicle)
    
    if status:
        query = query.where(EmergencyVehicle.status == status)
    
    result = await db.execute(query)
    vehicles = result.scalars().all()
    
    return vehicles

@router.post("/vehicles", response_model=EmergencyVehicleResponse, status_code=201)
async def create_emergency_vehicle(
    vehicle_data: EmergencyVehicleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Register new emergency vehicle"""
    if current_user.role not in ['admin', 'supervisor']:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    new_vehicle = EmergencyVehicle(**vehicle_data.dict())
    
    db.add(new_vehicle)
    await db.commit()
    await db.refresh(new_vehicle)
    
    return new_vehicle

@router.post("/green-wave/activate")
async def activate_green_wave_route(
    green_wave_data: GreenWaveActivate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Activate Green Wave Protocol for emergency vehicle
    Clears the path by turning lights green and lowering cross-traffic speeds
    """
    # Get emergency vehicle
    result = await db.execute(
        select(EmergencyVehicle).where(EmergencyVehicle.id == green_wave_data.vehicle_id)
    )
    vehicle = result.scalar_one_or_none()
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Emergency vehicle not found")
    
    # Activate Green Wave
    result = await activate_green_wave(
        vehicle_id=vehicle.id,
        route=green_wave_data.route,
        priority=green_wave_data.priority,
        db=db
    )
    
    # Update vehicle status
    vehicle.status = 'en_route'
    vehicle.green_wave_active = True
    vehicle.activated_at = func.now()
    
    await db.commit()
    
    # Broadcast to WebSocket clients
    await manager.broadcast({
        "type": "green_wave_activated",
        "vehicle_id": str(vehicle.id),
        "vehicle_type": vehicle.vehicle_type,
        "route": green_wave_data.route
    })
    
    return {
        "message": "Green Wave Protocol activated",
        "vehicle_id": str(vehicle.id),
        "vehicle_type": vehicle.vehicle_type,
        "affected_lights": result["affected_lights"],
        "affected_signs": result["affected_signs"],
        "eta_improvement_seconds": result["eta_improvement_seconds"]
    }

@router.post("/green-wave/deactivate/{vehicle_id}")
async def deactivate_green_wave_route(
    vehicle_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Deactivate Green Wave Protocol"""
    result = await db.execute(
        select(EmergencyVehicle).where(EmergencyVehicle.id == vehicle_id)
    )
    vehicle = result.scalar_one_or_none()
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Emergency vehicle not found")
    
    # Deactivate Green Wave
    await deactivate_green_wave(vehicle_id=vehicle.id, db=db)
    
    # Update vehicle status
    vehicle.green_wave_active = False
    vehicle.deactivated_at = func.now()
    
    await db.commit()
    
    await manager.broadcast({
        "type": "green_wave_deactivated",
        "vehicle_id": str(vehicle.id)
    })
    
    return {"message": "Green Wave Protocol deactivated", "vehicle_id": str(vehicle_id)}

@router.get("/vehicles/{vehicle_id}/tracking")
async def get_vehicle_tracking(
    vehicle_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get multi-camera tracking data for emergency vehicle"""
    result = await db.execute(
        select(EmergencyVehicle).where(EmergencyVehicle.id == vehicle_id)
    )
    vehicle = result.scalar_one_or_none()
    
    if not vehicle:
        raise HTTPException(status_code=404, detail="Emergency vehicle not found")
    
    return {
        "vehicle_id": str(vehicle.id),
        "current_location": vehicle.current_location,
        "destination": vehicle.destination,
        "cameras_tracking": vehicle.cameras_tracking,
        "speed_kmh": vehicle.speed_kmh,
        "eta_seconds": vehicle.eta_seconds,
        "green_wave_active": vehicle.green_wave_active
    }
