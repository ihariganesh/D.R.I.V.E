from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from database.connection import get_db
from database.models import ManualOverride, User
from api.schemas.override_schemas import ManualOverrideResponse, ManualOverrideCreate
from services.auth_service import get_current_user

router = APIRouter()

@router.get("/", response_model=List[ManualOverrideResponse])
async def list_overrides(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List manual overrides"""
    query = select(ManualOverride)
    
    if active_only:
        query = query.where(ManualOverride.applied == True, ManualOverride.reverted_at == None)
        
    query = query.order_by(ManualOverride.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    overrides = result.scalars().all()
    
    return overrides

@router.post("/", response_model=ManualOverrideResponse)
async def request_override(
    override_data: ManualOverrideCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Request a new manual override"""
    new_override = ManualOverride(
        **override_data.model_dump(),
        user_id=current_user.id
    )
    # Automatically approve if admin/supervisor? For now, let's say all need explicit approval or just create it as requested
    # But schema assumes it needs approval. Let's just create it.
    
    db.add(new_override)
    await db.commit()
    await db.refresh(new_override)
    return new_override

@router.post("/{override_id}/approve", response_model=ManualOverrideResponse)
async def approve_override(
    override_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve and apply an override"""
    if current_user.role not in ['admin', 'supervisor']:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    result = await db.execute(select(ManualOverride).where(ManualOverride.id == override_id))
    override = result.scalar_one_or_none()
    
    if not override:
        raise HTTPException(status_code=404, detail="Override not found")
        
    if override.approved:
        raise HTTPException(status_code=400, detail="Already approved")
        
    override.approved = True
    override.applied = True
    override.applied_at = datetime.utcnow()
    
    # Logic to actually apply changes to the entity would go here (or trigger a service)
    
    await db.commit()
    await db.refresh(override)
    return override

@router.post("/{override_id}/reject", response_model=ManualOverrideResponse)
async def reject_override(
    override_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reject an override request"""
    if current_user.role not in ['admin', 'supervisor']:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    result = await db.execute(select(ManualOverride).where(ManualOverride.id == override_id))
    override = result.scalar_one_or_none()
    
    if not override:
        raise HTTPException(status_code=404, detail="Override not found")
        
    # We might just delete it or mark it as rejected (schema doesn't have rejected flag, but we can leave approved=False)
    # Or maybe delete? Let's just leave it unapproved.
    
    return override

@router.post("/{override_id}/revert", response_model=ManualOverrideResponse)
async def revert_override(
    override_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Revert an applied override"""
    if current_user.role not in ['admin', 'supervisor']:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    result = await db.execute(select(ManualOverride).where(ManualOverride.id == override_id))
    override = result.scalar_one_or_none()
    
    if not override:
        raise HTTPException(status_code=404, detail="Override not found")
    
    if not override.applied:
        raise HTTPException(status_code=400, detail="Override not currently applied")
        
    override.applied = False
    override.reverted_at = datetime.utcnow()
    
    # Logic to revert entity would go here
    
    await db.commit()
    await db.refresh(override)
    return override
