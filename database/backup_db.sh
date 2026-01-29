#!/bin/bash
# D.R.I.V.E Database Backup Script

set -e

# Load environment variables
if [ -f ../.env ]; then
    export $(cat ../.env | grep -v '^#' | xargs)
else
    export DB_HOST=${DB_HOST:-localhost}
    export DB_PORT=${DB_PORT:-5432}
    export DB_NAME=${DB_NAME:-drive_db}
    export DB_USER=${DB_USER:-postgres}
    export DB_PASSWORD=${DB_PASSWORD:-postgres}
fi

# Create backup directory
BACKUP_DIR="./backups"
mkdir -p $BACKUP_DIR

# Generate timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_backup_${TIMESTAMP}.sql"

echo "🔄 D.R.I.V.E Database Backup"
echo "============================"
echo "Database: $DB_NAME"
echo "Backup file: $BACKUP_FILE"
echo ""

# Perform backup
echo "📦 Creating backup..."
PGPASSWORD=$DB_PASSWORD pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -F p -f $BACKUP_FILE

# Compress backup
echo "🗜️  Compressing backup..."
gzip $BACKUP_FILE

echo "✅ Backup completed: ${BACKUP_FILE}.gz"
echo "📊 Backup size: $(du -h ${BACKUP_FILE}.gz | cut -f1)"

# Clean old backups (keep last 7 days)
echo ""
echo "🧹 Cleaning old backups (keeping last 7 days)..."
find $BACKUP_DIR -name "${DB_NAME}_backup_*.sql.gz" -mtime +7 -delete
echo "✅ Cleanup complete"

echo ""
echo "To restore this backup:"
echo "gunzip -c ${BACKUP_FILE}.gz | psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME"
