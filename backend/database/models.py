from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, ARRAY, Text
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geography
from datetime import datetime
import uuid

from database.connection import Base

class Camera(Base):
    __tablename__ = "cameras"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    camera_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    location = Column(Geography(geometry_type='POINT', srid=4326))
    region = Column(String(100))
    status = Column(String(20), default='active')
    resolution_width = Column(Integer, default=1920)
    resolution_height = Column(Integer, default=1080)
    fps = Column(Integer, default=30)
    direction = Column(Float)
    coverage_radius = Column(Integer, default=100)
    additional_metadata = Column("metadata", JSON)
    installed_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TrafficLight(Base):
    __tablename__ = "traffic_lights"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    light_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(255))
    location = Column(Geography(geometry_type='POINT', srid=4326))
    junction_id = Column(String(50))
    current_state = Column(String(20), default='red')
    control_mode = Column(String(20), default='auto')
    cycle_time = Column(Integer, default=120)
    green_duration = Column(Integer, default=45)
    yellow_duration = Column(Integer, default=5)
    red_duration = Column(Integer, default=70)
    cameras = Column(ARRAY(UUID(as_uuid=True)))
    additional_metadata = Column("metadata", JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SignBoard(Base):
    __tablename__ = "sign_boards"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sign_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(255))
    location = Column(Geography(geometry_type='POINT', srid=4326))
    sign_type = Column(String(50), default='speed_limit')
    current_display = Column(String(255))
    default_value = Column(String(50))
    road_segment = Column(String(100))
    direction = Column(String(20))
    cameras = Column(ARRAY(UUID(as_uuid=True)))
    status = Column(String(20), default='active')
    additional_metadata = Column("metadata", JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TrafficEvent(Base):
    __tablename__ = "traffic_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(50), nullable=False)
    severity = Column(String(20), default='medium')
    location = Column(Geography(geometry_type='POINT', srid=4326))
    road_segment = Column(String(100))
    description = Column(Text)
    detected_by = Column(UUID(as_uuid=True))
    detection_method = Column(String(50), default='ai')
    confidence_score = Column(Float)
    video_url = Column(Text)
    image_urls = Column(ARRAY(Text))
    affected_radius = Column(Integer, default=500)
    vehicles_involved = Column(Integer, default=0)
    status = Column(String(20), default='active')
    additional_metadata = Column("metadata", JSON)
    detected_at = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class EmergencyVehicle(Base):
    __tablename__ = "emergency_vehicles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(String(50), unique=True, nullable=False)
    vehicle_type = Column(String(50))
    license_plate = Column(String(50))
    current_location = Column(Geography(geometry_type='POINT', srid=4326))
    destination = Column(Geography(geometry_type='POINT', srid=4326))
    status = Column(String(20), default='inactive')
    priority = Column(Integer, default=1)
    green_wave_active = Column(Boolean, default=False)
    route = Column(Geography(geometry_type='LINESTRING', srid=4326))
    cameras_tracking = Column(ARRAY(UUID(as_uuid=True)))
    speed_kmh = Column(Float)
    eta_seconds = Column(Integer)
    activated_at = Column(DateTime)
    deactivated_at = Column(DateTime)
    additional_metadata = Column("metadata", JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AIDecision(Base):
    __tablename__ = "ai_decisions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    decision_type = Column(String(50), nullable=False)
    decision_value = Column(JSON, nullable=False)
    explanation = Column(Text, nullable=False)
    reasoning = Column(JSON)
    confidence_score = Column(Float)
    input_data = Column(JSON)
    related_cameras = Column(ARRAY(UUID(as_uuid=True)))
    related_events = Column(ARRAY(UUID(as_uuid=True)))
    affected_entities = Column(JSON)
    model_version = Column(String(50))
    processing_time_ms = Column(Integer)
    applied = Column(Boolean, default=False)
    override_reason = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class ManualOverride(Base):
    __tablename__ = "manual_overrides"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    override_type = Column(String(50), nullable=False)
    entity_id = Column(UUID(as_uuid=True))
    entity_type = Column(String(50))
    previous_value = Column(JSON)
    new_value = Column(JSON)
    reason = Column(Text, nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    simulation_run = Column(Boolean, default=False)
    simulation_result = Column(JSON)
    approved = Column(Boolean, default=False)
    applied = Column(Boolean, default=False)
    duration_minutes = Column(Integer)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    applied_at = Column(DateTime)
    reverted_at = Column(DateTime)

class Simulation(Base):
    __tablename__ = "simulations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    simulation_type = Column(String(50))
    scenario_description = Column(Text)
    input_state = Column(JSON, nullable=False)
    proposed_changes = Column(JSON, nullable=False)
    simulation_duration = Column(Integer, default=5)
    results = Column(JSON)
    predicted_metrics = Column(JSON)
    warnings = Column(JSON)
    recommendation = Column(String(20))
    execution_time_ms = Column(Integer)
    created_by = Column(UUID(as_uuid=True))
    related_override_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), default='officer')
    department = Column(String(100))
    badge_number = Column(String(50))
    phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    permissions = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
