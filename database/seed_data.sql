-- Sample data for testing D.R.I.V.E system

-- Sample Cameras
INSERT INTO cameras (camera_id, name, location, region, direction, coverage_radius) VALUES
('CAM001', 'Main Street North', ST_SetSRID(ST_MakePoint(77.5946, 12.9716), 4326)::geography, 'Central', 0, 150),
('CAM002', 'Main Street South', ST_SetSRID(ST_MakePoint(77.5947, 12.9710), 4326)::geography, 'Central', 180, 150),
('CAM003', 'MG Road Junction', ST_SetSRID(ST_MakePoint(77.6050, 12.9750), 4326)::geography, 'East', 90, 200),
('CAM004', 'Brigade Road Entry', ST_SetSRID(ST_MakePoint(77.6088, 12.9726), 4326)::geography, 'East', 270, 180),
('CAM005', 'Airport Road Toll', ST_SetSRID(ST_MakePoint(77.6648, 13.0156), 4326)::geography, 'North', 45, 250);

-- Sample Traffic Lights
INSERT INTO traffic_lights (light_id, name, location, junction_id, current_state) VALUES
('TL001', 'Main Street Junction - North', ST_SetSRID(ST_MakePoint(77.5946, 12.9716), 4326)::geography, 'JCT001', 'green'),
('TL002', 'Main Street Junction - South', ST_SetSRID(ST_MakePoint(77.5947, 12.9710), 4326)::geography, 'JCT001', 'red'),
('TL003', 'MG Road Junction - East', ST_SetSRID(ST_MakePoint(77.6050, 12.9750), 4326)::geography, 'JCT002', 'yellow'),
('TL004', 'MG Road Junction - West', ST_SetSRID(ST_MakePoint(77.6048, 12.9750), 4326)::geography, 'JCT002', 'red');

-- Sample Sign Boards
INSERT INTO sign_boards (sign_id, name, location, sign_type, current_display, default_value, road_segment, direction) VALUES
('SB001', 'Main Street Speed Sign', ST_SetSRID(ST_MakePoint(77.5945, 12.9720), 4326)::geography, 'speed_limit', '60', '60', 'Main Street', 'north'),
('SB002', 'MG Road Speed Sign', ST_SetSRID(ST_MakePoint(77.6045, 12.9755), 4326)::geography, 'speed_limit', '50', '50', 'MG Road', 'east'),
('SB003', 'Airport Road Speed Sign', ST_SetSRID(ST_MakePoint(77.6640, 13.0160), 4326)::geography, 'speed_limit', '80', '80', 'Airport Road', 'north'),
('SB004', 'Brigade Road Warning', ST_SetSRID(ST_MakePoint(77.6085, 12.9730), 4326)::geography, 'warning', 'CONGESTION AHEAD', '', 'Brigade Road', 'both');

-- Sample Users (Traffic Authorities)
-- Password is 'password123' hashed with bcrypt
INSERT INTO users (username, email, password_hash, full_name, role, department, badge_number) VALUES
('admin', 'admin@traffic.gov', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5Hq8QvI1bKPBK', 'System Administrator', 'admin', 'IT Department', 'ADM001'),
('supervisor1', 'supervisor@traffic.gov', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5Hq8QvI1bKPBK', 'John Supervisor', 'supervisor', 'Traffic Control', 'SUP001'),
('officer1', 'officer1@traffic.gov', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5Hq8QvI1bKPBK', 'Jane Officer', 'officer', 'Traffic Control', 'OFF001'),
('officer2', 'officer2@traffic.gov', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5Hq8QvI1bKPBK', 'Bob Officer', 'officer', 'Emergency Response', 'OFF002');

-- Sample Emergency Vehicles
INSERT INTO emergency_vehicles (vehicle_id, vehicle_type, license_plate, current_location, status, priority) VALUES
('AMB001', 'ambulance', 'KA01AB1234', ST_SetSRID(ST_MakePoint(77.5950, 12.9720), 4326)::geography, 'inactive', 1),
('FIR001', 'fire_truck', 'KA01FT5678', ST_SetSRID(ST_MakePoint(77.6000, 12.9700), 4326)::geography, 'inactive', 1),
('POL001', 'police', 'KA01PL9012', ST_SetSRID(ST_MakePoint(77.6100, 12.9800), 4326)::geography, 'active', 2);

-- Sample Traffic Events
INSERT INTO traffic_events (event_type, severity, location, road_segment, description, detected_by, confidence_score, status) VALUES
('congestion', 'medium', ST_SetSRID(ST_MakePoint(77.6088, 12.9726), 4326)::geography, 'Brigade Road', 'Heavy traffic detected', (SELECT id FROM cameras WHERE camera_id = 'CAM004'), 0.89, 'active'),
('road_work', 'low', ST_SetSRID(ST_MakePoint(77.5946, 12.9716), 4326)::geography, 'Main Street', 'Road maintenance in progress', (SELECT id FROM cameras WHERE camera_id = 'CAM001'), 0.95, 'active');

-- Sample AI Decisions
INSERT INTO ai_decisions (decision_type, decision_value, explanation, confidence_score, applied) VALUES
('speed_limit_change', '{"sign_board_id": "SB001", "new_limit": 40, "old_limit": 60}'::jsonb, 'Speed reduced to 40 km/h due to road maintenance detected 500m ahead by Camera CAM001. High pedestrian activity observed.', 0.85, true),
('green_wave_activation', '{"route": ["TL001", "TL003"], "duration": 120}'::jsonb, 'Green Wave activated for ambulance AMB001. Clearing Main Street to MG Road route. ETA: 2 minutes.', 0.92, true);

-- Sample Traffic Metrics
INSERT INTO traffic_metrics (camera_id, road_segment, vehicle_count, average_speed, congestion_level, density, flow_rate) VALUES
((SELECT id FROM cameras WHERE camera_id = 'CAM001'), 'Main Street', 45, 52.3, 0.6, 35.5, 450),
((SELECT id FROM cameras WHERE camera_id = 'CAM002'), 'Main Street', 38, 55.1, 0.5, 28.2, 420),
((SELECT id FROM cameras WHERE camera_id = 'CAM003'), 'MG Road', 67, 35.8, 0.8, 52.3, 380),
((SELECT id FROM cameras WHERE camera_id = 'CAM004'), 'Brigade Road', 82, 28.5, 0.9, 68.7, 290);
