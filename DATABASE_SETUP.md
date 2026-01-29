# D.R.I.V.E Database Setup Guide

Quick reference for setting up the D.R.I.V.E database.

## 🐳 Option 1: Docker (Recommended)

### Start Database Services

```bash
# Start PostgreSQL + Redis + pgAdmin
docker-compose -f docker-compose.db.yml up -d

# Check status
docker-compose -f docker-compose.db.yml ps

# View logs
docker-compose -f docker-compose.db.yml logs -f postgres
```

### Access Services

- **PostgreSQL**: `localhost:5432`
- **Redis**: `localhost:6379`
- **pgAdmin**: http://localhost:5050
  - Email: `admin@drive.local`
  - Password: `admin`

### Stop Services

```bash
docker-compose -f docker-compose.db.yml down

# To remove volumes (⚠️ deletes all data)
docker-compose -f docker-compose.db.yml down -v
```

## 💻 Option 2: Local Installation

### Install PostgreSQL with PostGIS

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql-15 postgresql-15-postgis-3
sudo systemctl start postgresql
```

**macOS (Homebrew):**
```bash
brew install postgresql@15 postgis
brew services start postgresql@15
```

**Arch Linux:**
```bash
sudo pacman -S postgresql postgis
sudo systemctl start postgresql
```

### Initialize Database

```bash
cd database
./init_db.sh
```

## 🔧 Configuration

Create `.env` file in project root:

```bash
cp .env.example .env
```

Edit database credentials:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=drive_db
DB_USER=postgres
DB_PASSWORD=your_secure_password
```

## ✅ Verify Installation

### Check Connection

```bash
psql -h localhost -p 5432 -U postgres -d drive_db -c "SELECT version();"
```

### Check PostGIS

```sql
SELECT PostGIS_Version();
```

### Check Tables

```sql
\dt
```

Expected output: 14 tables

## 📊 Sample Queries

### List all cameras

```sql
SELECT camera_id, name, region, status FROM cameras;
```

### Find cameras near a location

```sql
SELECT * FROM find_nearby_cameras(13.0827, 80.2707, 1000);
```

### Check active events

```sql
SELECT event_type, severity, description, detected_at 
FROM traffic_events 
WHERE status = 'active'
ORDER BY detected_at DESC;
```

## 🔄 Backup & Restore

### Create Backup

```bash
./database/backup_db.sh
```

### Restore Backup

```bash
./database/restore_db.sh ./database/backups/drive_db_backup_YYYYMMDD_HHMMSS.sql.gz
```

## 🐛 Troubleshooting

### PostgreSQL not starting

```bash
# Check status
sudo systemctl status postgresql

# Check logs
sudo journalctl -u postgresql -n 50
```

### Connection refused

```bash
# Check if PostgreSQL is listening
sudo netstat -plnt | grep 5432

# Edit pg_hba.conf to allow connections
sudo nano /etc/postgresql/15/main/pg_hba.conf
```

### PostGIS extension missing

```sql
-- Connect to database
psql -U postgres -d drive_db

-- Create extension
CREATE EXTENSION postgis;
```

## 📚 Next Steps

1. ✅ Database setup complete
2. 🔧 Configure backend connection in `backend/.env`
3. 🚀 Start backend server: `cd backend && uvicorn main:app --reload`
4. 🌐 Start frontend: `cd frontend && npm start`

## 🔗 Resources

- [Database Schema Documentation](./database/README.md)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [PostGIS Docs](https://postgis.net/documentation/)
