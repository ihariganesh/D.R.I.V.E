from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Optional
from services.weather_service import get_weather_service, WeatherService

router = APIRouter(prefix="/weather", tags=["weather"])

@router.get("/current")
async def get_current_weather(
    city: Optional[str] = None,
    service: WeatherService = Depends(get_weather_service)
) -> Dict:
    """
    Get current weather data for traffic management
    """
    try:
        return await service.get_current_weather(city)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/impact")
async def get_weather_impact(
    service: WeatherService = Depends(get_weather_service)
) -> Dict:
    """
    Get assessment of how current weather impacts traffic
    """
    weather = await service.get_current_weather()
    condition = weather["condition"]
    visibility = weather["visibility"]
    
    impact = "low"
    suggested_reduction = 0
    warnings = []
    
    if condition == "heavy_rain":
        impact = "high"
        suggested_reduction = 25
        warnings.append("Heavy rain: Significant reduction in visibility and traction")
    elif condition == "rain":
        impact = "medium"
        suggested_reduction = 15
        warnings.append("Rain: Reduced road traction, drive with caution")
    elif condition == "fog":
        impact = "high"
        suggested_reduction = 20
        warnings.append("Dense fog: Extremely low visibility")
    elif visibility < 2000:
        impact = "medium"
        suggested_reduction = 10
        warnings.append("Low visibility detected")
        
    return {
        "weather": weather,
        "traffic_impact": impact,
        "suggested_speed_reduction": suggested_reduction,
        "warnings": warnings,
        "is_safe_for_high_speed": impact == "low"
    }
