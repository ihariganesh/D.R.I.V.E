from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from api.routes import cameras, traffic_lights, sign_boards, events, emergency, users, decisions, overrides, simulations, dashboard, weather
from database.connection import init_db, close_db
from services.websocket_manager import manager

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    print("✅ Database connected")
    yield
    # Shutdown
    await close_db()
    print("👋 Database connection closed")

app = FastAPI(
    title="D.R.I.V.E API",
    description="Dynamic Road Intelligence & Vehicle Environment - AI-powered traffic management system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(cameras.router, prefix="/api/v1/cameras", tags=["Cameras"])
app.include_router(traffic_lights.router, prefix="/api/v1/traffic-lights", tags=["Traffic Lights"])
app.include_router(sign_boards.router, prefix="/api/v1/sign-boards", tags=["Sign Boards"])
app.include_router(events.router, prefix="/api/v1/events", tags=["Events"])
app.include_router(emergency.router, prefix="/api/v1/emergency", tags=["Emergency"])
app.include_router(decisions.router, prefix="/api/v1/decisions", tags=["AI Decisions"])
app.include_router(overrides.router, prefix="/api/v1/overrides", tags=["Manual Overrides"])
app.include_router(simulations.router, prefix="/api/v1/simulations", tags=["Simulations"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(weather.router, prefix="/api/v1/weather", tags=["Weather"])

@app.get("/")
async def root():
    return {
        "message": "D.R.I.V.E API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for now - will be enhanced with real-time updates
            await manager.send_personal_message(f"Message received: {data}", client_id)
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        await manager.broadcast(f"Client #{client_id} left")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
