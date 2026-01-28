from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from database.connection import get_db
from database.models import AIDecision, User
from api.schemas.decision_schemas import AIDecisionResponse, DecisionFilter
from services.auth_service import get_current_user

router = APIRouter()

@router.get("/", response_model=List[AIDecisionResponse])
async def list_decisions(
    skip: int = 0,
    limit: int = 50,
    decision_type: str = None,
    applied: bool = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List AI decisions with XAI explanations
    Shows what the AI decided and WHY
    """
    query = select(AIDecision)
    
    if decision_type:
        query = query.where(AIDecision.decision_type == decision_type)
    if applied is not None:
        query = query.where(AIDecision.applied == applied)
    
    query = query.order_by(AIDecision.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    decisions = result.scalars().all()
    
    return decisions

@router.get("/{decision_id}", response_model=AIDecisionResponse)
async def get_decision(
    decision_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed AI decision with full XAI explanation
    Example: "Speed lowered to 40km/h because Camera 4 detected debris 500m ahead"
    """
    result = await db.execute(select(AIDecision).where(AIDecision.id == decision_id))
    decision = result.scalar_one_or_none()
    
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    
    return decision

@router.get("/{decision_id}/explanation")
async def get_decision_explanation(
    decision_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get human-readable explanation for an AI decision (XAI Dashboard)
    """
    result = await db.execute(select(AIDecision).where(AIDecision.id == decision_id))
    decision = result.scalar_one_or_none()
    
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    
    return {
        "decision_id": str(decision.id),
        "decision_type": decision.decision_type,
        "what": decision.decision_value,
        "why": decision.explanation,
        "detailed_reasoning": decision.reasoning,
        "confidence": decision.confidence_score,
        "input_data": decision.input_data,
        "model_version": decision.model_version,
        "timestamp": decision.created_at
    }

@router.post("/{decision_id}/override")
async def override_decision(
    decision_id: UUID,
    reason: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Override an AI decision (requires supervisor/admin role)
    """
    if current_user.role not in ['admin', 'supervisor']:
        raise HTTPException(status_code=403, detail="Not authorized to override AI decisions")
    
    result = await db.execute(select(AIDecision).where(AIDecision.id == decision_id))
    decision = result.scalar_one_or_none()
    
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    
    decision.applied = False
    decision.override_reason = f"Overridden by {current_user.full_name}: {reason}"
    
    await db.commit()
    
    return {
        "message": "AI decision overridden",
        "decision_id": str(decision_id),
        "overridden_by": current_user.full_name,
        "reason": reason
    }
