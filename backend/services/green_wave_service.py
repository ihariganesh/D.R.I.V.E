from typing import List, Dict
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from datetime import datetime
import os

from database.models import TrafficLight, SignBoard, EmergencyVehicle, AIDecision

async def activate_green_wave(
    vehicle_id: UUID,
    route: List[Dict],
    priority: int,
    db: AsyncSession
) -> Dict:
    """
    Activate Green Wave Protocol
    
    This is Innovation #2: Green Wave Protocol
    - Turns downstream lights green
    - Lowers cross-traffic speed limits
    - Clears junction before emergency vehicle arrives
    
    Args:
        vehicle_id: Emergency vehicle UUID
        route: List of waypoints with traffic lights
        priority: Emergency priority (1=highest)
        db: Database session
    
    Returns:
        Dict with affected traffic lights and signs
    """
    affected_lights = []
    affected_signs = []
    
    advance_time = int(os.getenv("GREEN_WAVE_ADVANCE_TIME", 45))  # seconds
    
    # Process each waypoint in the route
    for waypoint in route:
        # Get traffic lights near this waypoint
        query = text("""
            SELECT id, light_id, location, junction_id
            FROM traffic_lights
            WHERE ST_DWithin(
                location::geography,
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
                :radius
            )
            AND control_mode != 'emergency'
        """)
        
        result = await db.execute(
            query, 
            {"lat": waypoint["lat"], "lon": waypoint["lon"], "radius": 100}
        )
        lights = result.fetchall()
        
        for light in lights:
            # Update traffic light to green
            update_query = text("""
                UPDATE traffic_lights
                SET current_state = 'green',
                    control_mode = 'emergency',
                    updated_at = NOW()
                WHERE id = :light_id
            """)
            await db.execute(update_query, {"light_id": light[0]})
            affected_lights.append(str(light[0]))
            
            # Log AI decision for XAI
            ai_decision = AIDecision(
                decision_type='green_wave_activation',
                decision_value={
                    "light_id": str(light[0]),
                    "previous_state": "auto",
                    "new_state": "green"
                },
                explanation=f"Traffic light {light[1]} turned GREEN for Green Wave Protocol. "
                           f"Emergency vehicle (Priority {priority}) approaching junction {light[3]}.",
                reasoning={
                    "vehicle_id": str(vehicle_id),
                    "eta_seconds": advance_time,
                    "priority": priority,
                    "protocol": "green_wave"
                },
                confidence_score=0.95,
                applied=True
            )
            db.add(ai_decision)
        
        # Get sign boards near this waypoint (for cross-traffic)
        sign_query = text("""
            SELECT id, sign_id, current_display, road_segment
            FROM sign_boards
            WHERE ST_DWithin(
                location::geography,
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
                :radius
            )
            AND sign_type = 'speed_limit'
        """)
        
        result = await db.execute(
            sign_query,
            {"lat": waypoint["lat"], "lon": waypoint["lon"], "radius": 200}
        )
        signs = result.fetchall()
        
        for sign in signs:
            # Lower speed limit for cross-traffic
            current_speed = int(sign[2]) if sign[2] else 60
            reduced_speed = max(20, current_speed - 20)
            
            update_sign_query = text("""
                UPDATE sign_boards
                SET current_display = :new_speed,
                    updated_at = NOW()
                WHERE id = :sign_id
            """)
            await db.execute(update_sign_query, {
                "sign_id": sign[0],
                "new_speed": str(reduced_speed)
            })
            affected_signs.append(str(sign[0]))
            
            # Log AI decision for XAI
            ai_decision = AIDecision(
                decision_type='speed_limit_change',
                decision_value={
                    "sign_id": str(sign[0]),
                    "previous_limit": current_speed,
                    "new_limit": reduced_speed
                },
                explanation=f"Speed limit on {sign[3]} reduced to {reduced_speed} km/h for Green Wave Protocol. "
                           f"Allowing safe passage for emergency vehicle.",
                reasoning={
                    "vehicle_id": str(vehicle_id),
                    "protocol": "green_wave",
                    "cross_traffic_safety": True
                },
                confidence_score=0.92,
                applied=True
            )
            db.add(ai_decision)
    
    await db.commit()
    
    # Calculate ETA improvement
    eta_improvement = len(affected_lights) * 30  # Approximate 30 seconds saved per light
    
    return {
        "affected_lights": affected_lights,
        "affected_signs": affected_signs,
        "eta_improvement_seconds": eta_improvement,
        "message": f"Green Wave activated: {len(affected_lights)} lights turned green, "
                  f"{len(affected_signs)} speed limits reduced"
    }

async def deactivate_green_wave(vehicle_id: UUID, db: AsyncSession):
    """
    Deactivate Green Wave Protocol and restore normal traffic control
    """
    # Restore traffic lights to auto mode
    restore_lights_query = text("""
        UPDATE traffic_lights
        SET control_mode = 'auto',
            updated_at = NOW()
        WHERE control_mode = 'emergency'
    """)
    await db.execute(restore_lights_query)
    
    # Restore sign boards to default values
    restore_signs_query = text("""
        UPDATE sign_boards
        SET current_display = default_value,
            updated_at = NOW()
        WHERE current_display != default_value
    """)
    await db.execute(restore_signs_query)
    
    await db.commit()
    
    return {"message": "Green Wave deactivated, normal traffic control restored"}
