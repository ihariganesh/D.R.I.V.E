from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from uuid import UUID

from database.connection import get_db
from database.models import SignBoard, User
from api.schemas.sign_board_schemas import SignBoardResponse, SignBoardUpdate, SignBoardCreate
from services.auth_service import get_current_user

router = APIRouter()

@router.get("/", response_model=List[SignBoardResponse])
async def list_sign_boards(
    skip: int = 0,
    limit: int = 100,
    road_segment: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all sign boards"""
    query = select(SignBoard)
    
    if road_segment:
        query = query.where(SignBoard.road_segment == road_segment)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    signs = result.scalars().all()
    
    return signs

@router.get("/{sign_id}", response_model=SignBoardResponse)
async def get_sign_board(
    sign_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific sign board details"""
    result = await db.execute(select(SignBoard).where(SignBoard.id == sign_id))
    sign = result.scalar_one_or_none()
    
    if not sign:
        raise HTTPException(status_code=404, detail="Sign board not found")
    
    return sign

@router.post("/", response_model=SignBoardResponse)
async def create_sign_board(
    sign_data: SignBoardCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new sign board (Admin only)"""
    if current_user.role not in ['admin', 'supervisor']:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    new_sign = SignBoard(**sign_data.model_dump())
    db.add(new_sign)
    await db.commit()
    await db.refresh(new_sign)
    return new_sign

@router.patch("/{sign_id}/display", response_model=SignBoardResponse)
async def update_sign_display(
    sign_id: UUID,
    display_text: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update sign board display message"""
    if current_user.role not in ['admin', 'supervisor']:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    result = await db.execute(select(SignBoard).where(SignBoard.id == sign_id))
    sign = result.scalar_one_or_none()
    
    if not sign:
        raise HTTPException(status_code=404, detail="Sign board not found")
        
    sign.current_display = display_text
    
    await db.commit()
    await db.refresh(sign)
    return sign
