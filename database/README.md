# D.R.I.V.E Database

Complete database setup and management for the D.R.I.V.E traffic management system.

## 📁 Files

- **schema.sql** - Complete database schema with all tables, indexes, and functions
- **seed_data.sql** - Sample data for development and testing
- **init_db.sh** - Database initialization script
- **backup_db.sh** - Automated backup script
- **restore_db.sh** - Database restore script
- **migrations/** - Database migration scripts

## 🚀 Quick Start

### Prerequisites

- PostgreSQL 15+ with PostGIS extension
- Bash shell (Linux/macOS) or WSL (Windows)

### 1. Setup Environment

Copy the example environment file and configure your database credentials:

```bash
cp ../.env.example ../.env
# Edit .env with your database credentials
```

### 2. Initialize Database

Run the initialization script:

```bash
cd database
chmod +x init_db.sh backup_db.sh restore_db.sh
./init_db.sh
```

This will:
- Create the database
- Install required extensions (uuid-ossp, postgis)
- Create all tables and indexes
- Set up triggers and functions
- Optionally load seed data

### 3. Verify Installation

Connect to the database:

```bash
psql -h localhost -p 5432 -U postgres -d drive_db
```

Check tables:

```sql
\dt
```

## 📊 Database Schema

### Core Tables

#### Infrastructure
- **cameras** - Camera network metadata and locations
- **traffic_lights** - Traffic light states and control
- **sign_boards** - Digital sign boards and displays

#### Events & Tracking
- **traffic_events** - Detected incidents and events
- **emergency_vehicles** - Emergency vehicle tracking
- **vehicle_tracking** - Multi-camera vehicle tracking

#### AI & Control
- **ai_decisions** - AI decision logs with explanations (XAI)
- **manual_overrides** - Authority intervention logs
- **simulations** - Digital Twin simulation results

#### System
- **users** - Traffic authority user accounts
- **audit_logs** - System audit trail
- **traffic_metrics** - Traffic analytics data
- **system_settings** - System configuration

### Spatial Features

The database uses PostGIS for spatial operations:

- Geographic coordinates (latitude/longitude)
- Distance calculations
- Nearby camera queries
- Route tracking

## 🔧 Management Scripts

### Backup Database

Create a timestamped backup:

```bash
./backup_db.sh
```

Backups are stored in `./backups/` and automatically compressed. Old backups (>7 days) are automatically cleaned up.

### Restore Database

Restore from a backup file:

```bash
./restore_db.sh ./backups/drive_db_backup_20260129_120000.sql.gz
```

⚠️ **Warning**: This will drop and recreate the database!

## 🔄 Migrations

Database migrations are stored in `migrations/` directory:

1. **001_add_indexes.sql** - Performance optimization indexes
2. **002_add_partitioning.sql** - Table partitioning for high-volume deployments

To apply a migration:

```bash
psql -h localhost -U postgres -d drive_db -f migrations/001_add_indexes.sql
```

## 📈 Performance Optimization

### Indexes

The schema includes comprehensive indexes for:
- Spatial queries (GIST indexes)
- Time-based queries
- Status filters
- JSON queries (GIN indexes)
- Composite queries

### Partitioning (Optional)

For high-volume deployments, consider partitioning:
- `traffic_metrics` - by month
- `audit_logs` - by month
- `vehicle_tracking` - by month

See `migrations/002_add_partitioning.sql` for details.

### Maintenance

Regular maintenance tasks:

```sql
-- Vacuum and analyze
VACUUM ANALYZE;

-- Reindex
REINDEX DATABASE drive_db;

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## 🔍 Useful Queries

### Find nearby cameras

```sql
SELECT * FROM find_nearby_cameras(13.0827, 80.2707, 1000);
```

### Get region traffic status

```sql
SELECT * FROM get_region_traffic_status('Downtown');
```

### Active emergency vehicles

```sql
SELECT * FROM emergency_vehicles 
WHERE status = 'active' AND green_wave_active = TRUE;
```

### Recent AI decisions

```sql
SELECT 
    decision_type,
    explanation,
    confidence_score,
    created_at
FROM ai_decisions
ORDER BY created_at DESC
LIMIT 10;
```

## 🔐 Security

### User Roles

- **admin** - Full system control
- **supervisor** - Override approval, system settings
- **officer** - View data, acknowledge events
- **viewer** - Read-only access

### Best Practices

1. Use strong passwords
2. Enable SSL/TLS for connections
3. Restrict network access
4. Regular backups
5. Monitor audit logs
6. Keep PostgreSQL updated

## 🐛 Troubleshooting

### Connection Issues

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check port
sudo netstat -plnt | grep 5432
```

### Extension Issues

```sql
-- Check installed extensions
SELECT * FROM pg_extension;

-- Install PostGIS if missing
CREATE EXTENSION postgis;
```

### Permission Issues

```sql
-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE drive_db TO your_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_user;
```

## 📚 Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [PostGIS Documentation](https://postgis.net/documentation/)
- [D.R.I.V.E Architecture](../docs/ARCHITECTURE.md)

## 🤝 Contributing

When adding new tables or modifying schema:

1. Create a migration file in `migrations/`
2. Update this README
3. Test with seed data
4. Document any new functions or triggers
