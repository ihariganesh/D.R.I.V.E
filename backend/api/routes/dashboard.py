from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, func
from database.connection import get_db
from database.models import User, Camera, TrafficEvent, EmergencyVehicle, TrafficLight
from services.auth_service import get_current_user

router = APIRouter()

@router.get("/overview")
async def get_dashboard_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get dashboard overview with real-time statistics
    """
    # Get active cameras
    cameras_result = await db.execute(
        select(func.count(Camera.id)).where(Camera.status == 'active')
    )
    active_cameras = cameras_result.scalar()
    
    # Get active events
    events_result = await db.execute(
        select(func.count(TrafficEvent.id)).where(TrafficEvent.status == 'active')
    )
    active_events = events_result.scalar()
    
    # Get emergency vehicles
    emergency_result = await db.execute(
        select(func.count(EmergencyVehicle.id)).where(EmergencyVehicle.status == 'active')
    )
    active_emergency = emergency_result.scalar()
    
    # Get green wave status
    green_wave_result = await db.execute(
        select(func.count(EmergencyVehicle.id)).where(EmergencyVehicle.green_wave_active == True)
    )
    green_wave_count = green_wave_result.scalar()
    
    return {
        "system_status": "operational",
        "active_cameras": active_cameras,
        "active_events": active_events,
        "emergency_vehicles_active": active_emergency,
        "green_wave_protocols_active": green_wave_count,
        "timestamp": func.now()
    }
