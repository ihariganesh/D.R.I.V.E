-- Migration: Add performance optimization indexes
-- Created: 2026-01-29
-- Description: Additional indexes for query optimization

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_traffic_events_status_time 
    ON traffic_events(status, detected_at DESC);

CREATE INDEX IF NOT EXISTS idx_ai_decisions_type_applied 
    ON ai_decisions(decision_type, applied);

CREATE INDEX IF NOT EXISTS idx_manual_overrides_user_time 
    ON manual_overrides(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_vehicle_tracking_session_time 
    ON vehicle_tracking(tracking_session_id, last_seen DESC);

-- Partial indexes for active records
CREATE INDEX IF NOT EXISTS idx_emergency_vehicles_active_status 
    ON emergency_vehicles(status) 
    WHERE status IN ('active', 'en_route');

CREATE INDEX IF NOT EXISTS idx_traffic_events_active 
    ON traffic_events(detected_at DESC) 
    WHERE status = 'active';

-- GIN index for JSONB columns (for fast JSON queries)
CREATE INDEX IF NOT EXISTS idx_ai_decisions_reasoning_gin 
    ON ai_decisions USING GIN(reasoning);

CREATE INDEX IF NOT EXISTS idx_simulations_results_gin 
    ON simulations USING GIN(results);

CREATE INDEX IF NOT EXISTS idx_traffic_metrics_metadata_gin 
    ON traffic_metrics USING GIN(metadata);

-- Index for array operations
CREATE INDEX IF NOT EXISTS idx_traffic_lights_cameras_gin 
    ON traffic_lights USING GIN(cameras);

CREATE INDEX IF NOT EXISTS idx_sign_boards_cameras_gin 
    ON sign_boards USING GIN(cameras);

COMMENT ON INDEX idx_traffic_events_status_time IS 'Optimizes event listing by status and time';
COMMENT ON INDEX idx_ai_decisions_type_applied IS 'Optimizes AI decision queries by type and application status';
