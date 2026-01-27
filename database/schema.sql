-- D.R.I.V.E Database Schema
-- PostgreSQL 15+ with PostGIS extension for spatial data

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- Cameras Table
CREATE TABLE cameras (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    camera_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    region VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'maintenance')),
    resolution_width INTEGER DEFAULT 1920,
    resolution_height INTEGER DEFAULT 1080,
    fps INTEGER DEFAULT 30,
    direction FLOAT, -- Camera facing direction in degrees
    coverage_radius INTEGER DEFAULT 100, -- meters
    metadata JSONB DEFAULT '{}',
    installed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_active TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_cameras_location ON cameras USING GIST(location);
CREATE INDEX idx_cameras_status ON cameras(status);
CREATE INDEX idx_cameras_region ON cameras(region);

-- Traffic Lights Table
CREATE TABLE traffic_lights (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    light_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255),
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    junction_id VARCHAR(50),
    current_state VARCHAR(20) DEFAULT 'red' CHECK (current_state IN ('red', 'yellow', 'green', 'flashing_red', 'flashing_yellow')),
    control_mode VARCHAR(20) DEFAULT 'auto' CHECK (control_mode IN ('auto', 'manual', 'emergency')),
    cycle_time INTEGER DEFAULT 120, -- seconds
    green_duration INTEGER DEFAULT 45,
    yellow_duration INTEGER DEFAULT 5,
    red_duration INTEGER DEFAULT 70,
    cameras UUID[], -- Array of camera IDs monitoring this light
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_traffic_lights_location ON traffic_lights USING GIST(location);
CREATE INDEX idx_traffic_lights_junction ON traffic_lights(junction_id);
CREATE INDEX idx_traffic_lights_state ON traffic_lights(current_state);

-- Digital Sign Boards Table
CREATE TABLE sign_boards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sign_id VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255),
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    sign_type VARCHAR(50) DEFAULT 'speed_limit' CHECK (sign_type IN ('speed_limit', 'warning', 'informational')),
    current_display VARCHAR(255),
    default_value VARCHAR(50),
    road_segment VARCHAR(100),
    direction VARCHAR(20) CHECK (direction IN ('north', 'south', 'east', 'west', 'both')),
    cameras UUID[], -- Cameras influencing this sign
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'error')),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_sign_boards_location ON sign_boards USING GIST(location);
CREATE INDEX idx_sign_boards_road ON sign_boards(road_segment);

-- Speed Limits History Table
CREATE TABLE speed_limits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sign_board_id UUID REFERENCES sign_boards(id) ON DELETE CASCADE,
    speed_limit INTEGER NOT NULL,
    previous_limit INTEGER,
    reason VARCHAR(255),
    confidence_score FLOAT,
    set_by VARCHAR(50) DEFAULT 'ai' CHECK (set_by IN ('ai', 'manual', 'scheduled')),
    ai_decision_id UUID, -- Reference to AI decision explanation
    valid_from TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    valid_until TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_speed_limits_sign ON speed_limits(sign_board_id);
CREATE INDEX idx_speed_limits_time ON speed_limits(valid_from, valid_until);

-- Traffic Events Table
CREATE TABLE traffic_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_type VARCHAR(50) NOT NULL CHECK (event_type IN (
        'accident', 'congestion', 'debris', 'road_work', 
        'weather_hazard', 'vehicle_breakdown', 'pedestrian_incident',
        'emergency_vehicle', 'suspect_vehicle', 'other'
    )),
    severity VARCHAR(20) DEFAULT 'medium' CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    road_segment VARCHAR(100),
    description TEXT,
    detected_by UUID REFERENCES cameras(id),
    detection_method VARCHAR(50) DEFAULT 'ai' CHECK (detection_method IN ('ai', 'manual', 'sensor', 'report')),
    confidence_score FLOAT,
    video_url TEXT,
    image_urls TEXT[],
    affected_radius INTEGER DEFAULT 500, -- meters
    vehicles_involved INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'acknowledged', 'resolved', 'false_positive')),
    metadata JSONB DEFAULT '{}',
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_traffic_events_location ON traffic_events USING GIST(location);
CREATE INDEX idx_traffic_events_type ON traffic_events(event_type);
CREATE INDEX idx_traffic_events_status ON traffic_events(status);
CREATE INDEX idx_traffic_events_time ON traffic_events(detected_at);

-- Emergency Vehicles Table
CREATE TABLE emergency_vehicles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vehicle_id VARCHAR(50) UNIQUE NOT NULL,
    vehicle_type VARCHAR(50) CHECK (vehicle_type IN ('ambulance', 'fire_truck', 'police', 'rescue')),
    license_plate VARCHAR(50),
    current_location GEOGRAPHY(POINT, 4326),
    destination GEOGRAPHY(POINT, 4326),
    status VARCHAR(20) DEFAULT 'inactive' CHECK (status IN ('inactive', 'active', 'en_route', 'on_scene', 'returning')),
    priority INTEGER DEFAULT 1 CHECK (priority BETWEEN 1 AND 5),
    green_wave_active BOOLEAN DEFAULT FALSE,
    route GEOGRAPHY(LINESTRING, 4326),
    cameras_tracking UUID[], -- Cameras currently tracking this vehicle
    speed_kmh FLOAT,
    eta_seconds INTEGER,
    activated_at TIMESTAMP WITH TIME ZONE,
    deactivated_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_emergency_vehicles_location ON emergency_vehicles USING GIST(current_location);
