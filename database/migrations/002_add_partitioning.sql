-- Migration: Add table partitioning for large tables
-- Created: 2026-01-29
-- Description: Partition traffic_metrics and audit_logs by time for better performance

-- Note: This migration requires PostgreSQL 10+
-- Run this only if you expect high data volume

-- Create partitioned traffic_metrics table
-- Uncomment and run when ready to migrate to partitioned tables

/*
-- Rename existing table
ALTER TABLE traffic_metrics RENAME TO traffic_metrics_old;

-- Create partitioned table
CREATE TABLE traffic_metrics (
    id UUID DEFAULT uuid_generate_v4(),
    camera_id UUID REFERENCES cameras(id),
    road_segment VARCHAR(100),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    vehicle_count INTEGER DEFAULT 0,
    average_speed FLOAT,
    congestion_level FLOAT CHECK (congestion_level BETWEEN 0 AND 1),
    density FLOAT,
    flow_rate INTEGER,
    incidents INTEGER DEFAULT 0,
    weather_condition VARCHAR(50),
    visibility_meters INTEGER,
    metadata JSONB DEFAULT '{}',
    PRIMARY KEY (id, timestamp)
) PARTITION BY RANGE (timestamp);

-- Create partitions for current and next months
CREATE TABLE traffic_metrics_2026_01 PARTITION OF traffic_metrics
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE TABLE traffic_metrics_2026_02 PARTITION OF traffic_metrics
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

-- Create indexes on partitioned table
CREATE INDEX idx_traffic_metrics_camera ON traffic_metrics(camera_id);
CREATE INDEX idx_traffic_metrics_time ON traffic_metrics(timestamp);
CREATE INDEX idx_traffic_metrics_road ON traffic_metrics(road_segment);

-- Migrate data
INSERT INTO traffic_metrics SELECT * FROM traffic_metrics_old;

-- Drop old table after verification
-- DROP TABLE traffic_metrics_old;
*/

-- Create function to automatically create new partitions
CREATE OR REPLACE FUNCTION create_monthly_partition(
    table_name TEXT,
    start_date DATE
)
RETURNS VOID AS $$
DECLARE
    partition_name TEXT;
    start_ts TEXT;
    end_ts TEXT;
BEGIN
    partition_name := table_name || '_' || TO_CHAR(start_date, 'YYYY_MM');
    start_ts := TO_CHAR(start_date, 'YYYY-MM-DD');
    end_ts := TO_CHAR(start_date + INTERVAL '1 month', 'YYYY-MM-DD');
    
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I PARTITION OF %I FOR VALUES FROM (%L) TO (%L)',
        partition_name, table_name, start_ts, end_ts
    );
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION create_monthly_partition IS 'Helper function to create monthly partitions';
