#!/bin/bash
# D.R.I.V.E Database Initialization Script

set -e

# Load environment variables
if [ -f ../.env ]; then
    export $(cat ../.env | grep -v '^#' | xargs)
else
    echo "Warning: .env file not found. Using default values."
    export DB_HOST=${DB_HOST:-localhost}
    export DB_PORT=${DB_PORT:-5432}
    export DB_NAME=${DB_NAME:-drive_db}
    export DB_USER=${DB_USER:-postgres}
    export DB_PASSWORD=${DB_PASSWORD:-postgres}
fi

echo "🚀 D.R.I.V.E Database Initialization"
echo "===================================="
echo "Host: $DB_HOST:$DB_PORT"
echo "Database: $DB_NAME"
echo "User: $DB_USER"
echo ""

# Check if PostgreSQL is running
echo "📡 Checking PostgreSQL connection..."
if ! PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -lqt | cut -d \| -f 1 | grep -qw postgres; then
    echo "❌ Error: Cannot connect to PostgreSQL server"
    echo "Please ensure PostgreSQL is running and credentials are correct"
    exit 1
fi
echo "✅ PostgreSQL is running"

# Check if database exists
echo ""
echo "🔍 Checking if database exists..."
if PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
    echo "⚠️  Database '$DB_NAME' already exists"
    read -p "Do you want to drop and recreate it? (yes/no): " confirm
    if [ "$confirm" = "yes" ]; then
        echo "🗑️  Dropping existing database..."
        PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "DROP DATABASE $DB_NAME;"
        echo "✅ Database dropped"
    else
        echo "ℹ️  Skipping database creation"
        exit 0
    fi
fi

# Create database
echo ""
echo "🏗️  Creating database '$DB_NAME'..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -c "CREATE DATABASE $DB_NAME;"
echo "✅ Database created"

# Run schema
echo ""
echo "📋 Running schema.sql..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f schema.sql
echo "✅ Schema created successfully"

# Run seed data
echo ""
read -p "Do you want to load seed data? (yes/no): " load_seed
if [ "$load_seed" = "yes" ]; then
    echo "🌱 Loading seed data..."
    PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f seed_data.sql
    echo "✅ Seed data loaded"
fi

# Verify installation
echo ""
echo "🔍 Verifying installation..."
TABLE_COUNT=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
echo "✅ Created $TABLE_COUNT tables"

echo ""
echo "🎉 Database initialization complete!"
echo ""
echo "Connection string:"
echo "postgresql://$DB_USER:****@$DB_HOST:$DB_PORT/$DB_NAME"
echo ""
echo "To connect:"
echo "psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME"
