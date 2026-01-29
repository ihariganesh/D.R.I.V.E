#!/bin/bash
# D.R.I.V.E Database Restore Script

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

echo "🔄 D.R.I.V.E Database Restore"
echo "============================"
echo ""

# Check if backup file is provided
if [ -z "$1" ]; then
    echo "Available backups:"
    ls -lh ./backups/*.sql.gz 2>/dev/null || echo "No backups found"
    echo ""
    echo "Usage: $0 <backup_file.sql.gz>"
    exit 1
fi

BACKUP_FILE=$1

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "Database: $DB_NAME"
echo "Backup file: $BACKUP_FILE"
echo ""
echo "⚠️  WARNING: This will DROP and recreate the database!"
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Restore cancelled"
    exit 0
fi

# Drop existing database
echo ""
echo "🗑️  Dropping existing database..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "DROP DATABASE IF EXISTS $DB_NAME;"

# Create fresh database
echo "🏗️  Creating fresh database..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "CREATE DATABASE $DB_NAME;"

# Restore backup
echo "📥 Restoring backup..."
gunzip -c $BACKUP_FILE | PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME

echo ""
echo "✅ Database restored successfully!"