CREATE INDEX idx_emergency_vehicles_status ON emergency_vehicles(status);
CREATE INDEX idx_emergency_vehicles_active ON emergency_vehicles(green_wave_active) WHERE green_wave_active = TRUE;

-- Vehicle Tracking Table (Multi-camera collaborative tracking)
CREATE TABLE vehicle_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tracking_session_id UUID NOT NULL,
    vehicle_type VARCHAR(50),
    license_plate VARCHAR(50),
    is_emergency BOOLEAN DEFAULT FALSE,
    is_suspect BOOLEAN DEFAULT FALSE,
    camera_id UUID REFERENCES cameras(id),
    location GEOGRAPHY(POINT, 4326) NOT NULL,
    direction FLOAT, -- Direction of movement in degrees
    speed_kmh FLOAT,
    confidence_score FLOAT,
    image_url TEXT,
    tracking_path GEOGRAPHY(LINESTRING, 4326),
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_vehicle_tracking_session ON vehicle_tracking(tracking_session_id);
CREATE INDEX idx_vehicle_tracking_camera ON vehicle_tracking(camera_id);
CREATE INDEX idx_vehicle_tracking_emergency ON vehicle_tracking(is_emergency) WHERE is_emergency = TRUE;
CREATE INDEX idx_vehicle_tracking_time ON vehicle_tracking(last_seen);

-- AI Decisions Table (XAI - Explainable AI)
CREATE TABLE ai_decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    decision_type VARCHAR(50) NOT NULL CHECK (decision_type IN (
        'speed_limit_change', 'traffic_light_control', 
        'green_wave_activation', 'event_detection', 'route_optimization'
    )),
    decision_value JSONB NOT NULL, -- The actual decision made
    explanation TEXT NOT NULL, -- Human-readable explanation
    reasoning JSONB, -- Detailed reasoning breakdown
    confidence_score FLOAT,
    input_data JSONB, -- Data used for decision
    related_cameras UUID[],
    related_events UUID[],
    affected_entities JSONB, -- sign_boards, traffic_lights affected
    model_version VARCHAR(50),
    processing_time_ms INTEGER,
    applied BOOLEAN DEFAULT FALSE,
    override_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_ai_decisions_type ON ai_decisions(decision_type);
CREATE INDEX idx_ai_decisions_time ON ai_decisions(created_at);
CREATE INDEX idx_ai_decisions_applied ON ai_decisions(applied);

