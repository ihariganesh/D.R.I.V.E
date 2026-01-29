#!/bin/bash
# D.R.I.V.E Database Health Check Script

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

echo "🏥 D.R.I.V.E Database Health Check"
echo "=================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check PostgreSQL connection
echo -n "📡 PostgreSQL Connection... "
if PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
    exit 1
fi

# Check PostGIS extension
echo -n "🗺️  PostGIS Extension... "
POSTGIS_VERSION=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT PostGIS_Version();" 2>/dev/null | xargs)
if [ -n "$POSTGIS_VERSION" ]; then
    echo -e "${GREEN}✓ OK${NC} ($POSTGIS_VERSION)"
else
    echo -e "${RED}✗ MISSING${NC}"
fi

# Check table count
echo -n "📊 Tables... "
TABLE_COUNT=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" | xargs)
if [ "$TABLE_COUNT" -ge 14 ]; then
    echo -e "${GREEN}✓ OK${NC} ($TABLE_COUNT tables)"
else
    echo -e "${YELLOW}⚠ WARNING${NC} (Expected 14+, found $TABLE_COUNT)"
fi

# Check database size
echo -n "💾 Database Size... "
DB_SIZE=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));" | xargs)
echo -e "${GREEN}$DB_SIZE${NC}"

# Check active connections
echo -n "🔌 Active Connections... "
CONN_COUNT=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT count(*) FROM pg_stat_activity WHERE datname = '$DB_NAME';" | xargs)
echo -e "${GREEN}$CONN_COUNT${NC}"

# Check for long-running queries
echo -n "⏱️  Long-running Queries... "
LONG_QUERIES=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active' AND now() - query_start > interval '5 minutes';" | xargs)
if [ "$LONG_QUERIES" -eq 0 ]; then
    echo -e "${GREEN}✓ None${NC}"
else
    echo -e "${YELLOW}⚠ $LONG_QUERIES queries${NC}"
fi

# Check record counts
echo ""
echo "📈 Record Counts:"
echo "----------------"

TABLES=("cameras" "traffic_lights" "sign_boards" "traffic_events" "emergency_vehicles" "users" "ai_decisions" "manual_overrides")

for table in "${TABLES[@]}"; do
    COUNT=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM $table;" 2>/dev/null | xargs)
    if [ -n "$COUNT" ]; then
        printf "  %-20s %s\n" "$table:" "$COUNT"
    fi
done

# Check recent activity
echo ""
echo "🕐 Recent Activity:"
echo "------------------"

RECENT_EVENTS=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM traffic_events WHERE detected_at > NOW() - INTERVAL '1 hour';" 2>/dev/null | xargs)
echo "  Events (last hour): $RECENT_EVENTS"

RECENT_DECISIONS=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM ai_decisions WHERE created_at > NOW() - INTERVAL '1 hour';" 2>/dev/null | xargs)
echo "  AI Decisions (last hour): $RECENT_DECISIONS"

# Check indexes
echo ""
echo -n "🔍 Indexes... "
INDEX_COUNT=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public';" | xargs)
echo -e "${GREEN}$INDEX_COUNT${NC}"

# Check for missing indexes on foreign keys
echo -n "⚠️  Missing FK Indexes... "
MISSING_FK_INDEXES=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "
SELECT COUNT(*)
FROM pg_constraint c
LEFT JOIN pg_index i ON c.conrelid = i.indrelid AND c.conkey[1] = i.indkey[0]
WHERE c.contype = 'f' AND i.indexrelid IS NULL;
" | xargs)

if [ "$MISSING_FK_INDEXES" -eq 0 ]; then
    echo -e "${GREEN}✓ None${NC}"
else
    echo -e "${YELLOW}⚠ $MISSING_FK_INDEXES${NC}"
fi

# Performance stats
echo ""
echo "⚡ Performance:"
echo "--------------"

CACHE_HIT_RATIO=$(PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "
SELECT ROUND(100.0 * sum(blks_hit) / NULLIF(sum(blks_hit) + sum(blks_read), 0), 2)
FROM pg_stat_database WHERE datname = '$DB_NAME';
" | xargs)
echo "  Cache Hit Ratio: ${CACHE_HIT_RATIO}%"

if (( $(echo "$CACHE_HIT_RATIO < 90" | bc -l) )); then
    echo -e "  ${YELLOW}⚠ Consider increasing shared_buffers${NC}"
fi

echo ""
echo -e "${GREEN}✅ Health check complete!${NC}"
