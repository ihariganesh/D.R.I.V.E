from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID
from datetime import datetime

from database.connection import get_db
from database.models import Simulation, ManualOverride, User
from api.schemas.simulation_schemas import SimulationCreate, SimulationResponse, SimulationRequest
from services.auth_service import get_current_user
from services.digital_twin_service import run_digital_twin_simulation

router = APIRouter()

@router.post("/run", response_model=SimulationResponse)
async def run_simulation(
    simulation_request: SimulationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Run Digital Twin simulation before applying manual override
    Predicts outcome in 5 seconds to prevent traffic jams
    """
    # Run the simulation using Digital Twin engine
    simulation_result = await run_digital_twin_simulation(
        input_state=simulation_request.input_state,
        proposed_changes=simulation_request.proposed_changes,
        duration=simulation_request.simulation_duration or 5,
        db=db
    )
    
    # Save simulation to database
    new_simulation = Simulation(
        simulation_type=simulation_request.simulation_type,
        scenario_description=simulation_request.scenario_description,
        input_state=simulation_request.input_state,
        proposed_changes=simulation_request.proposed_changes,
        simulation_duration=simulation_request.simulation_duration or 5,
        results=simulation_result["results"],
        predicted_metrics=simulation_result["predicted_metrics"],
        warnings=simulation_result["warnings"],
        recommendation=simulation_result["recommendation"],
        execution_time_ms=simulation_result["execution_time_ms"],
        created_by=current_user.id
    )
    
    db.add(new_simulation)
    await db.commit()
    await db.refresh(new_simulation)
    
    return new_simulation

@router.get("/", response_model=List[SimulationResponse])
async def list_simulations(
    skip: int = 0,
    limit: int = 50,
    simulation_type: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List simulation history"""
    query = select(Simulation)
    
    if simulation_type:
        query = query.where(Simulation.simulation_type == simulation_type)
    
    query = query.order_by(Simulation.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    simulations = result.scalars().all()
    
    return simulations

@router.get("/{simulation_id}", response_model=SimulationResponse)
async def get_simulation(
    simulation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get simulation details"""
    result = await db.execute(select(Simulation).where(Simulation.id == simulation_id))
    simulation = result.scalar_one_or_none()
    
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    return simulation

@router.post("/{simulation_id}/approve")
async def approve_simulation(
    simulation_id: UUID,
    override_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Approve simulation and apply manual override
    This happens after Digital Twin shows it's safe
    """
    if current_user.role not in ['admin', 'supervisor', 'officer']:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    result = await db.execute(select(Simulation).where(Simulation.id == simulation_id))
    simulation = result.scalar_one_or_none()
    
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    if simulation.recommendation == 'reject':
        raise HTTPException(
            status_code=400, 
            detail=f"Simulation recommends rejecting this action. Warnings: {simulation.warnings}"
        )
    
    # Create manual override
    manual_override = ManualOverride(
        override_type=override_data.get('override_type'),
        entity_id=override_data.get('entity_id'),
        entity_type=override_data.get('entity_type'),
        previous_value=override_data.get('previous_value'),
        new_value=override_data.get('new_value'),
        reason=override_data.get('reason'),
        user_id=current_user.id,
        simulation_run=True,
        simulation_result=simulation.results,
        approved=True,
        applied=True,
        applied_at=datetime.utcnow(),
        duration_minutes=override_data.get('duration_minutes', 60)
    )
    
    db.add(manual_override)
    await db.commit()
    
    return {
        "message": "Simulation approved and override applied",
        "simulation_id": str(simulation_id),
        "override_id": str(manual_override.id),
        "warnings": simulation.warnings if simulation.recommendation == 'caution' else []
    }