-- Manual Overrides Table
CREATE TABLE manual_overrides (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    override_type VARCHAR(50) NOT NULL CHECK (override_type IN (
        'speed_limit', 'traffic_light', 'sign_board', 'emergency_protocol', 'system_disable'
    )),
    entity_id UUID, -- ID of the entity being overridden
    entity_type VARCHAR(50),
    previous_value JSONB,
    new_value JSONB,
    reason TEXT NOT NULL,
    user_id UUID NOT NULL, -- Reference to users table
    simulation_run BOOLEAN DEFAULT FALSE,
    simulation_result JSONB, -- Digital Twin simulation result
    approved BOOLEAN DEFAULT FALSE,
    applied BOOLEAN DEFAULT FALSE,
    duration_minutes INTEGER, -- How long override should last
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    applied_at TIMESTAMP WITH TIME ZONE,
    reverted_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_manual_overrides_entity ON manual_overrides(entity_id);
CREATE INDEX idx_manual_overrides_user ON manual_overrides(user_id);
CREATE INDEX idx_manual_overrides_time ON manual_overrides(created_at);
CREATE INDEX idx_manual_overrides_active ON manual_overrides(applied, expires_at);

-- Digital Twin Simulations Table
CREATE TABLE simulations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    simulation_type VARCHAR(50) CHECK (simulation_type IN ('manual_override', 'green_wave', 'traffic_optimization', 'scenario_test')),
    scenario_description TEXT,
    input_state JSONB NOT NULL, -- Current traffic state
    proposed_changes JSONB NOT NULL, -- Changes to simulate
    simulation_duration INTEGER DEFAULT 5, -- seconds
    results JSONB, -- Simulation outcomes
    predicted_metrics JSONB, -- traffic_flow, congestion_score, etc.
    warnings JSONB, -- Potential issues detected
    recommendation VARCHAR(20) CHECK (recommendation IN ('approve', 'reject', 'caution')),
    execution_time_ms INTEGER,
    created_by UUID, -- user_id if manual trigger
    related_override_id UUID REFERENCES manual_overrides(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_simulations_type ON simulations(simulation_type);
CREATE INDEX idx_simulations_override ON simulations(related_override_id);
CREATE INDEX idx_simulations_time ON simulations(created_at);

-- Users Table (Traffic authorities)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'officer' CHECK (role IN ('admin', 'supervisor', 'officer', 'viewer')),
    department VARCHAR(100),
    badge_number VARCHAR(50),
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP WITH TIME ZONE,
    permissions JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- Audit Log Table
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id UUID,
    changes JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_time ON audit_logs(created_at);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);

-- Traffic Metrics Table (for analytics)
CREATE TABLE traffic_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    camera_id UUID REFERENCES cameras(id),
    road_segment VARCHAR(100),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    vehicle_count INTEGER DEFAULT 0,
    average_speed FLOAT,
    congestion_level FLOAT CHECK (congestion_level BETWEEN 0 AND 1),
    density FLOAT, -- vehicles per km
    flow_rate INTEGER, -- vehicles per hour
    incidents INTEGER DEFAULT 0,
    weather_condition VARCHAR(50),
    visibility_meters INTEGER,
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_traffic_metrics_camera ON traffic_metrics(camera_id);
CREATE INDEX idx_traffic_metrics_time ON traffic_metrics(timestamp);
CREATE INDEX idx_traffic_metrics_road ON traffic_metrics(road_segment);

-- System Settings Table
CREATE TABLE system_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key VARCHAR(100) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    description TEXT,
    category VARCHAR(50),
    updated_by UUID REFERENCES users(id),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default settings
INSERT INTO system_settings (key, value, description, category) VALUES
('min_speed_limit', '20', 'Minimum allowed speed limit (km/h)', 'traffic'),
('max_speed_limit', '120', 'Maximum allowed speed limit (km/h)', 'traffic'),
('default_speed_limit', '60', 'Default speed limit (km/h)', 'traffic'),
('speed_adjustment_interval', '30', 'Seconds between speed limit recalculations', 'ai'),
('green_wave_advance_time', '45', 'Seconds ahead to clear for emergency vehicles', 'emergency'),
('emergency_speed_boost', '20', 'Additional speed allowance for emergency routes (km/h)', 'emergency'),
('ai_confidence_threshold', '0.7', 'Minimum confidence for AI decisions', 'ai'),
('simulation_duration', '5', 'Digital twin simulation duration (seconds)', 'simulation'),
('enable_auto_control', 'true', 'Enable automatic AI control', 'system'),
('enable_green_wave', 'true', 'Enable Green Wave protocol', 'emergency');

-- Triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_cameras_updated_at BEFORE UPDATE ON cameras
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_traffic_lights_updated_at BEFORE UPDATE ON traffic_lights
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sign_boards_updated_at BEFORE UPDATE ON sign_boards
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_traffic_events_updated_at BEFORE UPDATE ON traffic_events
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_emergency_vehicles_updated_at BEFORE UPDATE ON emergency_vehicles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to find nearby cameras
CREATE OR REPLACE FUNCTION find_nearby_cameras(
    lat FLOAT,
    lon FLOAT,
    radius_meters INTEGER DEFAULT 1000
)
RETURNS TABLE (
    camera_id UUID,
    camera_name VARCHAR,
    distance_meters FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.name,
        ST_Distance(c.location::geography, ST_SetSRID(ST_MakePoint(lon, lat), 4326)::geography) as distance
    FROM cameras c
    WHERE ST_DWithin(
        c.location::geography,
        ST_SetSRID(ST_MakePoint(lon, lat), 4326)::geography,
        radius_meters
    )
    AND c.status = 'active'
    ORDER BY distance;
END;
$$ LANGUAGE plpgsql;

-- Function to get current traffic status for a region
CREATE OR REPLACE FUNCTION get_region_traffic_status(region_name VARCHAR)
RETURNS TABLE (
    active_events INTEGER,
    avg_congestion FLOAT,
    active_emergency_vehicles INTEGER,
    cameras_online INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(DISTINCT te.id)::INTEGER as active_events,
        AVG(tm.congestion_level) as avg_congestion,
        COUNT(DISTINCT ev.id)::INTEGER as active_emergency_vehicles,
        COUNT(DISTINCT c.id)::INTEGER as cameras_online
    FROM cameras c
    LEFT JOIN traffic_events te ON te.detected_by = c.id AND te.status = 'active'
    LEFT JOIN traffic_metrics tm ON tm.camera_id = c.id 
        AND tm.timestamp > NOW() - INTERVAL '5 minutes'
    LEFT JOIN emergency_vehicles ev ON ev.status = 'active'
        AND ST_DWithin(ev.current_location::geography, c.location::geography, 5000)
    WHERE c.region = region_name AND c.status = 'active';
END;
$$ LANGUAGE plpgsql;

COMMENT ON DATABASE drive_db IS 'D.R.I.V.E - Dynamic Road Intelligence & Vehicle Environment Database';
