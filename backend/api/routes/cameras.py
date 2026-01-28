from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from typing import List, Optional
from uuid import UUID

from database.connection import get_db
from database.models import Camera, User
from api.schemas.camera_schemas import CameraResponse, CameraUpdate
from services.auth_service import get_current_user

router = APIRouter()

@router.get("/", response_model=List[CameraResponse])
async def list_cameras(
    skip: int = 0,
    limit: int = 100,
    region: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all cameras with optional filtering"""
    query = select(Camera)
    
    if region:
        query = query.where(Camera.region == region)
    if status:
        query = query.where(Camera.status == status)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    cameras = result.scalars().all()
    
    return cameras

@router.get("/{camera_id}", response_model=CameraResponse)
async def get_camera(
    camera_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific camera details"""
    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    return camera

@router.get("/nearby/{lat}/{lon}")
async def get_nearby_cameras(
    lat: float,
    lon: float,
    radius: int = Query(1000, description="Radius in meters"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Find cameras near a specific location"""
    query = text("""
        SELECT * FROM find_nearby_cameras(:lat, :lon, :radius)
    """)
    
    result = await db.execute(query, {"lat": lat, "lon": lon, "radius": radius})
    cameras = result.fetchall()
    
    return [{"camera_id": row[0], "camera_name": row[1], "distance_meters": row[2]} for row in cameras]

@router.patch("/{camera_id}", response_model=CameraResponse)
async def update_camera(
    camera_id: UUID,
    camera_update: CameraUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update camera information (admin/supervisor only)"""
    if current_user.role not in ['admin', 'supervisor']:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    # Update fields
    for field, value in camera_update.dict(exclude_unset=True).items():
        setattr(camera, field, value)
    
    await db.commit()
    await db.refresh(camera)
    
    return camera
